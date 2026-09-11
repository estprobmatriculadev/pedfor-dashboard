import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações centrais do sistema."""
    ENV = os.getenv("ENV", "development")
    TIDB_HOST = os.getenv("TIDB_HOST", "")
    TIDB_PORT = int(os.getenv("TIDB_PORT", "4000"))
    TIDB_USER = os.getenv("TIDB_USER", "")
    TIDB_PASSWORD = os.getenv("TIDB_PASSWORD", "")
    TIDB_DATABASE = os.getenv("TIDB_DATABASE", "")
    TIDB_SSL_ENABLE = os.getenv("TIDB_SSL_ENABLE", "true").lower() in ("true", "1", "t")

    @classmethod
    def validate(cls):
        """Valida se todas as variáveis essenciais estão preenchidas."""
        missing = []
        if not cls.TIDB_HOST:
            missing.append("TIDB_HOST")
        if not cls.TIDB_USER:
            missing.append("TIDB_USER")
        if not cls.TIDB_DATABASE:
            missing.append("TIDB_DATABASE")
        return missing
