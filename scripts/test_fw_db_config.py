import os
import sys
import subprocess
import tempfile
import sqlite3

# Validates that fw-db respects the --config flag
def test_cli_config():
    print("[TEST] Testing fw-db CLI Config Isolation...")
    
    # 1. Create unique temp config and DB
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test_iso.db')
        config_path = os.path.join(tmpdir, 'test_iso_config.py')
        
        with open(config_path, 'w') as f:
            f.write(f"DATABASE_URL = 'sqlite:///{db_path}'\n")
            f.write("ARTICLES_DB_FILE = 'dummy'\n")
            f.write("RUN_SHEET_FILE = 'dummy'\n")
            f.write("SECRETS_FILE = 'dummy'\n") # Minimal config
            
        # 2. Init DB (Manual SQLite to be fast, or alembic?)
        # fw-db status checks file existence.
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # 3. Run fw-db status
        cmd = [
            sys.executable, 
            'scripts/fw-db.py', 
            '--config', config_path, 
            'status'
        ]
        
        # We need to run from fishwrap/ dir so imports work
        cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[FAIL] fw-db failed: {result.stderr}")
            sys.exit(1)
            
        # 4. Assert Output contains correct DB path
        if f"Database File: {db_path}" in result.stdout:
            print("[PASS] fw-db targeted the correct config-defined DB.")
        else:
            print("[FAIL] fw-db did not target the correct DB.")
            print("Output:\n", result.stdout)
            sys.exit(1)

if __name__ == "__main__":
    test_cli_config()
