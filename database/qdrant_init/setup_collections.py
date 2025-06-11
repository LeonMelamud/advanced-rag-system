#!/usr/bin/env python3
"""
Qdrant Vector Database Initialization Script
Sets up initial collections and configurations for the Advanced RAG System
"""

import asyncio
import logging
from typing import Any, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import CollectionStatus, Distance, VectorParams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qdrant configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6335  # Updated to use non-default port
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

# Default collection configurations
DEFAULT_COLLECTIONS = {
    "default_collection": {
        "vector_size": 768,  # text-embedding-004 dimension
        "distance": Distance.COSINE,
        "description": "Default collection for initial testing",
    },
    "test_collection": {
        "vector_size": 1536,  # text-embedding-3-small dimension
        "distance": Distance.COSINE,
        "description": "Test collection for development",
    },
}


class QdrantInitializer:
    """Handles Qdrant database initialization"""

    def __init__(self, url: str = QDRANT_URL):
        self.client = QdrantClient(url=url)

    async def wait_for_qdrant(self, max_retries: int = 30, delay: int = 2) -> bool:
        """Wait for Qdrant to be ready"""
        for attempt in range(max_retries):
            try:
                # Try to get collections to test connection
                collections = self.client.get_collections()
                logger.info(f"Qdrant is ready. Found {len(collections.collections)} collections")
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Qdrant not ready - {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)

        logger.error("Qdrant failed to become ready within timeout")
        return False

    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        try:
            collections = self.client.get_collections()
            return any(col.name == collection_name for col in collections.collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False

    def create_collection(self, name: str, config: Dict[str, Any]) -> bool:
        """Create a collection with the given configuration"""
        try:
            if self.collection_exists(name):
                logger.info(f"Collection '{name}' already exists, skipping creation")
                return True

            # Create vector configuration
            vectors_config = VectorParams(size=config["vector_size"], distance=config["distance"])

            # Create the collection
            self.client.create_collection(collection_name=name, vectors_config=vectors_config)

            logger.info(f"Successfully created collection '{name}' with config: {config}")
            return True

        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            return False

    def verify_collection(self, name: str) -> bool:
        """Verify that a collection is properly configured"""
        try:
            collection_info = self.client.get_collection(name)
            logger.info(f"Collection '{name}' info: {collection_info}")

            # Check if collection is ready
            if collection_info.status == CollectionStatus.GREEN:
                logger.info(f"Collection '{name}' is ready and healthy")
                return True
            else:
                logger.warning(f"Collection '{name}' status: {collection_info.status}")
                return False

        except Exception as e:
            logger.error(f"Error verifying collection '{name}': {e}")
            return False

    async def initialize_collections(self) -> bool:
        """Initialize all default collections"""
        logger.info("Starting Qdrant collections initialization...")

        # Wait for Qdrant to be ready
        if not await self.wait_for_qdrant():
            return False

        success = True

        # Create each default collection
        for collection_name, config in DEFAULT_COLLECTIONS.items():
            logger.info(f"Creating collection: {collection_name}")

            if not self.create_collection(collection_name, config):
                success = False
                continue

            # Verify the collection
            if not self.verify_collection(collection_name):
                success = False
                continue

            logger.info(f"Collection '{collection_name}' successfully initialized")

        if success:
            logger.info("All collections initialized successfully!")
        else:
            logger.error("Some collections failed to initialize")

        return success


async def main():
    """Main initialization function"""
    logger.info("Starting Qdrant initialization...")

    initializer = QdrantInitializer()
    success = await initializer.initialize_collections()

    if success:
        logger.info("Qdrant initialization completed successfully!")
        return 0
    else:
        logger.error("Qdrant initialization failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
