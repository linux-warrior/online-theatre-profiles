from __future__ import annotations

import os

from .state import State


class Storage:
    def load(self) -> State:
        raise NotImplementedError

    def save(self, state: State) -> None:
        raise NotImplementedError


class JsonFileStorage(Storage):
    file_path: str

    def __init__(self, *, file_path: os.PathLike[str] | str) -> None:
        self.file_path = str(file_path)

    def load(self) -> State:
        state_json = '{}'

        try:
            with open(self.file_path, 'rb') as state_file:
                state_json = state_file.read().decode()

        except FileNotFoundError:
            pass

        return State.model_validate_json(state_json)

    def save(self, state: State) -> None:
        state_json = state.model_dump_json(indent=2)

        with open(self.file_path, 'wb') as state_file:
            state_file.write(state_json.encode())
