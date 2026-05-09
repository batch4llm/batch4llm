import base64
import json
from typing import Optional

import anthropic
from anthropic import APIStatusError

from batch4llm.manager.file_manager import MediaFile
from batch4llm.manager.llm_client.clients.base import BaseLLMClient
from batch4llm.manager.llm_client.models.engine_health_model import EngineHealth
from batch4llm.manager.llm_client.models.exceptions import RateLimitError
from batch4llm.manager.llm_client.models.model_settings_model import ModelSettings
from batch4llm.manager.llm_client.models.response_model import (
    LLMClientResponse,
    ProviderBatchStatus,
    BatchResultEntry,
)


class AnthropicLLMClient(BaseLLMClient):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        self.client = anthropic.Anthropic(api_key=api_token)
        self._batch_requests: list = []

    def models(self) -> list[str]:
        models = self.client.models.list()
        return [m.id for m in models.data]

    def health(self) -> EngineHealth:
        try:
            self.models()
            return EngineHealth(True)
        except Exception as e:
            return EngineHealth(False, str(e))

    def token_count(self, model: str, text: str) -> int:
        response = self.client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": text}],
        )
        return response.input_tokens

    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[MediaFile] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> LLMClientResponse:
        if file is None and content is None:
            raise ValueError("Either file or content must be specified")

        if file:
            encoded = base64.standard_b64encode(file.data).decode("utf-8")
            user_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": file.mime_type,
                        "data": encoded,
                    },
                },
            ]
        else:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "text", "text": content},
            ]

        system_prompt = (
            "Respond only with valid JSON. No explanation, no markdown."
            if model_settings.json_format
            else None
        )

        kwargs = {
            "model": model,
            "max_tokens": model_settings.max_output_tokens or 4096,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": model_settings.temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if model_settings.top_p is not None:
            kwargs["top_p"] = model_settings.top_p
        if model_settings.top_k is not None:
            kwargs["top_k"] = model_settings.top_k

        try:
            response = self.client.messages.create(**kwargs)
        except APIStatusError as e:
            if e.status_code == 429:
                raise RateLimitError(e)
            raise

        output_text = response.content[0].text

        return LLMClientResponse(
            client=self.__class__.__name__,
            model=model,
            temperature=model_settings.temperature,
            json_format=model_settings.json_format,
            top_p=model_settings.top_p,
            top_k=model_settings.top_k,
            max_output_tokens=model_settings.max_output_tokens,
            seed=model_settings.seed,
            context_window=None,
            prompt=prompt,
            input=content or "[Uploaded File]",
            output=output_text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
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
        if file:
            encoded = base64.standard_b64encode(file.data).decode("utf-8")
            user_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": file.mime_type,
                        "data": encoded,
                    },
                },
            ]
        else:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "text", "text": content},
            ]

        params: dict = {
            "model": model,
            "max_tokens": model_settings.max_output_tokens or 4096,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": model_settings.temperature,
        }
        if model_settings.json_format:
            params["system"] = (
                "Respond only with valid JSON. No explanation, no markdown."
            )
        if model_settings.top_p is not None:
            params["top_p"] = model_settings.top_p
        if model_settings.top_k is not None:
            params["top_k"] = model_settings.top_k

        self._batch_requests.append({"custom_id": custom_id, "params": params})

    def submit_batch(self) -> tuple[str, bytes]:
        response = self.client.beta.messages.batches.create(
            requests=self._batch_requests
        )
        jsonl_bytes = "\n".join(json.dumps(r) for r in self._batch_requests).encode()
        return response.id, jsonl_bytes

    def get_batch_status(self, provider_batch_id: str) -> ProviderBatchStatus:
        batch = self.client.beta.messages.batches.retrieve(provider_batch_id)
        is_complete = batch.processing_status == "ended"
        counts = batch.request_counts
        return ProviderBatchStatus(
            is_complete=is_complete,
            is_failed=is_complete and counts.succeeded == 0 and counts.errored > 0,
            completed_count=counts.succeeded,
            failed_count=counts.errored,
            raw_status=batch.processing_status,
        )

    def retrieve_batch_results(self, provider_batch_id: str) -> list[BatchResultEntry]:
        results = []
        for item in self.client.beta.messages.batches.results(provider_batch_id):
            if item.result.type == "succeeded":
                message = item.result.message
                results.append(
                    BatchResultEntry(
                        custom_id=item.custom_id,
                        success=True,
                        output=message.content[0].text,
                        input_tokens=message.usage.input_tokens,
                        output_tokens=message.usage.output_tokens,
                        error_message=None,
                    )
                )
            else:
                results.append(
                    BatchResultEntry(
                        custom_id=item.custom_id,
                        success=False,
                        output=None,
                        input_tokens=0,
                        output_tokens=0,
                        error_message=str(item.result),
                    )
                )
        return results
