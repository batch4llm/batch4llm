import uuid


def test_endpoint_workflow(authenticated_client):
    # Retrieve endpoints
    r = authenticated_client.get("/api/endpoints/")
    assert r.status_code == 200

    endpoint_name = str(uuid.uuid4())[:8]

    # Create a endpoint
    r = authenticated_client.post(
        "/api/endpoints/add",
        json={
            "name": endpoint_name,
            "client": "test",
            "provider": "self_hosted",
        },
    )
    assert r.status_code == 200
    result = r.json()
    endpoint_id = result["id"]

    # Verify the endpoint is in the list
    r = authenticated_client.get("/api/endpoints/")
    assert r.status_code == 200
    assert endpoint_id in [item["id"] for item in r.json()]

    # Delete the endpoint
    r = authenticated_client.delete(f"/api/endpoints/delete/{endpoint_id}")
    assert r.status_code == 200

    # Verify the endpoint is not in the list
    r = authenticated_client.get("/api/endpoints/")
    assert r.status_code == 200
    assert endpoint_id not in [item["id"] for item in r.json()]
