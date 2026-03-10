from __future__ import annotations

import abc
import os

from .state import State


class Storage(abc.ABC):
    @abc.abstractmethod
    def load(self) -> State:
        ...

    @abc.abstractmethod
    def save(self, state: State) -> None:
        ...


class JsonFileStorage(Storage):
    _file_path: str

    def __init__(self, *, file_path: os.PathLike[str] | str) -> None:
        self._file_path = str(file_path)

    def load(self) -> State:
        state_json = '{}'

        try:
            with open(self._file_path, 'rb') as state_file:
                state_json = state_file.read().decode()

        except FileNotFoundError:
            pass

        return State.model_validate_json(state_json)

    def save(self, state: State) -> None:
        state_json = state.model_dump_json(indent=2)

        with open(self._file_path, 'wb') as state_file:
            state_file.write(state_json.encode())
