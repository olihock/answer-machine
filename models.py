import uuid

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID, BYTEA


class Base(DeclarativeBase):
    pass


class UploadFile(Base):
    __tablename__ = "upload_file"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid] = mapped_column(UUID(as_uuid=True))
    category: Mapped[str] = mapped_column(String)
    filename: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    content: Mapped[BYTEA] = mapped_column(BYTEA)


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String)
