"""User account model — simple email/password with hashed passwords."""
import uuid, hashlib, secrets
from sqlalchemy import Column, Text, DateTime, func
from src.db.base import Base, UniversalUUID


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    password_salt = Column(Text, nullable=False)
    tier = Column(Text, nullable=False, default="registered")  # registered, enterprise
    role = Column(Text, nullable=False, default="consumer")    # consumer, dealer, moderator, admin, super_admin, system
    api_key_hash = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
        salt = salt or secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return h.hex(), salt

    def verify_password(self, password: str) -> bool:
        h, _ = self.hash_password(password, self.password_salt)
        return h == self.password_hash
