__version__ = "1.3.3"

import os
import nltk

# Configure NLTK to look for data in the local project directory
# structure: fishwrap/fishwrap/__init__.py -> fishwrap/nltk_data
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_nltk_data_path = os.path.join(_base_dir, 'nltk_data')
nltk.data.path.append(_nltk_data_path)
