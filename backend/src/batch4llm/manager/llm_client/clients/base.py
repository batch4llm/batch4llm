from abc import ABC, abstractmethod
from typing import Optional

from batch4llm.manager.file_manager import MediaFile
from batch4llm.manager.llm_client.models.engine_health_model import EngineHealth
from batch4llm.manager.llm_client.models.response_model import (
    LLMClientResponse,
    ProviderBatchStatus,
    BatchResultEntry,
)
from batch4llm.manager.llm_client.models.model_settings_model import ModelSettings


class BaseLLMClient(ABC):

    def __init__(self, api_token: Optional[str] = None, base_url: Optional[str] = None):
        self.api_token = api_token
        self.base_url = base_url

    @abstractmethod
    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[MediaFile] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> LLMClientResponse:
        pass

    @abstractmethod
    def models(self) -> list[str]:
        pass

    @abstractmethod
    def health(self) -> EngineHealth:
        pass

    @abstractmethod
    def token_count(self, model: str, text: str) -> int:
        pass

    def supports_provider_batch(self) -> bool:
        return False

    def add_to_batch(
        self,
        custom_id: str,
        model: str,
        prompt: str,
        file: Optional[MediaFile],
        content: Optional[str],
        model_settings: ModelSettings,
    ) -> None:
        raise NotImplementedError

    def submit_batch(self) -> tuple[str, bytes]:
        raise NotImplementedError

    def get_batch_status(self, provider_batch_id: str) -> ProviderBatchStatus:
        raise NotImplementedError

    def retrieve_batch_results(self, provider_batch_id: str) -> list[BatchResultEntry]:
        raise NotImplementedError
