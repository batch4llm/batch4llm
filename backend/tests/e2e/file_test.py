def test_file_workflow(authenticated_client):
    # Retrieve list of files
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200

    pdf_bytes = open("tests/fixtures/sample-1.pdf", "rb").read()

    # Upload a file
    r = authenticated_client.post(
        "/api/files/upload",
        json={"tags": ["test_tag"]},
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
