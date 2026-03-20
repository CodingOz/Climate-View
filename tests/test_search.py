import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_returns_results(client: AsyncClient, auth_headers: dict):
    # Seed a known threat to search for
    await client.post("/threats/", json={
        "name": "Searchable Pipeline Project",
        "threat_type": "PIPELINE",
        "status": "PROPOSED",
        "country": "United Kingdom",
        "region": "North Sea",
        "description": "A uniquely searchable pipeline description",
        "estimated_co2_impact_tonnes": 1000000.0,
        "latitude": 55.0,
        "longitude": -2.0,
        "source_url": "https://example.com"
    }, headers=auth_headers)

    response = await client.get("/search/?q=Searchable")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Searchable"
    assert data["total_results"] > 0
    assert any("Searchable" in t["name"] for t in data["threats"])


@pytest.mark.asyncio
async def test_search_too_short(client: AsyncClient):
    response = await client.get("/search/?q=a")
    assert response.status_code == 400
    assert "2 characters" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient):
    response = await client.get("/search/?q=xyznonexistentterm999")
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 0
    assert data["threats"] == []
    assert data["organisations"] == []
    assert data["campaigns"] == []


@pytest.mark.asyncio
async def test_search_response_structure(client: AsyncClient):
    response = await client.get("/search/?q=climate")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "threats" in data
    assert "organisations" in data
    assert "campaigns" in data


@pytest.mark.asyncio
async def test_search_missing_query(client: AsyncClient):
    response = await client.get("/search/")
    assert response.status_code == 422