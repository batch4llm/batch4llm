from .base import BaseExportMode
from .raw_mode import RawExportMode
from .expanded_mode import ExpandedExportMode
from typing import List, Any, Dict, Type, Union, Tuple
from io import BytesIO, StringIO


class BatchExporter:
    _modes: Dict[str, Tuple[Type[BaseExportMode], str]] = {}

    @classmethod
    def register(cls, reader_cls: Type[BaseExportMode]):
        for mode in reader_cls.modes:
            public_name = f"{reader_cls.base_name}_{mode}".lower()
            cls._modes[public_name] = (reader_cls, mode)

    def __init__(self, mode: str):
        exporter_name = mode.lower()

        if exporter_name not in self._modes:
            raise ValueError(f"Unknown export mode: {exporter_name}")

        reader_cls, setting = self._modes[exporter_name]
        self.mode = reader_cls()
        self.setting = setting

    def export(
        self, results: List[Dict[str, Any]]
    ) -> Tuple[Union[StringIO, BytesIO], str, str]:
        return self.mode.export(results=results, mode=self.setting)


BatchExporter.register(RawExportMode)
BatchExporter.register(ExpandedExportMode)
