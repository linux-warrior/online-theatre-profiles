from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import Field

PhoneNumberField = Annotated[str, Field(pattern=r'^\+79\d{9}$')]
RatingField = Annotated[Decimal, Field(max_digits=3, decimal_places=1, ge=0, le=10)]
