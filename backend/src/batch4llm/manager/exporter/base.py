from typing import List, Any, Dict, Union, Tuple, Iterable
from datetime import datetime
from io import BytesIO, StringIO
import pandas as pd


class BaseExportMode:
    """Common class for all export modes."""

    base_name: str
    modes: Iterable[str]
    default_mode: str

    def export(
        self, results: List[Dict[str, Any]], mode: str
    ) -> Tuple[Union[StringIO, BytesIO], str, str]:
        raise NotImplementedError

    @staticmethod
    def strip_timezones(df: pd.DataFrame) -> pd.DataFrame:
        """Excel cannot store tz-aware datetimes, so convert them to naive UTC.
        Columns mixing datetimes with other values (or with different offsets)
        end up with object dtype and are normalized via to_datetime first."""
        df = df.copy()
        for col in df.columns:
            series = df[col]
            if series.dtype == object:
                values = series.dropna()
                if (
                    values.empty
                    or not values.map(lambda v: isinstance(v, datetime)).all()
                ):
                    continue
                series = pd.to_datetime(series, utc=True)
            if isinstance(series.dtype, pd.DatetimeTZDtype):
                df[col] = series.dt.tz_convert("UTC").dt.tz_localize(None)
        return df

    def scientific_date_for_filename(self):
        now = datetime.now()
        return now.strftime("%y%m%d")
