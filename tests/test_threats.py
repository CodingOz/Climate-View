import pytest
from httpx import AsyncClient

THREAT_PAYLOAD = {
    "name": "Test Pipeline Project",
    "threat_type": "PIPELINE",
    "status": "PROPOSED",
    "country": "United Kingdom",
    "region": "North Sea",
    "description": "A test pipeline threat",
    "estimated_co2_impact_tonnes": 5000000.0,
    "land_area_affected_km2": 100.0,
    "latitude": 55.0,
    "longitude": -2.0,
    "source_url": "https://example.com"
}


@pytest.mark.asyncio
async def test_create_threat(client: AsyncClient, auth_headers: dict):
    response = await client.post("/threats/", json=THREAT_PAYLOAD, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Pipeline Project"
    assert data["threat_type"] == "PIPELINE"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_threat_unauthenticated(client: AsyncClient):
    response = await client.post("/threats/", json=THREAT_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_threats(client: AsyncClient):
    response = await client.get("/threats/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_threat_by_id(client: AsyncClient, auth_headers: dict):
    create = await client.post("/threats/", json={**THREAT_PAYLOAD, "name": "Unique Threat ABC"}, headers=auth_headers)
    threat_id = create.json()["id"]
    response = await client.get(f"/threats/{threat_id}")
    assert response.status_code == 200
    assert response.json()["id"] == threat_id


@pytest.mark.asyncio
async def test_get_threat_not_found(client: AsyncClient):
    response = await client.get("/threats/nonexistent-id-12345")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_threat(client: AsyncClient, auth_headers: dict):
    create = await client.post("/threats/", json={**THREAT_PAYLOAD, "name": "Threat To Update"}, headers=auth_headers)
    threat_id = create.json()["id"]
    updated = {**THREAT_PAYLOAD, "name": "Threat To Update", "status": "APPROVED"}
    response = await client.put(f"/threats/{threat_id}", json=updated, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_delete_threat(client: AsyncClient, auth_headers: dict):
    create = await client.post("/threats/", json={**THREAT_PAYLOAD, "name": "Threat To Delete"}, headers=auth_headers)
    threat_id = create.json()["id"]
    delete = await client.delete(f"/threats/{threat_id}", headers=auth_headers)
    assert delete.status_code == 204
    get = await client.get(f"/threats/{threat_id}")
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_delete_threat_unauthenticated(client: AsyncClient, auth_headers: dict):
    create = await client.post("/threats/", json={**THREAT_PAYLOAD, "name": "Protected Threat"}, headers=auth_headers)
    threat_id = create.json()["id"]
    response = await client.delete(f"/threats/{threat_id}")
    assert response.status_code == 401