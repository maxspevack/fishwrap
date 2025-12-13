import os
import sys

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import _config

REQUIRED_TEMPLATES = [
    'layout.html',
    'card.html',
    'section.html',
    'sidebar_item.html',
    'transparency.html'
]

def test_templates():
    print(f"[TEST] Verifying templates for theme: {_config.THEME}")
    
    # Locate theme dir
    if os.path.isabs(_config.THEME):
        theme_path = _config.THEME
    else:
        # Resolve relative to fishwrap/
        # This mirrors renderers/html.py logic roughly
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        theme_path = os.path.join(repo_root, _config.THEME)
        
    template_dir = os.path.join(theme_path, 'templates')
    
    if not os.path.exists(template_dir):
        print(f"[FAIL] Template directory not found: {template_dir}")
        sys.exit(1)
        
    missing = []
    for tpl in REQUIRED_TEMPLATES:
        p = os.path.join(template_dir, tpl)
        if not os.path.exists(p):
            missing.append(tpl)
            
    if missing:
        print(f"[FAIL] Missing required templates: {missing}")
        sys.exit(1)
        
    print("[PASS] All required templates exist.")

if __name__ == "__main__":
    test_templates()
