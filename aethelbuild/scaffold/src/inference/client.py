"""Thin async client for one of: local model, Triton gRPC, vLLM OpenAI API.
Selected via INFERENCE_BACKEND; local is the default dev backend."""
import os

import httpx


class InferenceClient:
    def __init__(self) -> None:
        self.backend = os.getenv("INFERENCE_BACKEND", "local")
        self.base_url = os.getenv("INFERENCE_BASE_URL", "http://localhost:8000")

    async def generate(self, prompt: str, max_tokens: int = 256) -> str:
        if self.backend == "local":
            return f"[local-echo:{prompt[:32]}…]"  # synthetic, no real inference
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{self.base_url}/v1/completions", json={
                "prompt": prompt, "max_tokens": max_tokens,
            })
            r.raise_for_status()
            return r.json()["choices"][0]["text"]
