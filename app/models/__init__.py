"""
This module imports all model files in the current directory.
"""
import os
import glob

# Get the directory of this file
models_dir = os.path.dirname(__file__)

# Import all .py files except __init__.py and files starting with '_'
for file in glob.glob(os.path.join(models_dir, "*.py")):
    module = os.path.basename(file)[:-3]
    if module not in ("__init__", "base_dict_mixin") and not module.startswith("_"):
        __import__(f"{__name__}.{module}")
