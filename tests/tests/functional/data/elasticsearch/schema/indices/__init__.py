from __future__ import annotations

from .films import index_data as films_index_data
from .genres import index_data as genres_index_data
from .persons import index_data as persons_index_data

indices_data: dict[str, dict] = {
    'films': films_index_data,
    'genres': genres_index_data,
    'persons': persons_index_data,
}
