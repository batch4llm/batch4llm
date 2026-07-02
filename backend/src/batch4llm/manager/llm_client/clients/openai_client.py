import json
from io import BytesIO
from typing import Optional

from batch4llm.manager.file_manager import MediaFile
from batch4llm.manager.llm_client.clients.base import BaseLLMClient
import tiktoken
import openai

from batch4llm.manager.llm_client.models.engine_health_model import EngineHealth
from batch4llm.manager.llm_client.models.exceptions import RateLimitError
from batch4llm.manager.llm_client.models.model_settings_model import ModelSettings
from batch4llm.manager.llm_client.models.response_model import (
    LLMClientResponse,
    ProviderBatchStatus,
    BatchResultEntry,
)


class OpenAILLMClient(BaseLLMClient):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        if base_url is None:
            self.client = openai.Client(api_key=api_token)
        else:
            self.client = openai.Client(api_key=api_token, base_url=base_url)
        self._batch_lines: list = []

    def models(self) -> list[str]:
        models = self.client.models.list()
        model_ids = [m.id for m in models.data]
        return model_ids

    def health(self) -> EngineHealth:
        try:
            self.models()
            return EngineHealth(True)
        except Exception as e:
            return EngineHealth(False, e.__str__())

    def token_count(self, model: str, text: str) -> int:
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[MediaFile] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> LLMClientResponse:
        if file is None and content is None:
            raise ValueError("Either file_path or content must be specified")

        text_format = (
            {"format": {"type": "json_object"}}
            if model_settings.json_format
            else {"format": {"type": "text"}}
        )
        response_format = (
            {"type": "json_object"} if model_settings.json_format else {"type": "text"}
        )
        try:
            if file:
                uploaded = self.client.files.create(
                    file=(file.name, file.data), purpose="user_data"
                )
                response = self.client.responses.create(  # type: ignore
                    model=model,
                    input=[
                        {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_file", "file_id": uploaded.id},
                            ],
                        }
                    ],
                    temperature=model_settings.temperature,
                    stream=False,
                    text=text_format,
                )
                result_text = response.output_text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
            else:
                response = self.client.chat.completions.create(  # type: ignore
                    model=model,
                    temperature=model_settings.temperature,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": content},
                    ],
                    stream=False,
                    response_format=response_format,
                )
                result_text = response.choices[0].message.content
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
        except openai.RateLimitError as e:
            raise RateLimitError(e)

        return LLMClientResponse(
            client=self.__class__.__name__,
            model=model,
            temperature=model_settings.temperature,
            json_format=model_settings.json_format,
            top_p=model_settings.top_p,
            top_k=None,
            max_output_tokens=None,
            seed=None,
            context_window=None,
            prompt=prompt,
            input=content or "[Uploaded File]",
            output=result_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def supports_provider_batch(self) -> bool:
        return True

    def add_to_batch(
        self,
        custom_id: str,
        model: str,
        prompt: str,
        file: Optional[MediaFile],
        content: Optional[str],
        model_settings: ModelSettings,
    ) -> None:
        if file is not None:
            raise ValueError(
                "OpenAI Batch API does not support file uploads. "
                "Use a text-based file_reader instead of 'upload'."
            )
        response_format = (
            {"type": "json_object"} if model_settings.json_format else {"type": "text"}
        )
        self._batch_lines.append(
            {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": content},
                    ],
                    "temperature": model_settings.temperature,
                    "response_format": response_format,
                },
            }
        )

    def submit_batch(self) -> tuple[str, bytes]:
        jsonl_bytes = "\n".join(json.dumps(line) for line in self._batch_lines).encode()
        uploaded = self.client.files.create(
            file=("batch_input.jsonl", BytesIO(jsonl_bytes), "application/jsonl"),
            purpose="batch",
        )
        batch = self.client.batches.create(
            input_file_id=uploaded.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        return batch.id, jsonl_bytes

    def get_batch_status(self, provider_batch_id: str) -> ProviderBatchStatus:
        batch = self.client.batches.retrieve(provider_batch_id)
        terminal_statuses = {"completed", "failed", "expired", "cancelled"}
        is_complete = batch.status in terminal_statuses
        is_failed = batch.status in {"failed", "expired", "cancelled"}
        counts = batch.request_counts
        return ProviderBatchStatus(
            is_complete=is_complete,
            is_failed=is_failed,
            completed_count=counts.completed,
            failed_count=counts.failed,
            raw_status=batch.status,
        )

    def retrieve_batch_results(self, provider_batch_id: str) -> list[BatchResultEntry]:
        batch = self.client.batches.retrieve(provider_batch_id)
        raw = self.client.files.content(batch.output_file_id)
        results = []
        for line in raw.text.strip().splitlines():
            if not line:
                continue
            item = json.loads(line)
            custom_id = item["custom_id"]
            if item.get("error"):
                results.append(
                    BatchResultEntry(
                        custom_id=custom_id,
                        success=False,
                        output=None,
                        input_tokens=0,
                        output_tokens=0,
                        error_message=str(item["error"]),
                    )
                )
            else:
                body = item["response"]["body"]
                usage = body.get("usage", {})
                results.append(
                    BatchResultEntry(
                        custom_id=custom_id,
                        success=True,
                        output=body["choices"][0]["message"]["content"],
                        input_tokens=usage.get("prompt_tokens", 0),
                        output_tokens=usage.get("completion_tokens", 0),
                        error_message=None,
                    )
                )
        return results
