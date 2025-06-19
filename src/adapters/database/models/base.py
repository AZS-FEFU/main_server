from datetime import datetime

from sqlalchemy import BIGINT, TIMESTAMP, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.utils.time import utc_signed_now


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class that provides metadata and id with int4
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
