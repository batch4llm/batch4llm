import os
import subprocess
import time
import httpx
import pytest
from fixtures import upload_file, create_endpoint, create_prompt  # noqa: F401

BASE_URL = "http://localhost"
TEST_USERNAME = os.environ.get("TEST_USERNAME", "testuser")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "testpass")


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


def wait_for_worker(retries=30, delay=2):
    """Waits for the Celery worker to be online and accepting tasks."""
    for _ in range(retries):
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "compose.yaml",
                "-f",
                "compose.dev.yaml",
                "exec",
                "-T",
                "worker",
                "celery",
                "-A",
                "batch4llm.celery.worker",
                "inspect",
                "ping",
                "--timeout",
                "2",
            ],
            capture_output=True,
        )
        if result.returncode == 0:
            return
        time.sleep(delay)
    raise RuntimeError("Celery worker not ready")


@pytest.fixture(scope="session", autouse=True)
def ensure_backend_ready():
    wait_for_backend()


@pytest.fixture(scope="session", autouse=True)
def ensure_worker_ready(ensure_backend_ready):
    wait_for_worker()


@pytest.fixture(scope="session", autouse=True)
def setup_test_user(ensure_worker_ready):
    subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "compose.yaml",
            "-f",
            "compose.dev.yaml",
            "exec",
            "-T",
            "backend",
            "b4",
            "user",
            "create",
            TEST_USERNAME,
            TEST_PASSWORD,
        ],
        capture_output=True,
    )


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
def authenticated_client(client, setup_test_user):
    r = client.post(
        "/api/authentication/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert r.status_code == 200, "Login fehlgeschlagen — läuft der Stack?"
    return client
