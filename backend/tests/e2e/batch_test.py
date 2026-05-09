import time


def wait_for_status(
    authenticated_client,
    batch_id,
    status,
    raise_on_status=None,
    raise_after_seconds=120,
):
    for i in range(raise_after_seconds):
        time.sleep(1)
        r = authenticated_client.get("/api/batches/")
        assert r.status_code == 200
        items = r.json()
        match = next(item for item in items if item["id"] == batch_id)
        if match["status"] == status:
            return True
        elif match["status"] in raise_on_status:
            r = authenticated_client.get(f"/api/batches/log/{batch_id}")
            log = r.json()
            assert r.status_code == 200
            raise RuntimeError(
                "Raise on status {}, batch details {}, log {}".format(
                    match["status"], match, log
                )
            )
    raise RuntimeError("Timed out waiting for status")


def test_batch_workflow(
    authenticated_client, upload_file, create_endpoint, create_prompt
):

    # Start a batch
    batch_run_payload = {
        "prompt_id": create_prompt,
        "endpoint_id": create_endpoint,
        "files": [upload_file],
        "file_reader": "pymupdf_default",
        "model": "test_model_pro",
        "temperature": 1.0,
        "json_format": False,
        "batch_worker_settings": {
            "max_tasks_per_minute": 20,
            "max_parallel_tasks": 1,
            "retries_per_failed_task": 3,
            "max_retries": 0,  #! important for testing, set batch to failed as soon as one task fails
            "queue_batch": False,
        },
    }
    r = authenticated_client.post("/api/batches/start", json=batch_run_payload)
    assert r.status_code == 200
    batch_id = r.json()["id"]

    # Verify the batch is in the list
    r = authenticated_client.get("/api/batches/")
    assert r.status_code == 200
    items = r.json()
    match = next(item for item in items if item["id"] == batch_id)
    assert match["status"] == "QUEUED"

    assert wait_for_status(
        authenticated_client, batch_id, "COMPLETED", ["FAILED", "STOPPED"], 60
    )
