import uuid

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class UploadFile(Base):
    __tablename__ = "upload_file"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid] = mapped_column(UUID(as_uuid=True))
    category: Mapped[str] = mapped_column(String)
    filename: Mapped[str] = mapped_column(String)
