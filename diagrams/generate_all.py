#!/usr/bin/env python3
"""
Master script to generate all architecture diagrams for Advanced RAG System
Usage: python diagrams/generate_all.py
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


def check_dependencies() -> bool:
    """Check if required dependencies are installed"""
    try:
        import diagrams

        print("✅ Diagrams library found")
        return True
    except ImportError:
        print("❌ Diagrams library not found. Install with: pip install diagrams")
        print("   Also ensure Graphviz is installed: brew install graphviz (macOS)")
        return False


def generate_diagram(script_path: Path) -> Tuple[bool, str]:
    """Generate a single diagram and return success status and message"""
    try:
        print(f"🔄 Generating: {script_path.name}")
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Generated: {script_path.name} ({elapsed:.1f}s)")
            return True, f"Success in {elapsed:.1f}s"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"❌ Failed: {script_path.name}")
            print(f"   Error: {error_msg}")
            return False, error_msg

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {script_path.name} (>60s)")
        return False, "Timeout after 60 seconds"
    except Exception as e:
        print(f"❌ Error: {script_path.name}")
        print(f"   Exception: {e}")
        return False, str(e)


def main():
    """Generate all diagrams with progress reporting"""
    print("🚀 Advanced RAG System - Architecture Diagrams Generator")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Get the diagrams directory
    diagrams_dir = Path(__file__).parent
    generated_dir = diagrams_dir / "generated"

    # Ensure generated directory exists
    generated_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {generated_dir}")
    print()

    # Define all diagram scripts in order of generation
    diagram_scripts = [
        # Architecture diagrams (foundational)
        (
            "Architecture",
            [
                diagrams_dir / "architecture" / "system_overview.py",
                diagrams_dir / "architecture" / "infrastructure.py",
            ],
        ),
        # Component diagrams (detailed views)
        (
            "Components",
            [
                diagrams_dir / "components" / "backend_components.py",
                diagrams_dir / "components" / "frontend_components.py",
            ],
        ),
        # Flow diagrams (process flows)
        (
            "Flows",
            [
                diagrams_dir / "flows" / "ai_processing_flow.py",
            ],
        ),
    ]

    # Track results
    total_diagrams = sum(len(scripts) for _, scripts in diagram_scripts)
    successful = 0
    failed = 0
    results = []

    start_time = time.time()

    # Generate diagrams by category
    for category, scripts in diagram_scripts:
        print(f"📊 {category} Diagrams")
        print("-" * 30)

        for script_path in scripts:
            if not script_path.exists():
                print(f"⚠️  Script not found: {script_path}")
                failed += 1
                results.append((script_path.name, False, "Script not found"))
                continue

            success, message = generate_diagram(script_path)
            results.append((script_path.name, success, message))

            if success:
                successful += 1
            else:
                failed += 1

        print()  # Empty line between categories

    # Summary
    total_time = time.time() - start_time
    print("📋 Generation Summary")
    print("=" * 60)
    print(f"Total diagrams: {total_diagrams}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time:.1f}s")
    print()

    # Detailed results
    if results:
        print("📝 Detailed Results:")
        for script_name, success, message in results:
            status = "✅" if success else "❌"
            print(f"  {status} {script_name:<30} {message}")

    print()

    # List generated files
    generated_files = list(generated_dir.glob("*.png"))
    if generated_files:
        print(f"📁 Generated files in {generated_dir}:")
        for file_path in sorted(generated_files):
            file_size = file_path.stat().st_size / 1024  # KB
            print(f"  📄 {file_path.name} ({file_size:.1f} KB)")
    else:
        print("⚠️  No diagram files were generated")

    print()

    # Final status
    if failed == 0:
        print("🎉 All diagrams generated successfully!")
        print("   You can now view them in the diagrams/generated/ directory")
        sys.exit(0)
    else:
        print(f"⚠️  {failed} diagram(s) failed to generate")
        print("   Check the error messages above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
