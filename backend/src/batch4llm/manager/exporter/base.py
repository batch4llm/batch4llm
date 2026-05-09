from typing import List, Any, Dict, Union, Tuple, Iterable
from datetime import datetime
from io import BytesIO, StringIO


class BaseExportMode:
    """Common class for all export modes."""

    base_name: str
    modes: Iterable[str]
    default_mode: str

    def export(
        self, results: List[Dict[str, Any]], mode: str
    ) -> Tuple[Union[StringIO, BytesIO], str, str]:
        raise NotImplementedError

    def scientific_date_for_filename(self):
        now = datetime.now()
        return now.strftime("%y%m%d")
