import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://c216:c216@localhost:5432/c216",
)
