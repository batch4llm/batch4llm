from .base import BaseExportMode
from typing import List, Any, Dict, Union, Tuple
from io import BytesIO, StringIO
import pandas as pd
import json
import csv
import logging

logger = logging.getLogger(__name__)


class ExpandedExportMode(BaseExportMode):
    """
    ExpandedExportMode flattens and expands JSON-like output data into a tabular structure.
    It tries to interpret the 'output' field as JSON, expanding lists and dictionaries into
    separate rows or columns for CSV export.
    """

    base_name = "long_format"

    modes = ("csv", "excel")

    default_mode = "csv"

    @staticmethod
    def normalize_json(raw: str) -> str:
        s = raw.strip()
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("`")
            s = s.split("\n", 1)[1] if "\n" in s else ""
        return s.strip()

    def export(
        self, results: List[Dict[str, Any]], mode
    ) -> Tuple[Union[StringIO, BytesIO], str, str]:
        expanded_rows = []

        for row in results:
            base = {k: v for k, v in row.items() if k != "output"}
            raw = row.get("output")
            if not raw or not raw.strip():
                parsed = {}
            else:
                raw = self.normalize_json(raw)
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError as e:
                    logger.exception(e)
                    parsed = {"_output_raw": raw}

            if isinstance(parsed, list):
                for item in parsed:
                    new_row = base.copy()
                    if isinstance(item, dict):
                        for k, v in item.items():
                            new_row[f"_{k}"] = v
                    else:
                        new_row["value"] = item
                    expanded_rows.append(new_row)
            elif isinstance(parsed, dict):
                new_row = base.copy()
                for k, v in parsed.items():
                    new_row[f"_{k}"] = v
                expanded_rows.append(new_row)
            else:
                new_row = base.copy()
                new_row["value"] = parsed
                expanded_rows.append(new_row)

        df = pd.DataFrame(expanded_rows)
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
