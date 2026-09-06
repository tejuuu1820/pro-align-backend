import os
import sys
import types

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if 'backend' not in sys.modules:
    try:
        import backend
    except ModuleNotFoundError:
        m = types.ModuleType('backend')
        m.__path__ = [current_dir]
        sys.modules['backend'] = m
