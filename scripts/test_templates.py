import sys
import os
from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import _config

def test_templates():
    # Mock Theme Path for Test
    # Assuming we run from repo root
    _config.THEME = "demo/themes/basic"
    
    theme_name = _config.THEME
    print(f"[TEST] Verifying templates for theme: {theme_name}")
    
    template_dir = os.path.join(theme_name, 'templates')
    if not os.path.exists(template_dir):
        print(f"[FAIL] Template directory not found: {os.path.abspath(template_dir)}")
        sys.exit(1)
        
    env = Environment(loader=FileSystemLoader(template_dir))
    
    required_templates = ['layout.html', 'transparency.html'] # Index is now layout
    
    for t in required_templates:
        try:
            env.get_template(t)
            print(f"  [PASS] Found {t}")
        except Exception as e:
            print(f"  [FAIL] Missing {t}: {e}")
            sys.exit(1)
            
    print("[PASS] Templates are valid.")

if __name__ == "__main__":
    test_templates()