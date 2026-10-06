import httpx
import pytest
import respx

from sua_urna_2026 import tse_urls as u
from sua_urna_2026.tse_client import TseClient


@pytest.fixture
def aux_url() -> str:
    return u.section_aux_url("ap", "06050", "0002", "0069")


@respx.mock
async def test_fetch_section_downloads_aux_then_bu(aux_json: dict, bu_bytes: bytes, aux_url: str):
    h = aux_json["hashes"][0]["hash"]
    respx.get(aux_url).mock(return_value=httpx.Response(200, json=aux_json))
    respx.get(u.bu_url("ap", "06050", "0002", "0069", h, "o03220ap0605000020069-bu.dat")).mock(
        return_value=httpx.Response(200, content=bu_bytes)
    )
    async with TseClient(rate_per_second=1000) as client:
        result = await client.fetch_section("ap", "06050", "0002", "0069")
    assert result.status == "ok"
    assert result.votos["22"] == 67


@respx.mock
async def test_fetch_section_without_hash_is_marked_missing(aux_url: str):
    respx.get(aux_url).mock(
        return_value=httpx.Response(200, json={"st": "Não instalada", "hashes": []})
    )
    async with TseClient(rate_per_second=1000) as client:
        result = await client.fetch_section("ap", "06050", "0002", "0069")
    assert result.status == "sem_bu"


@respx.mock
async def test_fetch_section_404_is_marked_missing(aux_url: str):
    respx.get(aux_url).mock(return_value=httpx.Response(404))
    async with TseClient(rate_per_second=1000) as client:
        result = await client.fetch_section("ap", "06050", "0002", "0069")
    assert result.status == "sem_bu"


@respx.mock
async def test_get_json_retries_on_server_error(aux_url: str, aux_json: dict):
    route = respx.get(aux_url)
    route.side_effect = [httpx.Response(503), httpx.Response(200, json=aux_json)]
    async with TseClient(rate_per_second=1000, backoff_seconds=0.0) as client:
        data = await client.get_json(aux_url)
    assert data["st"] == "Totalizada"
    assert route.call_count == 2


@respx.mock
async def test_sends_browser_user_agent(aux_url: str, aux_json: dict):
    route = respx.get(aux_url).mock(return_value=httpx.Response(200, json=aux_json))
    async with TseClient(rate_per_second=1000) as client:
        await client.get_json(aux_url)
    assert "Mozilla" in route.calls[0].request.headers["user-agent"]


@respx.mock
async def test_persistent_server_error_marks_section_as_erro(aux_url: str):
    respx.get(aux_url).mock(return_value=httpx.Response(503))
    async with TseClient(rate_per_second=1000, retries=2, backoff_seconds=0.0) as client:
        result = await client.fetch_section("ap", "06050", "0002", "0069")
    assert result.status == "erro"
