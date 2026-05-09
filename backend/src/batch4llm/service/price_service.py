from .file_service import FileService
from ..manager.database import Database
from batch4llm.manager.price_calculator import estimate_batch_costs_in_usd


class PriceService:
    def __init__(self, db: Database, file_service: FileService):
        self.db = db
        self.file_service = file_service

    def estimate_batch_costs_in_usd(
        self,
        provider: str,
        model: str,
        file_reader: str,
        files: list[str],
        prompt=None,
        output=None,
    ) -> float:

        file_paths = []
        for name in files:
            path = self.file_service.get_file_path(name)
            if path is None:
                raise ValueError(f"Invalid file: {name}")
            file_paths.append(path)

        return estimate_batch_costs_in_usd(
            provider=provider,
            model=model,
            file_paths=file_paths,
            file_reader=file_reader,
            prompt=prompt,
            output=output,
        )
