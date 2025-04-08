from __future__ import annotations

from typing import Annotated

from fastapi import Depends


class Page:
    size: int
    number: int

    def __init__(self, *, page_size: int = 50, page_number: int = 1) -> None:
        self.size = page_size if page_size <= 50 else 50
        self.number = page_number if page_number >= 1 else 1


PageDep = Annotated[Page, Depends()]
