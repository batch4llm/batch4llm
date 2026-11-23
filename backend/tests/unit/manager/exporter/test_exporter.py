from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from batch4llm.manager.exporter.exporter import BatchExporter

_CET = timezone(timedelta(hours=1))


def _rows():
    return [
        {
            "batch_task_id": 1,
            "status": "COMPLETED",
            "request_started_at": datetime(2026, 11, 16, 9, 30, tzinfo=timezone.utc),
            "output": '{"answer": "a"}',
        },
        {
            # different offset, same instant style as values coming from psycopg
            "batch_task_id": 2,
            "status": "COMPLETED",
            "request_started_at": datetime(2026, 11, 16, 11, 0, tzinfo=_CET),
            "output": '{"answer": "b"}',
        },
        {
            "batch_task_id": 3,
            "status": "FAILED",
            "request_started_at": None,
            "output": None,
        },
    ]


@pytest.mark.parametrize("mode", ["raw_excel", "long_format_excel"])
def test_excel_export_handles_tz_aware_datetimes(mode):
    buffer, filename, _ = BatchExporter(mode).export(_rows())

    assert filename.endswith(".xlsx")
    df = pd.read_excel(buffer)
    started = df.sort_values("batch_task_id")["request_started_at"].tolist()
    # exported as naive UTC
    assert started[0] == pd.Timestamp("2026-11-16 09:30:00")
    assert started[1] == pd.Timestamp("2026-11-16 10:00:00")
    assert pd.isna(started[2])


@pytest.mark.parametrize("mode", ["raw_csv", "long_format_csv"])
def test_csv_export_keeps_datetimes(mode):
    buffer, _, _ = BatchExporter(mode).export(_rows())

    text = buffer.getvalue()
    assert "2026-11-16 09:30:00+00:00" in text
    assert '"COMPLETED"' in text
    assert "BatchTaskStatus" not in text
