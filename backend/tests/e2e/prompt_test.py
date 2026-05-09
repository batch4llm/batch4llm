import uuid


def test_prompt_workflow(authenticated_client):
    # Retrieve prompts
    r = authenticated_client.get("/api/prompts/")
    assert r.status_code == 200

    prompt_name = str(uuid.uuid4())[:8]

    # Create a prompt
    r = authenticated_client.post(
        "/api/prompts/add",
        json={"name": prompt_name, "content": "this is a test"},
    )
    assert r.status_code == 200
    result = r.json()
    prompt_id = result["id"]

    # Verify the prompt is in the list
    r = authenticated_client.get("/api/prompts/")
    assert r.status_code == 200
    assert prompt_id in [item["id"] for item in r.json()]

    # Delete the prompt
    r = authenticated_client.delete(f"/api/prompts/delete/{prompt_id}")
    assert r.status_code == 200

    # Verify the prompt is not in the list
    r = authenticated_client.get("/api/prompts/")
    assert r.status_code == 200
    assert prompt_id not in [item["id"] for item in r.json()]
