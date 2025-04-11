from __future__ import annotations

import json
import logging
import os


def setup_logging(*, file_path: str | os.PathLike[str] | None = None) -> None:
    logging.basicConfig(filename=file_path, level=logging.DEBUG)


def load_index_file(file_path: str | os.PathLike[str]) -> dict:
    with open(file_path, 'rb') as index_file:
        index_json = index_file.read().decode()

    return json.loads(index_json)
