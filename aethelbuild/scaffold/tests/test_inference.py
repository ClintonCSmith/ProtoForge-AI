import pytest


@pytest.mark.asyncio
async def test_local_backend_echo() -> None:
    from src.inference.client import InferenceClient
    out = await InferenceClient().generate("hello")
    assert out.startswith("[local-echo:")
