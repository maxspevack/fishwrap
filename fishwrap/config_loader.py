import os
import sys
from fishwrap.config_schema import FishwrapConfig

def load_config() -> FishwrapConfig:
    """
    Loads configuration from the path specified in FISHWRAP_CONFIG env var.
    Executes the file to get raw dict, then validates with Pydantic.
    """
    config_path = os.environ.get('FISHWRAP_CONFIG')
    
    if not config_path:
        # Fallback for dev/testing if not set
        if os.path.exists('config.py'):
            config_path = 'config.py'
        else:
            print("[WARN] FISHWRAP_CONFIG not set.")
            return None

    # Execute the config file as Python code
    d = {
        '__file__': os.path.abspath(config_path) # Inject __file__ for path resolution
    }
    
    try:
        with open(config_path, 'r') as f:
            exec(f.read(), d)
    except FileNotFoundError:
         print(f"[ERROR] Config file not found at {config_path}")
         sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to execute config file: {e}")
        sys.exit(1)

    # Filter for uppercase keys (convention)
    clean_config = {k: v for k, v in d.items() if k.isupper()}
    
    # Validate and Create Model
    try:
        config_model = FishwrapConfig(**clean_config)
        return config_model
    except Exception as e:
        print(f"[ERROR] Configuration Validation Failed: {e}")
        sys.exit(1)

# Singleton instance
Config = load_config()