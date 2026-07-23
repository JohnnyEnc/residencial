"""SQLAlchemy Enum helper compatible with SQLite (VARCHAR) and Postgres."""

from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum


def str_enum(enum_cls: type[PyEnum], name: str):
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        values_callable=lambda members: [item.value for item in members],
    )
