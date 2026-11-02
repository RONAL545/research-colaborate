"""Start the regular API on Render, migrating its configured database first."""

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    for prefix in ("postgres://", "postgresql://"):
        if database_url.startswith(prefix):
            database_url = "postgresql+psycopg://" + database_url[len(prefix):]
            break
    os.environ["DATABASE_URL"] = database_url
    os.chdir(Path(__file__).resolve().parents[1] / "backend")
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    os.execv(sys.executable, [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0", "--port", os.environ.get("PORT", "10000"),
    ])


if __name__ == "__main__":
    main()
