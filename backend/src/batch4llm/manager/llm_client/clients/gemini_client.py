import io
from typing import Optional

from batch4llm.manager.file_manager import MediaFile
from batch4llm.manager.llm_client.clients.base import BaseLLMClient
import tiktoken
from google import genai
from google.genai import errors as genai_errors

from batch4llm.manager.llm_client.models.engine_health_model import EngineHealth
from batch4llm.manager.llm_client.models.exceptions import RateLimitError
from batch4llm.manager.llm_client.models.model_settings_model import ModelSettings
from batch4llm.manager.llm_client.models.response_model import LLMClientResponse


class GeminiLLMClient(BaseLLMClient):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        self.client = genai.Client(api_key=api_token)

    def models(self) -> list[str]:
        models = self.client.models.list()
        model_ids = [m.name for m in models]
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

        if file:
            file_obj = io.BytesIO(file.data)
            file_obj.name = file.name

            file = self.client.files.upload(
                file=file_obj,
                config=genai.types.UploadFileConfig(
                    mime_type=file.mime_type, display_name=file.name
                ),
            )
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"file_data": {"file_uri": file.uri}},
                    ],
                },
            ]
        else:
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"text": content},
                    ],
                },
            ]

        response_type = (
            "application/json" if model_settings.json_format else "text/plain"
        )
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,  # type: ignore
                config={  # type: ignore
                    "temperature": model_settings.temperature,
                    "response_mime_type": (response_type),
                },
            )
        except genai_errors.ClientError as e:
            if e.code == 429:
                raise RateLimitError(e)
            else:
                raise e
        except genai_errors.ServerError as e:
            if e.code == 503:
                raise RateLimitError(e)
            else:
                raise e

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
            output=response.text,
            input_tokens=response.usage_metadata.prompt_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
        )
