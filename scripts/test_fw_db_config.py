import os
import sys
import subprocess
import sqlite3
from pathlib import Path

# Validates that fw-db respects the --config flag.
# The new config shape is an instance directory containing masthead.toml.
# The DATABASE_URL is derived from the instance directory's name as
# sqlite:///demo/data/<dirname>.db (see fishwrap/_config.py).


def test_cli_config():
    print("[TEST] Testing fw-db CLI Config Isolation...")

    repo_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    # Create a unique instance directory under demo/<name>/.
    # We deliberately put it inside demo/ rather than /tmp/ because the
    # DATABASE_URL derivation uses Path("demo/data") / f"{dirname}.db".
    instance_name = f"test_iso_{os.getpid()}"
    instance_dir = repo_root / "demo" / instance_name
    instance_dir.mkdir(parents=True, exist_ok=True)

    masthead_path = instance_dir / "masthead.toml"
    expected_db_path = repo_root / "demo" / "data" / f"{instance_name}.db"

    try:
        masthead_path.write_text(
            '[identity]\n'
            'name = "Test"\n'
            'timezone = "UTC"\n'
            '\n'
            '[engine]\n'
            'expiration_hours = 24\n'
            '\n'
            '[[section]]\n'
            'id = "test"\n'
            'title = "Test"\n'
            'description = "Test"\n'
            'edition_size = 1\n'
            'lead_count = 1\n'
            'feature_count = 0\n'
            'max_per_source = 1\n'
            'keywords = []\n'
            '\n'
            '[feeds]\n'
            'urls = ["https://example.com/feed.xml"]\n'
        )

        expected_db_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite3.connect(str(expected_db_path)).close()

        cmd = [
            sys.executable,
            'scripts/fw-db.py',
            '--config', str(instance_dir),
            'status',
        ]
        result = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FAIL] fw-db failed: {result.stderr or result.stdout}")
            sys.exit(1)

        if f"Database File: {expected_db_path}" in result.stdout:
            print("[PASS] fw-db targeted the correct config-defined DB.")
        else:
            print("[FAIL] fw-db did not target the expected DB.")
            print("expected:", expected_db_path)
            print("Output:\n", result.stdout)
            sys.exit(1)
    finally:
        if masthead_path.exists():
            masthead_path.unlink()
        if instance_dir.exists():
            try:
                instance_dir.rmdir()
            except OSError:
                pass
        if expected_db_path.exists():
            expected_db_path.unlink()


if __name__ == "__main__":
    test_cli_config()
