import asyncio
import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client_session():
    client_session = aiohttp.ClientSession()
    yield client_session
    await client_session.close()
