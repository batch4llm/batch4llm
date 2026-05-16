import logging

from .endpoint_service import EndpointService
from .file_service import FileService
from batch4llm.manager.file_reader.reader_manager import FileReaderManager
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.manager.prompt_interpreter import interpret_prompt
from ..manager.database import Database
from ..manager.database.models.batch import BatchStatus
from ..manager.prompt_interpreter.prompt_interpreter import MultiPrompt
from batch4llm.celery.tasks.submit_provider_batch import submit_provider_batch

logger = logging.getLogger(__name__)


class BatchService:
    def __init__(
        self,
        db: Database,
        endpoint_service: EndpointService,
        file_service: FileService,
    ):
        self.db = db
        self.endpoint_service = endpoint_service
        self.file_service = file_service
        self.file_reader = FileReaderManager()
        self.client_manager = ClientManager()

    def start(
        self,
        prompt_id: int,
        endpoint_id: int,
        files: list[int],
        file_reader: str,
        model: str,
        temperature: float,
        json_format: bool,
        user_id: int,
        batch_worker_settings,
        use_provider_batch: bool = False,
    ) -> dict:
        batch_name = f"batch_{hash(model + str(endpoint_id) + str(prompt_id))}"
        endpoint = self.endpoint_service.get(endpoint_id, user_id, True)
        if not endpoint:
            raise ValueError(f"Endpoint ID {endpoint_id} does not exist")

        prompt_record = self.db.prompts.get(prompt_id, user_id)
        if not prompt_record:
            raise RuntimeError(f"Prompt ID {prompt_id} not found")

        prompt_content = prompt_record["content"]
        multi_prompt = prompt_record["multi_prompt"]
        logger.info(f"Multi Prompt: {multi_prompt}")
        if multi_prompt:
            try:
                prompts_list = interpret_prompt(prompt_content)
                logger.info("Batch with Multi-Prompt started")
                logger.info(f"Interpretation as {len(prompts_list)} prompts.")
            except Exception as e:
                logger.exception(e)
                raise ValueError(f"Invalid prompt content: {prompt_content}")
        else:
            prompts_list = [MultiPrompt("-", prompt_content)]

        initial_status = (
            BatchStatus.PROVIDER_BATCH_PENDING
            if use_provider_batch
            else BatchStatus.QUEUED
        )
        batch_args = {
            "name": batch_name,
            "status": initial_status,
            "endpoint_id": endpoint_id,
            "prompt_id": prompt_id,
            "file_reader": file_reader,
            "model": model,
            "temperature": temperature,
            "json_format": json_format,
            "user_id": user_id,
            "batch_worker_settings": batch_worker_settings,
            "use_provider_batch": use_provider_batch,
        }

        db_batch = self.db.batches.add(**batch_args)
        self.db.batches.add_batch_log(
            batch_id=db_batch["id"],
            message=f"Batch created with settings: \n {batch_args}",
        )

        for file_id in files:
            path = self.file_service.get_file_path(file_id, user_id)
            if path is None:
                raise ValueError(f"Invalid file: {file_id}")

            batch_file = self.db.batches.add_batch_file(
                batch_id=db_batch["id"],
                file_id=file_id,
            )
            for prompt in prompts_list:
                self.db.batches.add_batch_task(
                    batch_id=db_batch["id"],
                    file_id=file_id,
                    batch_file_id=batch_file["id"],
                    prompt=prompt.prompt,
                    prompt_marker=prompt.marker,
                )

        if use_provider_batch:
            submit_provider_batch.delay(db_batch["id"])
            self.db.batches.add_batch_log(
                batch_id=db_batch["id"],
                message="Provider batch submission queued.",
            )

        return db_batch

    def stop(self, batch_id: int, user_id: int) -> dict:
        check_batch = self.db.batches.get(batch_id=batch_id, user_id=user_id)
        if not check_batch:
            raise ValueError(
                f"Batch ID {batch_id} does not exist or user has not the permission"
            )
        self.db.batches.update_status(batch_id, BatchStatus.STOPPED)
        self.db.batches.add_batch_log(
            batch_id, "Batch set to 'STOPPED' remaining task will shut down now."
        )
        return check_batch

    def get_batch(self, batch_id: int, user_id: int) -> dict:
        return self.db.batches.get(batch_id, user_id)

    def get_batch_files(self, batch_id: int, user_id: int) -> dict:
        return self.db.batches.get_files(batch_id, user_id)

    def get_batch_log(self, batch_id: int, user_id: int, after_id: int = None) -> dict:
        return self.db.batches.get_batch_log(batch_id, user_id, after_id)

    def list_batches(self, user_id: int, archived: bool | None = None) -> dict:
        result = self.db.batches.list(user_id, archived)
        return result

    def set_batch_archived(self, batch_id: int, user_id: int, archived: bool) -> dict:
        return self.db.batches.set_archived(batch_id, user_id, archived)

    def list_engines(self) -> dict:
        result = self.client_manager.get_engines()
        return result

    def list_file_readers(self) -> dict:
        result = self.file_reader.get_supported()
        return result
