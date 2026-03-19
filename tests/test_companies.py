import pytest
from httpx import AsyncClient

COMPANY_PAYLOAD = {
    "name": "Test Oil Corp",
    "sector": "OIL_GAS",
    "country_of_registration": "United Kingdom",
    "description": "A test oil company",
    "esg_score": 25.0,
    "annual_emissions_mtonnes": 10.0,
    "is_paris_signatory": False,
    "website": "https://example.com"
}


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient, auth_headers: dict):
    response = await client.post("/companies/", json=COMPANY_PAYLOAD, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Oil Corp"


@pytest.mark.asyncio
async def test_create_duplicate_company(client: AsyncClient, auth_headers: dict):
    await client.post("/companies/", json=COMPANY_PAYLOAD, headers=auth_headers)
    response = await client.post("/companies/", json=COMPANY_PAYLOAD, headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_companies(client: AsyncClient):
    response = await client.get("/companies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_company_not_found(client: AsyncClient):
    response = await client.get("/companies/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_company(client: AsyncClient, auth_headers: dict):
    create = await client.post("/companies/", json={**COMPANY_PAYLOAD, "name": "Company To Update"}, headers=auth_headers)
    company_id = create.json()["id"]
    updated = {**COMPANY_PAYLOAD, "name": "Company To Update", "esg_score": 50.0}
    response = await client.put(f"/companies/{company_id}", json=updated, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["esg_score"] == 50.0


@pytest.mark.asyncio
async def test_delete_company(client: AsyncClient, auth_headers: dict):
    create = await client.post("/companies/", json={**COMPANY_PAYLOAD, "name": "Company To Delete"}, headers=auth_headers)
    company_id = create.json()["id"]
    delete = await client.delete(f"/companies/{company_id}", headers=auth_headers)
    assert delete.status_code == 204