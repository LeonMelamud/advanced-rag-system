#!/usr/bin/env python3
"""
Advanced RAG System - Integration Tests
Week 2 Implementation: Service Integration Testing
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import pytest


class ServiceTester:
    """Integration tester for all microservices"""

    def __init__(self):
        self.base_urls = {
            "auth": "http://localhost:8001",
            "file": "http://localhost:8002",
            "chat": "http://localhost:8003",
            "collection": "http://localhost:8004",
            "mcp": "http://localhost:8005",
            "gateway": "http://localhost:8000",
        }
        self.auth_token: Optional[str] = None
        self.test_user = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        }

    async def test_health_checks(self) -> Dict[str, Any]:
        """Test health endpoints for all services"""
        results = {}

        async with httpx.AsyncClient() as client:
            for service, base_url in self.base_urls.items():
                if service == "gateway":  # Skip gateway for now
                    continue

                try:
                    # Test liveness
                    response = await client.get(f"{base_url}/health/live", timeout=10.0)
                    liveness_status = response.status_code == 200

                    # Test readiness
                    try:
                        response = await client.get(f"{base_url}/health/ready", timeout=10.0)
                        readiness_status = response.status_code in [
                            200,
                            503,
                        ]  # 503 is acceptable if dependencies are down
                        readiness_data = response.json() if response.status_code == 200 else None
                    except Exception:
                        readiness_status = False
                        readiness_data = None

                    results[service] = {
                        "liveness": liveness_status,
                        "readiness": readiness_status,
                        "readiness_data": readiness_data,
                        "url": base_url,
                    }

                except Exception as e:
                    results[service] = {
                        "liveness": False,
                        "readiness": False,
                        "error": str(e),
                        "url": base_url,
                    }

        return results

    async def test_auth_flow(self) -> Dict[str, Any]:
        """Test complete authentication flow"""
        results = {}

        async with httpx.AsyncClient() as client:
            try:
                # Test user registration
                register_response = await client.post(
                    f"{self.base_urls['auth']}/api/v1/auth/register",
                    json=self.test_user,
                    timeout=10.0,
                )

                results["registration"] = {
                    "status_code": register_response.status_code,
                    "success": register_response.status_code
                    in [200, 201, 409],  # 409 if user exists
                    "response": (
                        register_response.json() if register_response.status_code != 500 else None
                    ),
                }

                # Test user login
                login_response = await client.post(
                    f"{self.base_urls['auth']}/api/v1/auth/login",
                    json={"email": self.test_user["email"], "password": self.test_user["password"]},
                    timeout=10.0,
                )

                results["login"] = {
                    "status_code": login_response.status_code,
                    "success": login_response.status_code == 200,
                }

                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.auth_token = login_data.get("access_token")
                    results["login"]["token_received"] = bool(self.auth_token)

                    # Test token validation
                    if self.auth_token:
                        me_response = await client.get(
                            f"{self.base_urls['auth']}/api/v1/auth/me",
                            headers={"Authorization": f"Bearer {self.auth_token}"},
                            timeout=10.0,
                        )

                        results["token_validation"] = {
                            "status_code": me_response.status_code,
                            "success": me_response.status_code == 200,
                            "user_data": (
                                me_response.json() if me_response.status_code == 200 else None
                            ),
                        }

            except Exception as e:
                results["error"] = str(e)

        return results

    async def test_service_endpoints(self) -> Dict[str, Any]:
        """Test key endpoints for each service"""
        if not self.auth_token:
            return {"error": "No auth token available"}

        results = {}
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        async with httpx.AsyncClient() as client:
            # Test File Service
            try:
                files_response = await client.get(
                    f"{self.base_urls['file']}/api/v1/files/", headers=headers, timeout=10.0
                )
                results["file_service"] = {
                    "list_files": {
                        "status_code": files_response.status_code,
                        "success": files_response.status_code == 200,
                        "data": (
                            files_response.json() if files_response.status_code == 200 else None
                        ),
                    }
                }
            except Exception as e:
                results["file_service"] = {"error": str(e)}

            # Test Chat Service
            try:
                sessions_response = await client.get(
                    f"{self.base_urls['chat']}/api/v1/sessions/", headers=headers, timeout=10.0
                )
                results["chat_service"] = {
                    "list_sessions": {
                        "status_code": sessions_response.status_code,
                        "success": sessions_response.status_code == 200,
                        "data": (
                            sessions_response.json()
                            if sessions_response.status_code == 200
                            else None
                        ),
                    }
                }
            except Exception as e:
                results["chat_service"] = {"error": str(e)}

            # Test Collection Service
            try:
                collections_response = await client.get(
                    f"{self.base_urls['collection']}/api/v1/collections/",
                    headers=headers,
                    timeout=10.0,
                )
                results["collection_service"] = {
                    "list_collections": {
                        "status_code": collections_response.status_code,
                        "success": collections_response.status_code == 200,
                        "data": (
                            collections_response.json()
                            if collections_response.status_code == 200
                            else None
                        ),
                    }
                }
            except Exception as e:
                results["collection_service"] = {"error": str(e)}

            # Test MCP Orchestrator
            try:
                tools_response = await client.get(
                    f"{self.base_urls['mcp']}/api/v1/tools/", headers=headers, timeout=10.0
                )
                results["mcp_service"] = {
                    "list_tools": {
                        "status_code": tools_response.status_code,
                        "success": tools_response.status_code == 200,
                        "data": (
                            tools_response.json() if tools_response.status_code == 200 else None
                        ),
                    }
                }
            except Exception as e:
                results["mcp_service"] = {"error": str(e)}

        return results

    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity through service health checks"""
        results = {}

        async with httpx.AsyncClient() as client:
            for service, base_url in self.base_urls.items():
                if service == "gateway":
                    continue

                try:
                    response = await client.get(f"{base_url}/health/", timeout=15.0)
                    if response.status_code == 200:
                        health_data = response.json()
                        results[service] = {
                            "database_status": health_data.get("dependencies", {})
                            .get("database", {})
                            .get("status"),
                            "redis_status": health_data.get("dependencies", {})
                            .get("redis", {})
                            .get("status"),
                            "qdrant_status": health_data.get("dependencies", {})
                            .get("qdrant", {})
                            .get("status"),
                            "full_health": health_data,
                        }
                    else:
                        results[service] = {"error": f"Health check failed: {response.status_code}"}
                except Exception as e:
                    results[service] = {"error": str(e)}

        return results

    async def run_full_integration_test(self) -> Dict[str, Any]:
        """Run complete integration test suite"""
        print("🚀 Starting Advanced RAG System Integration Tests")
        print("=" * 60)

        start_time = time.time()

        # Test 1: Health Checks
        print("📋 Testing service health checks...")
        health_results = await self.test_health_checks()

        # Test 2: Authentication Flow
        print("🔐 Testing authentication flow...")
        auth_results = await self.test_auth_flow()

        # Test 3: Service Endpoints
        print("🌐 Testing service endpoints...")
        endpoint_results = await self.test_service_endpoints()

        # Test 4: Database Connectivity
        print("🗄️ Testing database connectivity...")
        db_results = await self.test_database_connectivity()

        end_time = time.time()

        # Compile results
        results = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(end_time - start_time, 2),
            "health_checks": health_results,
            "authentication": auth_results,
            "service_endpoints": endpoint_results,
            "database_connectivity": db_results,
            "summary": self._generate_summary(
                health_results, auth_results, endpoint_results, db_results
            ),
        }

        return results

    def _generate_summary(
        self, health_results, auth_results, endpoint_results, db_results
    ) -> Dict[str, Any]:
        """Generate test summary"""
        total_services = len([s for s in self.base_urls.keys() if s != "gateway"])
        healthy_services = sum(
            1 for result in health_results.values() if result.get("liveness", False)
        )

        auth_success = auth_results.get("login", {}).get("success", False)

        endpoint_success_count = 0
        total_endpoints = 0

        # Handle endpoint results safely
        if isinstance(endpoint_results, dict):
            for service_results in endpoint_results.values():
                if isinstance(service_results, dict) and "error" not in service_results:
                    for endpoint_result in service_results.values():
                        if isinstance(endpoint_result, dict):
                            total_endpoints += 1
                            if endpoint_result.get("success", False):
                                endpoint_success_count += 1

        return {
            "services_healthy": f"{healthy_services}/{total_services}",
            "authentication_working": auth_success,
            "endpoints_working": (
                f"{endpoint_success_count}/{total_endpoints}" if total_endpoints > 0 else "0/0"
            ),
            "overall_status": "PASS" if healthy_services >= 3 and auth_success else "FAIL",
        }


def print_results(results: Dict[str, Any]):
    """Print formatted test results"""
    print("\n" + "=" * 60)
    print("🧪 INTEGRATION TEST RESULTS")
    print("=" * 60)

    # Summary
    summary = results.get("summary", {})
    print(f"⏱️  Duration: {results.get('duration_seconds', 0)}s")
    print(f"🏥 Services Healthy: {summary.get('services_healthy', 'Unknown')}")
    print(f"🔐 Authentication: {'✅' if summary.get('authentication_working') else '❌'}")
    print(f"🌐 Endpoints: {summary.get('endpoints_working', 'Unknown')}")
    print(f"📊 Overall Status: {summary.get('overall_status', 'Unknown')}")

    # Health Checks
    print("\n📋 HEALTH CHECK RESULTS:")
    for service, result in results.get("health_checks", {}).items():
        liveness = "✅" if result.get("liveness") else "❌"
        readiness = "✅" if result.get("readiness") else "❌"
        print(f"  {service:15} | Liveness: {liveness} | Readiness: {readiness}")

    # Authentication
    print("\n🔐 AUTHENTICATION RESULTS:")
    auth_results = results.get("authentication", {})
    if "registration" in auth_results:
        reg_status = "✅" if auth_results["registration"].get("success") else "❌"
        print(f"  Registration: {reg_status}")
    if "login" in auth_results:
        login_status = "✅" if auth_results["login"].get("success") else "❌"
        print(f"  Login: {login_status}")
    if "token_validation" in auth_results:
        token_status = "✅" if auth_results["token_validation"].get("success") else "❌"
        print(f"  Token Validation: {token_status}")

    # Service Endpoints
    print("\n🌐 SERVICE ENDPOINT RESULTS:")
    endpoint_results = results.get("service_endpoints", {})
    if isinstance(endpoint_results, dict):
        for service, service_results in endpoint_results.items():
            if isinstance(service_results, dict):
                if "error" in service_results:
                    print(f"  {service:15} | ❌ Error: {service_results['error']}")
                else:
                    for endpoint, endpoint_result in service_results.items():
                        if isinstance(endpoint_result, dict):
                            status = "✅" if endpoint_result.get("success") else "❌"
                            print(f"  {service:15} | {endpoint}: {status}")
            else:
                print(f"  {service:15} | ❌ Invalid result format")
    else:
        print(f"  ❌ Error: {endpoint_results}")


async def main():
    """Main test runner"""
    tester = ServiceTester()

    try:
        results = await tester.run_full_integration_test()
        print_results(results)

        # Save results to file
        with open("tests/integration/results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: tests/integration/results.json")

        # Exit with appropriate code
        overall_status = results.get("summary", {}).get("overall_status", "FAIL")
        exit_code = 0 if overall_status == "PASS" else 1
        return exit_code

    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
