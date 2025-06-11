import asyncio

from backend.file_service.app.core.vector_integration import get_file_vector_service


async def test():
    try:
        vs = await get_file_vector_service()
        print("Vector service initialized successfully")
        collections = await vs.list_collections()
        print(f"Collections: {collections}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
