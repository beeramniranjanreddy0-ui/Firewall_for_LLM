from __future__ import annotations

import atexit
import os
import tempfile
from pathlib import Path

database_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
database_file.close()

os.environ.setdefault("DATABASE_URL", f"sqlite:///{database_file.name}")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "1000")


@atexit.register
def cleanup_test_database() -> None:
    try:
        Path(database_file.name).unlink(missing_ok=True)
    except PermissionError:
        pass
    except FileNotFoundError:
        pass
