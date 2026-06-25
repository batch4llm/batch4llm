from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import BatchStatus, LogLevel
from batch4llm.manager.database.models.llm_request import LlmRequestStatus
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.manager.llm_client.models.response_model import LLMClientResponse
from batch4llm.manager.price_calculator import calculate_price

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


@app.task
def poll_provider_batches():
    client_manager = ClientManager()
    pending_batches = db.worker.get_provider_batch_pending_batches()
    logger.debug(f"Polling {len(pending_batches)} provider batch(es)")

    for batch in pending_batches:
        try:
            endpoint = db.worker.get_endpoint(batch.endpoint_id)
            client = client_manager.get_client(endpoint)

            status = client.get_batch_status(batch.provider_batch_id)
            logger.debug(
                f"Batch {batch.id} provider status: {status.raw_status} "
                f"(complete={status.is_complete})"
            )

            if not status.is_complete:
                continue

            if status.is_failed:
                db.batches.fail_all_queued_tasks(batch.id)
                db.batches.update_status(batch.id, BatchStatus.FAILED)
                db.batches.add_batch_log(
                    batch_id=batch.id,
                    message=f"Provider batch failed. Status: {status.raw_status}",
                    level=LogLevel.ERROR,
                )
                continue

            results = client.retrieve_batch_results(batch.provider_batch_id)
            for entry in results:
                llm_request_id = int(entry.custom_id)
                if entry.success:
                    engine_response = LLMClientResponse(
                        client=endpoint["client"],
                        model=batch.model,
                        prompt="",
                        input="[Provider Batch]",
                        output=entry.output,
                        input_tokens=entry.input_tokens,
                        output_tokens=entry.output_tokens,
                        temperature=batch.temperature,
                        json_format=batch.json_format,
                        top_p=batch.top_p,
                        top_k=batch.top_k,
                        max_output_tokens=batch.max_output_tokens,
                        seed=None,
                        context_window=None,
                    )

                    price = None
                    if endpoint["provider"].lower() != "self_hosted":
                        try:
                            model_name = batch.model.replace("models/", "")
                            price = calculate_price(
                                entry.input_tokens,
                                entry.output_tokens,
                                endpoint["provider"],
                                model_name,
                            )
                        except Exception as e:
                            logger.error(
                                f"Price calculation failed for request {llm_request_id}: {e}"
                            )

                    db.batches.update_llm_request_status(
                        llm_request_id,
                        status=LlmRequestStatus.COMPLETED,
                        engine_response=engine_response,
                        costs_in_usd=price,
                    )
                else:
                    db.batches.update_llm_request_status(
                        llm_request_id,
                        status=LlmRequestStatus.FAILED,
                    )
                    llm_request = db.worker.get_llm_request_by_id(llm_request_id)
                    if llm_request:
                        db.batches.add_task_log(
                            batch_task_id=llm_request.batch_task_id,
                            message=f"Provider batch request failed: {entry.error_message}",
                            level=LogLevel.ERROR,
                        )

            db.batches.update_status(batch.id, BatchStatus.COMPLETED)
            db.batches.add_batch_log(
                batch_id=batch.id,
                message=f"Provider batch completed. {status.completed_count} succeeded, {status.failed_count} failed.",
            )

        except Exception as e:
            logger.exception(e)
            db.batches.add_batch_log(
                batch_id=batch.id,
                message=f"Error while polling provider batch: {str(e)}",
                level=LogLevel.ERROR,
            )
