"""Playwright com stack própria; finally remove somente os dados efêmeros."""

import os
import secrets
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    project = f"repara-e2e-{secrets.token_hex(6)}"
    env = {**os.environ, "E2E_DB_PASSWORD": secrets.token_hex(24)}
    compose = ["docker", "compose", "-f", str(ROOT / "compose.e2e.yaml"), "-p", project]
    try:
        subprocess.run(
            [*compose, "up", "--build", "--detach", "--wait", "--wait-timeout", "180"],
            env=env,
            check=True,
        )
        subprocess.run(
            [*compose, "exec", "-T", "api", "alembic", "upgrade", "head"],
            env=env,
            check=True,
        )
        port = (
            subprocess.check_output(
                [*compose, "port", "frontend", "8080"], env=env, text=True
            )
            .strip()
            .rsplit(":", 1)[1]
        )
        npm = "npm.cmd" if os.name == "nt" else "npm"
        result = subprocess.run(
            [npm, "run", "test:e2e"],
            cwd=ROOT / "frontend",
            env={**env, "E2E_BASE_URL": f"http://127.0.0.1:{port}"},
            check=False,
        )
        return result.returncode
    finally:
        # Não há volumes nomeados; down descarta apenas o tmpfs deste projeto.
        subprocess.run([*compose, "down", "--remove-orphans"], env=env, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
