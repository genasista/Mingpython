# app/clients/core.py
import os
import httpx
from typing import Any, Dict, Optional

API_KEY       = os.getenv("API_KEY", "ADD-X-API-KEY")
ADMIN_TOKEN   = os.getenv("ADMIN_TOKEN", "")
CORE_BASE_URL = os.getenv("CORE_BASE_URL", "http://localhost:3001")  # Backend runs on 3001
SANDBOX       = os.getenv("SANDBOX_MODE", "true").lower() == "true"

_DEFAULT_HEADERS: Dict[str, str] = {
    "X-API-KEY": API_KEY,  # Backend expects X-API-KEY (not X-Api-Key)
    "X-Data-Mode": "sandbox" if SANDBOX else "production",
    "Content-Type": "application/json",
}
if ADMIN_TOKEN:
    _DEFAULT_HEADERS["Authorization"] = f"Bearer {ADMIN_TOKEN}"

_client: Optional[httpx.AsyncClient] = None

def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=CORE_BASE_URL,
            headers=_DEFAULT_HEADERS,
            timeout=httpx.Timeout(30.0, connect=5.0, read=25.0),
        )
    return _client

async def aclose() -> None:
    """Stäng delad klient vid shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None

async def get(endpoint: str) -> httpx.Response:
    """GET request till Core API"""
    client = _get_client()
    try:
        r = await client.get(endpoint)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        body = e.response.text[:1000]
        raise RuntimeError(f"CORE {endpoint} failed: {e.response.status_code} {body}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"CORE not reachable at {CORE_BASE_URL}: {e}") from e

async def post(endpoint: str, json: dict = None) -> httpx.Response:
    """POST request till Core API"""
    client = _get_client()
    try:
        r = await client.post(endpoint, json=json)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        body = e.response.text[:1000]
        raise RuntimeError(f"CORE {endpoint} failed: {e.response.status_code} {body}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"CORE not reachable at {CORE_BASE_URL}: {e}") from e

async def put(endpoint: str, json: dict = None) -> httpx.Response:
    """PUT request till Core API"""
    client = _get_client()
    try:
        r = await client.put(endpoint, json=json)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        body = e.response.text[:1000]
        raise RuntimeError(f"CORE {endpoint} failed: {e.response.status_code} {body}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"CORE not reachable at {CORE_BASE_URL}: {e}") from e

async def delete(endpoint: str) -> httpx.Response:
    """DELETE request till Core API"""
    client = _get_client()
    try:
        r = await client.delete(endpoint)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        body = e.response.text[:1000]
        raise RuntimeError(f"CORE {endpoint} failed: {e.response.status_code} {body}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"CORE not reachable at {CORE_BASE_URL}: {e}") from e

async def patch(endpoint: str, json: dict = None) -> httpx.Response:
    """PATCH request till Core API"""
    client = _get_client()
    try:
        r = await client.patch(endpoint, json=json)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        body = e.response.text[:1000]
        raise RuntimeError(f"CORE {endpoint} failed: {e.response.status_code} {body}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"CORE not reachable at {CORE_BASE_URL}: {e}") from e

async def post_seed(payload: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
    client = _get_client()
    headers = {}
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id
    try:
        r = await client.post("/admin/seed", json=payload, headers=headers or None)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        # Ge enkel men nyttig felbild tillbaka, utan att spränga loggarna
        body = e.response.text[:1000]
        raise RuntimeError(f"CORE /admin/seed failed: {e.response.status_code} {body}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"CORE not reachable at {CORE_BASE_URL}: {e}") from e
