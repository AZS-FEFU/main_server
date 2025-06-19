from sqlalchemy import SMALLINT, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Attribute(Base):
    __tablename__ = "attributes"
    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(50))


    def __str__(self):
        return f"{self.name}"

