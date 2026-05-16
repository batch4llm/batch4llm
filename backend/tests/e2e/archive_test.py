import uuid


def _ids(response):
    return [item["id"] for item in response.json()]


def test_prompt_archive_workflow(authenticated_client):
    name = str(uuid.uuid4())[:8]

    r = authenticated_client.post(
        "/api/prompts/add",
        json={"name": name, "content": "archive test prompt"},
    )
    assert r.status_code == 200
    prompt_id = r.json()["id"]

    # Active by default — appears in non-archived list, not in archived list
    r = authenticated_client.get("/api/prompts/?archived=false")
    assert r.status_code == 200
    assert prompt_id in _ids(r)

    r = authenticated_client.get("/api/prompts/?archived=true")
    assert r.status_code == 200
    assert prompt_id not in _ids(r)

    # Archive it
    r = authenticated_client.patch(f"/api/prompts/{prompt_id}/archive")
    assert r.status_code == 200
    assert r.json()["archived_at"] is not None

    # Now appears only in archived list
    r = authenticated_client.get("/api/prompts/?archived=true")
    assert r.status_code == 200
    assert prompt_id in _ids(r)

    r = authenticated_client.get("/api/prompts/?archived=false")
    assert r.status_code == 200
    assert prompt_id not in _ids(r)

    # Both (no filter) includes it
    r = authenticated_client.get("/api/prompts/")
    assert r.status_code == 200
    assert prompt_id in _ids(r)

    # Unarchive it
    r = authenticated_client.patch(f"/api/prompts/{prompt_id}/archive?archived=false")
    assert r.status_code == 200
    assert r.json()["archived_at"] is None

    # Active again
    r = authenticated_client.get("/api/prompts/?archived=false")
    assert r.status_code == 200
    assert prompt_id in _ids(r)

    r = authenticated_client.get("/api/prompts/?archived=true")
    assert r.status_code == 200
    assert prompt_id not in _ids(r)

    # Cleanup
    authenticated_client.delete(f"/api/prompts/delete/{prompt_id}")


def test_endpoint_archive_workflow(authenticated_client):
    name = str(uuid.uuid4())[:8]

    r = authenticated_client.post(
        "/api/endpoints/add",
        json={"name": name, "client": "test", "provider": "self_hosted"},
    )
    assert r.status_code == 200
    endpoint_id = r.json()["id"]

    # Active by default
    r = authenticated_client.get("/api/endpoints/?archived=false")
    assert r.status_code == 200
    assert endpoint_id in _ids(r)

    r = authenticated_client.get("/api/endpoints/?archived=true")
    assert r.status_code == 200
    assert endpoint_id not in _ids(r)

    # Archive it
    r = authenticated_client.patch(f"/api/endpoints/{endpoint_id}/archive")
    assert r.status_code == 200
    assert r.json()["archived_at"] is not None

    # Now only in archived list
    r = authenticated_client.get("/api/endpoints/?archived=true")
    assert r.status_code == 200
    assert endpoint_id in _ids(r)

    r = authenticated_client.get("/api/endpoints/?archived=false")
    assert r.status_code == 200
    assert endpoint_id not in _ids(r)

    # Both (no filter) includes it
    r = authenticated_client.get("/api/endpoints/")
    assert r.status_code == 200
    assert endpoint_id in _ids(r)

    # Unarchive it
    r = authenticated_client.patch(
        f"/api/endpoints/{endpoint_id}/archive?archived=false"
    )
    assert r.status_code == 200
    assert r.json()["archived_at"] is None

    # Active again
    r = authenticated_client.get("/api/endpoints/?archived=false")
    assert r.status_code == 200
    assert endpoint_id in _ids(r)

    r = authenticated_client.get("/api/endpoints/?archived=true")
    assert r.status_code == 200
    assert endpoint_id not in _ids(r)

    # Cleanup
    authenticated_client.delete(f"/api/endpoints/delete/{endpoint_id}")


def test_file_archive_workflow(authenticated_client):
    pdf_bytes = open("backend/tests/fixtures/sample-1.pdf", "rb").read()

    r = authenticated_client.post(
        "/api/files/upload",
        files={"file": ("archive_test.pdf", pdf_bytes)},
    )
    assert r.status_code == 200
    file_id = r.json()["id"]

    # Active by default
    r = authenticated_client.get("/api/files/?archived=false")
    assert r.status_code == 200
    assert file_id in _ids(r)

    r = authenticated_client.get("/api/files/?archived=true")
    assert r.status_code == 200
    assert file_id not in _ids(r)

    # Archive it
    r = authenticated_client.patch(f"/api/files/{file_id}/archive")
    assert r.status_code == 200
    assert r.json()["archived_at"] is not None

    # Now only in archived list
    r = authenticated_client.get("/api/files/?archived=true")
    assert r.status_code == 200
    assert file_id in _ids(r)

    r = authenticated_client.get("/api/files/?archived=false")
    assert r.status_code == 200
    assert file_id not in _ids(r)

    # Both (no filter) includes it
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200
    assert file_id in _ids(r)

    # Unarchive it
    r = authenticated_client.patch(f"/api/files/{file_id}/archive?archived=false")
    assert r.status_code == 200
    assert r.json()["archived_at"] is None

    # Active again
    r = authenticated_client.get("/api/files/?archived=false")
    assert r.status_code == 200
    assert file_id in _ids(r)

    r = authenticated_client.get("/api/files/?archived=true")
    assert r.status_code == 200
    assert file_id not in _ids(r)

    # Cleanup
    authenticated_client.delete(f"/api/files/delete/{file_id}")
