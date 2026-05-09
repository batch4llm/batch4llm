import time
import httpx
import pytest
import uuid
from fixtures import upload_file, create_endpoint, create_prompt  # noqa: F401

BASE_URL = "http://localhost"


def wait_for_backend(retries=30, delay=1):
    """Waits for the backend to be available at BASE_URL/health."""
    for _ in range(retries):
        try:
            r = httpx.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(delay)
    raise RuntimeError("Backend not ready")


@pytest.fixture(scope="session", autouse=True)
def ensure_backend_ready():
    """Session fixture that ensures the backend is running."""
    wait_for_backend()


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
def authenticated_client(client):
    """Registers and logs in a test user."""
    session_username = str(uuid.uuid4())[:8]
    r = client.post(
        "/api/authentication/register",
        json={"username": session_username, "password": "123456"},
    )
    assert r.status_code == 200

    r = client.post(
        "/api/authentication/login",
        json={"username": session_username, "password": "123456"},
    )
    assert r.status_code == 200
    return client
