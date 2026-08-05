"""User account model — simple email/password with hashed passwords."""
import hashlib
import secrets
import uuid

from sqlalchemy import Column, DateTime, Text, func

from src.db.base import Base, UniversalUUID


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    password_salt = Column(Text, nullable=False)
    tier = Column(Text, nullable=False, default="registered")  # registered, enterprise
    role = Column(Text, nullable=False, default="consumer")    # consumer, dealer, moderator, admin, super_admin, system  # noqa: E501
    api_key_hash = Column(Text, nullable=True)
    failed_login_attempts = Column(Text, nullable=False, default="0")  # stored as text for SQLite compat  # noqa: E501
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
        salt = salt or secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
        return h.hex(), salt

    def verify_password(self, password: str) -> bool:
        h, _ = self.hash_password(password, self.password_salt)  # type: ignore[arg-type]
        return h == self.password_hash
