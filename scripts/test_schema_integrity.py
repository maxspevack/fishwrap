import subprocess
import sys
import os

def test_schema_integrity():
    print("[TEST] Verifying Schema Integrity (No pending migrations)...")
    
    # We need to run this against a real DB. Let's use vanilla.db.
    # Note: 'check' command checks if models match DB.
    # But for SQLite, 'check' might be limited.
    # Alternative: 'alembic upgrade head' should output nothing if up to date.
    
    # Let's try 'alembic check'
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # We must point to a specific DB to check against.
    cmd = [
        './venv/bin/alembic',
        '-x', 'url=sqlite:///demo/data/vanilla.db',
        'check'
    ]
    
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[PASS] Schema is in sync.")
        else:
            # If 'check' is not supported or fails
            if "No such command" in result.stderr:
                print("[SKIP] Alembic check command not found.")
            else:
                print(f"[FAIL] Schema drift detected or error:\n{result.stdout}\n{result.stderr}")
                sys.exit(1)
    except Exception as e:
        print(f"[FAIL] execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_schema_integrity()
