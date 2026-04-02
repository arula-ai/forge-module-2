#!/usr/bin/env python3
"""Run this to verify your environment is correctly configured."""

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


async def verify():
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("MODEL_NAME", "qwen3.5:4b")

    print(f"Checking Ollama at {base_url}...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check Ollama is running
        try:
            resp = await client.get(f"{base_url}/api/tags")
            models = resp.json().get("models", [])
            model_names = [m["name"] for m in models]
            print(f"  Available models: {model_names}")
        except Exception as e:
            print(f"  ERROR: Cannot reach Ollama — {e}")
            print("  Make sure 'ollama serve' is running.")
            return False

        # Check our model is available
        if not any(model in name for name in model_names):
            print(f"  ERROR: Model '{model}' not found. Run: ollama pull {model}")
            return False

        # Test inference
        print(f"Testing inference with {model}...")
        resp = await client.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Respond with: VERIFIED"}],
                "stream": False,
                "options": {"temperature": 0.0},
            },
        )
        result = resp.json()
        content = result["message"]["content"]
        print(f"  Model response: {content}")

    print("\nAll checks passed. You're ready for the lab!")
    return True


if __name__ == "__main__":
    asyncio.run(verify())
