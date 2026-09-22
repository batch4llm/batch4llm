import time
import uuid


def _wait_for_status(client, batch_id, target_status, fail_statuses, timeout=60):
    for _ in range(timeout):
        time.sleep(1)
        r = client.get("/api/batches/")
        assert r.status_code == 200
        match = next(item for item in r.json() if item["id"] == batch_id)
        if match["status"] == target_status:
            return match
        if match["status"] in fail_statuses:
            raise RuntimeError(f"Batch entered unexpected status {match['status']}")
    raise RuntimeError("Timed out waiting for status")


def _create_prompt(client):
    name = str(uuid.uuid4())[:8]
    r = client.post(
        "/api/prompts/add", json={"name": name, "content": "delete test prompt"}
    )
    assert r.status_code == 200
    return r.json()["id"], name


def _create_endpoint(client):
    name = str(uuid.uuid4())[:8]
    r = client.post(
        "/api/endpoints/add",
        json={"name": name, "client": "test", "provider": "self_hosted"},
    )
    assert r.status_code == 200
    return r.json()["id"], name


def test_delete_blocked_while_batch_active_then_allowed_after_completion(
    authenticated_client, upload_file
):
    # Regression test for: a prompt/endpoint used by a batch could never be
    # deleted again, even long after that batch had finished, because the
    # delete guard blocked on *any* referencing batch instead of only
    # active ones. Also covers the batch's prompt_name/endpoint_name
    # snapshot, which is what lets the batch keep showing a name after the
    # underlying resource is gone.
    prompt_id, prompt_name = _create_prompt(authenticated_client)
    endpoint_id, endpoint_name = _create_endpoint(authenticated_client)

    batch_run_payload = {
        "prompt_id": prompt_id,
        "endpoint_id": endpoint_id,
        "files": [upload_file],
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
    batch = r.json()
    batch_id = batch["id"]

    # names are snapshotted onto the batch at creation time
    assert batch["prompt_name"] == prompt_name
    assert batch["endpoint_name"] == endpoint_name

    # batch is still active (QUEUED/RUNNING) at this point -> both resources
    # must be protected from deletion
    r = authenticated_client.delete(f"/api/prompts/delete/{prompt_id}")
    assert r.status_code == 409
    r = authenticated_client.delete(f"/api/endpoints/delete/{endpoint_id}")
    assert r.status_code == 409

    _wait_for_status(authenticated_client, batch_id, "COMPLETED", ["FAILED", "STOPPED"])

    # batch is finished now -> deletion must succeed
    r = authenticated_client.delete(f"/api/prompts/delete/{prompt_id}")
    assert r.status_code == 200
    r = authenticated_client.delete(f"/api/endpoints/delete/{endpoint_id}")
    assert r.status_code == 200

    # the batch keeps showing the snapshotted names even though the
    # underlying prompt/endpoint rows are gone (foreign keys are nulled)
    r = authenticated_client.get(f"/api/batches/{batch_id}")
    assert r.status_code == 200
    result = r.json()
    assert result["prompt_id"] is None
    assert result["endpoint_id"] is None
    assert result["prompt_name"] == prompt_name
    assert result["endpoint_name"] == endpoint_name

    # and they're really gone from the resource lists
    r = authenticated_client.get("/api/prompts/")
    assert prompt_id not in [item["id"] for item in r.json()]
    r = authenticated_client.get("/api/endpoints/")
    assert endpoint_id not in [item["id"] for item in r.json()]


def _upload_local_file(client, filename="delete_test.txt"):
    pdf_bytes = open("backend/tests/fixtures/sample-1.pdf", "rb").read()
    r = client.post(
        "/api/files/upload",
        json={"tags": ["delete_test_tag"]},
        files={"file": (filename, pdf_bytes)},
    )
    assert r.status_code == 200
    return r.json()["id"]


def test_file_delete_blocked_while_batch_active_then_allowed_after_completion(
    authenticated_client, create_prompt, create_endpoint
):
    # Regression test for: deleting a file that had ever been used by a
    # batch permanently failed with a 409 ("still referenced"), even long
    # after that batch had finished — and, in an earlier version of the
    # guard, the physical file was deleted from storage anyway despite the
    # 409, orphaning the DB row. This mirrors
    # test_delete_blocked_while_batch_active_then_allowed_after_completion
    # above but for files, and additionally checks that batch results/export
    # keep showing the original filename after the file row is gone (via the
    # BatchFile.name snapshot taken at batch-creation time).
    file_id = _upload_local_file(authenticated_client)

    batch_run_payload = {
        "prompt_id": create_prompt,
        "endpoint_id": create_endpoint,
        "files": [file_id],
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
    batch_id = r.json()["id"]

    # batch is still active (QUEUED/RUNNING) at this point -> file must be
    # protected from deletion, and nothing should touch its storage object
    r = authenticated_client.delete(f"/api/files/delete/{file_id}")
    assert r.status_code == 409

    r = authenticated_client.get(f"/api/files/{file_id}/url")
    assert r.status_code == 200

    _wait_for_status(authenticated_client, batch_id, "COMPLETED", ["FAILED", "STOPPED"])

    # batch is finished now -> deletion must succeed
    r = authenticated_client.delete(f"/api/files/delete/{file_id}")
    assert r.status_code == 204

    # it's really gone from the file list
    r = authenticated_client.get("/api/files/")
    assert file_id not in [item["id"] for item in r.json()]

    # the batch's file overview keeps showing the snapshotted filename even
    # though the underlying File row is gone (FK is nulled)
    r = authenticated_client.get(f"/api/batches/{batch_id}/files")
    assert r.status_code == 200
    overview = r.json()
    assert len(overview) == 1
    assert overview[0]["file_id"] is None
    assert overview[0]["name"] == "delete_test.txt"

    # export still works and still shows the original filename
    r = authenticated_client.get(
        "/api/export/batches",
        params={"mode": "long_format_csv", "batch_ids": [batch_id]},
    )
    assert r.status_code == 200
    assert "delete_test.txt" in r.text
