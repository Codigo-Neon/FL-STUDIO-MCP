"""Parquet storage for the sample manifest.

Manifest is stored as a single parquet file. For 40k rows the file is
~10 MB and loads in <100ms. Schema is defined explicitly so we catch
mismatches early when adding new fields.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable

import pyarrow as pa
import pyarrow.parquet as pq

__all__ = ["MANIFEST_SCHEMA", "save_manifest", "load_manifest", "empty_manifest"]


MANIFEST_SCHEMA = pa.schema([
    pa.field("path", pa.string()),
    pa.field("filename", pa.string()),
    pa.field("relative_folder", pa.string()),
    pa.field("extension", pa.string()),
    pa.field("size_bytes", pa.int64()),
    pa.field("mtime", pa.int64()),
    pa.field("content_hash", pa.string()),
    pa.field("sample_type", pa.string()),
    pa.field("subtype", pa.string()),
    pa.field("genres", pa.list_(pa.string())),
    pa.field("moods", pa.list_(pa.string())),
    pa.field("key", pa.string()),
    pa.field("bpm", pa.int32()),
    pa.field("is_loop", pa.bool_()),
    pa.field("is_oneshot", pa.bool_()),
    pa.field("raw_tags", pa.list_(pa.string())),
    pa.field("indexed_at", pa.int64()),
])


def empty_manifest() -> list[dict]:
    return []


def save_manifest(path: Path | str, rows: Iterable[dict]) -> None:
    rows_list = list(rows)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Build column arrays explicitly to enforce the schema and handle Nones.
    columns: dict = {field.name: [] for field in MANIFEST_SCHEMA}
    for row in rows_list:
        for field in MANIFEST_SCHEMA:
            columns[field.name].append(row.get(field.name))

    table = pa.table(columns, schema=MANIFEST_SCHEMA)
    pq.write_table(table, target, compression="zstd")


def load_manifest(path: Path | str) -> list[dict]:
    target = Path(path)
    if not target.exists():
        return []
    table = pq.read_table(target)
    return table.to_pylist()
