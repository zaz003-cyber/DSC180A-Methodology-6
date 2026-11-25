"""Stage 1: fetch the raw dataset and assert its shape.

Run: python -m src.ingest
"""
import hashlib
import sys
import urllib.request

import pandas as pd

from src.config import DATA_URL, RAW

EXPECTED_MIN_ROWS = 700
EXPECTED_SHA256 = "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc"
REQUIRED_COLS = {"dteday", "cnt", "casual", "registered", "temp", "hum", "windspeed"}


def download(force: bool = False) -> None:
    if RAW.exists() and not force:
        return
    RAW.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(DATA_URL, RAW)


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW, parse_dates=["dteday"])
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"raw data is missing required columns: {sorted(missing)}")
    if len(df) < EXPECTED_MIN_ROWS:
        raise ValueError(f"raw data has only {len(df)} rows; expected >= {EXPECTED_MIN_ROWS}")
    return df


if __name__ == "__main__":
    download(force="--force" in sys.argv)
    actual = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"raw CSV checksum mismatch: expected {EXPECTED_SHA256}, found {actual}")
    df = load_raw()
    print(f"OK ingest: {len(df)} rows, {df.dteday.min().date()} -> {df.dteday.max().date()}")
