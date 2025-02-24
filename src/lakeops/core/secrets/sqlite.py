import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet
from .interface import SecretManager
from .utils import redact_secret
from typing import Optional


class SQLiteSecretManager(SecretManager):
    def __init__(
        self, db_path: str = "secrets.db", encryption_key: Optional[str] = None
    ):
        self.db_path = Path(db_path)
        # Generate or use provided encryption key
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS secrets (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    def _encrypt(self, value: str) -> bytes:
        return self.cipher_suite.encrypt(value.encode())

    def _decrypt(self, value: bytes) -> str:
        return self.cipher_suite.decrypt(value).decode()

    def write(self, key: str, value: str, scope: Optional[str] = None) -> None:
        encrypted_value = self._encrypt(value)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO secrets (key, value) VALUES (?, ?)",
                (key, encrypted_value),
            )
            conn.commit()

    def read(
        self, key: str, scope: Optional[str] = None, redacted: bool = True
    ) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM secrets WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result is None:
                raise KeyError(f"Secret not found: {key}")

            decrypted_value = self._decrypt(result[0])
            return redact_secret(decrypted_value) if redacted else decrypted_value
