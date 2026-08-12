import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "instance", "travel.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AI_PROVIDER = os.environ.get("AI_PROVIDER", "mock")
    AI_MODEL = os.environ.get("AI_MODEL", "claude-sonnet-4-6")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

    FLIGHT_PROVIDER = os.environ.get("FLIGHT_PROVIDER", "mock")

    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
