import os

from dotenv import load_dotenv


if os.getenv("APP_ENV", "development").lower() != "production":
    load_dotenv()

APP_ENV = os.getenv(
    "APP_ENV",
    "development"
).lower()


ALLOWED_ENVIRONMENTS = {
    "development",
    "testing",
    "production"
}


if APP_ENV not in ALLOWED_ENVIRONMENTS:
    raise RuntimeError(
        f"Invalid APP_ENV: {APP_ENV}. "
        f"Expected one of: "
        f"{', '.join(sorted(ALLOWED_ENVIRONMENTS))}"
    )


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

if APP_ENV == "production" and len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY must be at least 32 characters in production"
    )

JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_MINUTES = 30


if APP_ENV == "production":
    SQL_ECHO = False
else:
    SQL_ECHO = (
        os.getenv("SQL_ECHO", "false").lower()
        == "true"
    )