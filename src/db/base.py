from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.types import TypeDecorator, JSON, String, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, DATERANGE
import uuid as _uuid


class UniversalUUID(TypeDecorator):
    """UUID that works on both PostgreSQL (native UUID) and SQLite (string)."""
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, _uuid.UUID):
            return str(value) if dialect.name != "postgresql" else value
        return str(value)


class UniversalJSONB(TypeDecorator):
    """JSONB that works on both PostgreSQL (native JSONB) and SQLite (JSON text)."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class UniversalDATERANGE(TypeDecorator):
    """DATERANGE that works on PG (native) and SQLite (string)."""
    impl = String(64)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(DATERANGE())
        return dialect.type_descriptor(String(64))


class Base(DeclarativeBase):
    pass


class LineageMixin:
    schema_version = Column(Integer, nullable=False)
    parser_version = Column(Text, nullable=False)
    normalizer_version = Column(Text, nullable=False)
    pipeline_run_id = Column(UniversalUUID, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
