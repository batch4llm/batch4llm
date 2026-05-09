import pytest
from unittest.mock import patch

from batch4llm.manager.file_manager import MediaFile
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.manager.llm_client.models.response_model import LLMClientResponse


class MockEngine:
    def __init__(self, api_token, base_url):
        self.api_token = api_token
        self.base_url = base_url

    def run(self, model, prompt, content, file, model_settings):
        return LLMClientResponse(
            model=model,
            prompt=prompt,
            temperature=model_settings.temperature,
            output=content,
            client="Test Engine",
            input=content or f"[Uploaded File: {file}]",
            input_tokens=0,
            output_tokens=0,
            top_k=None,
            top_p=None,
            max_output_tokens=None,
            seed=None,
            context_window=None,
            json_format=False,
        )


@pytest.fixture
def client_manager():
    cm = ClientManager()
    cm.client_map = {"mock": MockEngine}
    return cm


@patch(
    "batch4llm.manager.llm_client.client_manager.FileReaderManager.read",
    return_value="file content",
)
def test_process_with_file_content(mock_read, client_manager):
    endpoint = {
        "name": "test_endpoint",
        "client": "mock",
        "token": "abc123",
        "url": "http://example.com",
    }
    result = client_manager.process(
        endpoint=endpoint,
        file_reader="text",
        prompt="Test prompt",
        file=MediaFile("some bytes", "test.txt", "text/plain"),
        model="gpt-test",
        temperature=0.5,
        json_format=False,
    )

    mock_read.assert_called_once_with("text", "some bytes")
    assert result.output == "file content"
    assert result.model == "gpt-test"


def test_process_with_upload(client_manager):
    endpoint = {
        "name": "test_endpoint",
        "client": "mock",
        "token": "abc123",
        "url": "http://example.com",
    }
    result = client_manager.process(
        endpoint=endpoint,
        file_reader="upload",
        prompt="Another test",
        file="path/to/upload.txt",
        model="gpt-test",
        temperature=1.0,
        json_format=False,
    )

    assert result.input == "[Uploaded File: path/to/upload.txt]"
    assert result.prompt == "Another test"


def test_invalid_engine_raises(client_manager):
    endpoint = {
        "name": "test_endpoint",
        "client": "invalid",
        "token": "123",
        "url": "x",
    }
    with pytest.raises(ValueError) as e:
        client_manager.process(
            endpoint, "text", "prompt", "file.txt", "model", 0.2, False
        )
    assert "not supported" in str(e.value)


def test_get_engines(client_manager):
    engines = list(client_manager.get_engines())
    assert engines == ["mock"]
