"""
IBM Granite LLM Client
Handles authentication and inference calls to IBM watsonx.ai

Model: ibm/granite-3-3-8b-instruct
  - Granite 3.3, 8B parameters
  - Available in Sydney (au-syd), Dallas, Toronto regions
  - Supports instruction-following, reasoning, summarisation, Q&A
  - Context window: 131,072 tokens
  - Replaces deprecated ibm/granite-13b-instruct-v2
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
IBM_API_KEY    = os.getenv("IBM_API_KEY", "bb6ugzpXAPzHw3iCH4lPe4Vf3gY5sm6r_1JqSYXcjOg8")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "48221ba9-412a-457a-9dfa-856de8ab423f")
IBM_ENDPOINT   = os.getenv("IBM_ENDPOINT", "https://au-syd.ml.cloud.ibm.com")

# ibm/granite-13b-instruct-v2 was removed — use Granite 3.3 8B Instruct (Sydney-available)
GRANITE_MODEL  = "ibm/granite-3-3-8b-instruct"

IAM_TOKEN_URL  = "https://iam.cloud.ibm.com/identity/token"

_cached_token: dict = {}


# ── Token management ──────────────────────────────────────────────────────────
def _get_iam_token() -> str:
    """Fetch (or return cached) IAM bearer token."""
    import time
    now = time.time()

    if _cached_token.get("token") and now < _cached_token.get("expires_at", 0) - 60:
        return _cached_token["token"]

    resp = requests.post(
        IAM_TOKEN_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": IBM_API_KEY,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    _cached_token["token"] = data["access_token"]
    _cached_token["expires_at"] = now + data.get("expires_in", 3600)
    return _cached_token["token"]


# ── Inference ─────────────────────────────────────────────────────────────────
def call_granite(prompt: str, max_tokens: int = 900, temperature: float = 0.7) -> str:
    """
    Send a prompt to IBM Granite via watsonx.ai REST API.
    Returns the generated text string.
    """
    token = _get_iam_token()

    url = f"{IBM_ENDPOINT}/ml/v1/text/generation?version=2024-03-19"

    payload = {
        "model_id": GRANITE_MODEL,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy" if temperature == 0 else "sample",
            "max_new_tokens": max_tokens,
            "min_new_tokens": 1,
            "temperature": temperature,
            "repetition_penalty": 1.05,
            "stop_sequences": ["<|user|>", "<|endoftext|>"],
        },
        "project_id": IBM_PROJECT_ID,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        return result["results"][0]["generated_text"].strip()
    except requests.exceptions.HTTPError as e:
        logger.error("Granite API HTTP error: %s – %s", e, resp.text)
        raise RuntimeError(f"IBM Granite API error: {resp.status_code} – {resp.text}") from e
    except Exception as e:
        logger.error("Granite call failed: %s", e)
        raise
