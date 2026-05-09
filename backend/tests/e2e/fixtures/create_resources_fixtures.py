import pytest
import uuid


@pytest.fixture(scope="session")
def upload_file(authenticated_client):
    pdf_bytes = open("tests/fixtures/sample-1.pdf", "rb").read()
    r = authenticated_client.post(
        "/api/files/upload",
        json={"tags": ["test_tag"]},
        files={"file": ("test.txt", pdf_bytes)},
    )
    assert r.status_code == 200
    file_id = r.json()["id"]
    return file_id


@pytest.fixture(scope="session")
def create_endpoint(authenticated_client):
    endpoint_name = str(uuid.uuid4())[:8]
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
    return result["id"]


@pytest.fixture(scope="session")
def create_prompt(authenticated_client):
    prompt_name = str(uuid.uuid4())[:8]
    r = authenticated_client.post(
        "/api/prompts/add",
        json={"name": prompt_name, "content": "this is a test"},
    )
    assert r.status_code == 200
    result = r.json()
    return result["id"]
