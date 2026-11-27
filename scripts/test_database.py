"""Executa testes em um PostgreSQL efemero, sem usar o banco de desenvolvimento."""

import os
import secrets
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import URL

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def temporary_database() -> Iterator[str]:
    project = f"repara-db-test-{secrets.token_hex(4)}"
    password = secrets.token_urlsafe(24)
    env = {**os.environ, "TEST_DB_PASSWORD": password}
    compose = [
        "docker",
        "compose",
        "-f",
        str(ROOT / "compose.test.yaml"),
        "-p",
        project,
    ]
    try:
        subprocess.run(
            [*compose, "up", "--wait", "--wait-timeout", "120"],
            env=env,
            check=True,
        )
        published = subprocess.check_output(
            [*compose, "port", "db", "5432"], env=env, text=True
        ).strip()
        port = int(published.rsplit(":", 1)[1])
        url = URL.create(
            "postgresql+psycopg",
            username="repara_test",
            password=password,
            host="127.0.0.1",
            port=port,
            database="repara_test",
        )
        yield url.render_as_string(hide_password=False)
    finally:
        # Dados em tmpfs; nenhum volume de desenvolvimento participa deste projeto.
        subprocess.run([*compose, "down", "--remove-orphans"], env=env, check=True)


def main() -> int:
    with temporary_database() as url:
        env = {**os.environ, "TEST_DATABASE_URL": url}
        return subprocess.run(
            [sys.executable, "-m", "pytest"],
            cwd=ROOT / "backend",
            env=env,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
