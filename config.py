import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not configured"
    )


JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_MINUTES = 30


SQL_ECHO = (
    os.getenv("SQL_ECHO", "false").lower()
    == "true"
)