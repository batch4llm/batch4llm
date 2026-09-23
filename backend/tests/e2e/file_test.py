import uuid


def test_file_workflow(authenticated_client):
    # Retrieve list of files
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200

    pdf_bytes = open("backend/tests/fixtures/sample-1.pdf", "rb").read()

    # Upload a file
    r = authenticated_client.post(
        "/api/files/upload",
        data={"tags": ["test_tag"]},
        files={"file": ("test.txt", pdf_bytes)},
    )
    assert r.status_code == 200
    file_id = r.json()["id"]
    file_name = r.json()["name"]

    # Verify the file is in the list
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200
    assert file_id in [item["id"] for item in r.json()]
    assert file_name in [item["name"] for item in r.json()]

    # Delete the file
    r = authenticated_client.delete(f"/api/files/delete/{file_id}")
    assert r.status_code == 204

    # Verify the file is not in the list
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200
    assert file_id not in [item["id"] for item in r.json()]


def _upload(client, tags):
    pdf_bytes = open("backend/tests/fixtures/sample-1.pdf", "rb").read()
    r = client.post(
        "/api/files/upload",
        data={"tags": tags},
        files={"file": ("tagged.txt", pdf_bytes)},
    )
    assert r.status_code == 200
    return r.json()["id"]


def test_delete_files_by_tag(authenticated_client):
    tag = f"bulk_delete_test_tag_{uuid.uuid4().hex[:8]}"
    id_a = _upload(authenticated_client, [tag])
    id_b = _upload(authenticated_client, [tag, "other_tag"])
    id_c = _upload(authenticated_client, ["other_tag"])  # different tag, must survive

    r = authenticated_client.delete(f"/api/files/by-tag/{tag}")
    assert r.status_code == 200
    result = r.json()
    assert sorted(result["deleted"]) == sorted([id_a, id_b])
    assert result["skipped"] == []

    r = authenticated_client.get("/api/files/")
    remaining_ids = [item["id"] for item in r.json()]
    assert id_a not in remaining_ids
    assert id_b not in remaining_ids
    assert id_c in remaining_ids

    # cleanup
    authenticated_client.delete(f"/api/files/delete/{id_c}")


def test_delete_files_by_tag_skips_files_used_by_active_batch(
    authenticated_client, create_prompt, create_endpoint
):
    tag = f"bulk_delete_active_batch_tag_{uuid.uuid4().hex[:8]}"
    free_id = _upload(authenticated_client, [tag])
    used_id = _upload(authenticated_client, [tag])

    batch_run_payload = {
        "prompt_id": create_prompt,
        "endpoint_id": create_endpoint,
        "files": [used_id],
        "file_reader": "pymupdf_default",
        "model": "test_model_pro",
        "temperature": 1.0,
        "json_format": False,
        "batch_worker_settings": {
            "max_tasks_per_minute": 20,
            "allow_concurrency": False,
            "retries_per_failed_task": 3,
            "failure_threshold_percent": 0,
            "queue_batch": False,
        },
    }
    r = authenticated_client.post("/api/batches/start", json=batch_run_payload)
    assert r.status_code == 200

    # batch is still active -> used_id must be skipped, free_id still deleted
    r = authenticated_client.delete(f"/api/files/by-tag/{tag}")
    assert r.status_code == 200
    result = r.json()
    assert result["deleted"] == [free_id]
    assert result["skipped"] == [used_id]

    r = authenticated_client.get("/api/files/")
    remaining_ids = [item["id"] for item in r.json()]
    assert free_id not in remaining_ids
    assert used_id in remaining_ids
