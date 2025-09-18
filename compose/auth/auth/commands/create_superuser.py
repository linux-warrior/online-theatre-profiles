from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from auth.db.sqlalchemy import async_session_maker  # noqa: E402
from auth.models.sqlalchemy import User  # noqa: E402
from auth.services.users.password import get_password_helper  # noqa: E402

stderr = Console(stderr=True)


class CommandError(Exception):
    pass


def main(login: Annotated[str, typer.Option()],
         password: Annotated[str, typer.Option()]) -> None:
    asyncio.run(main_async(login=login, password=password))


async def main_async(*, login: str, password: str) -> None:
    async with async_session_maker() as session:
        try:
            await create_superuser(
                session=session,
                login=login,
                password=password,
            )

        except CommandError as e:
            stderr.print(e)
            await session.rollback()
            raise typer.Exit(code=1)

        except Exception:
            await session.rollback()
            raise


async def create_superuser(*, session: AsyncSession, login: str, password: str) -> None:
    password_helper = await get_password_helper()

    statement = insert(User).values(
        login=login,
        password=password_helper.hash(password=password),
        is_superuser=True,
    )

    try:
        await session.execute(statement)
        await session.commit()

    except IntegrityError as e:
        raise CommandError('Failed to create a superuser.') from e


if __name__ == '__main__':
    typer.run(main)
