from .base import BaseExportMode
from typing import List, Any, Dict, Union, Tuple
from io import BytesIO, StringIO
import pandas as pd
import csv


class RawExportMode(BaseExportMode):
    base_name = "raw"

    modes = ("csv", "excel")

    default_mode = "csv"

    def export(
        self, results: List[Dict[str, Any]], mode
    ) -> Tuple[Union[StringIO, BytesIO], str, str]:
        df = pd.DataFrame(results)
        if mode == self.default_mode:
            buffer = StringIO()
            df = df.replace({r"[\r\n]+": r"\\n"}, regex=True)
            df.to_csv(buffer, index=False, quoting=csv.QUOTE_ALL)
            buffer.seek(0)
            return (
                buffer,
                f"batch_export_{self.scientific_date_for_filename()}.csv",
                "text/csv",
            )
        else:
            excel_buffer = BytesIO()
            df = df.replace({r"[\r\n]+": " "}, regex=True)
            df = df.replace(r"[\x00-\x1F\x7F-\x9F]", " ", regex=True)
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            return (
                excel_buffer,
                f"batch_export_{self.scientific_date_for_filename()}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
