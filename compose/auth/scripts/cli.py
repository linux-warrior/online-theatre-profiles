from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from typer import Typer

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from auth.db.sqlalchemy import engine  # noqa: E402
from auth.models.sqlalchemy import User  # noqa: E402
from auth.services.users.password import PasswordHelper  # noqa: E402

app = Typer()


@app.command()
def create_superuser(login: str, password: str):
    asyncio.run(create_superuser_async(login=login, password=password))


async def create_superuser_async(login: str, password: str):
    async with engine.begin() as connection:

        superuser = {
            "login": login,
            "password": PasswordHelper().hash(password),
            "is_superuser": True
        }

        statement = insert(User).values(superuser)

        try:
            await connection.execute(statement=statement)
            await connection.commit()
            print(f"Superuser with login={login} is created")
        except SQLAlchemyError:
            print("Creation of superuser is failed")
            await connection.rollback()
        finally:
            await connection.close()


if __name__ == '__main__':
    app()
