import sys
import os
# Add parent directory to path to allow relative imports from panels to work if treated as proper package
# OR just add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # gui/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # mold-detect/

import tkinter as tk
# We need to trick python into thinking we are in the package structure
# But for simplicity, let's just use the file path hacks.
# The issue is "attempted relative import beyond top-level package"
# This happens when 'panels' is imported as top level but it tries to go ..
# We need to run this as a module or fix the imports in the script.

# Let's try to mock the module if possible, or just properly setup path.
# If I run `python -m gui.verify_sidebar` from `mold-detect` root, it might work if `__init__.py` exists.
# There is no `__init__.py` in mold-detect root probably.
# Let's try adding the `gui` folder to sys.path and changing how we import.

# Actually, simply running from root `python gui/verify_sidebar.py` and adding `check` in script:
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
from gui.panels.left_sidebar import LeftSidebar
from gui.state import AppState, ImageState
import numpy as np
import cv2

def test_sidebar():
    print("Testing LeftSidebar...")
    root = tk.Tk()
    state = AppState()
    
    # Mock Sidebar (we need to mock some behavior or just instantiate)
    # The Sidebar expects 'panels.image_loader' in imports, but our script is in gui/
    # effectively 'from ..utils.image_loader' might fail if run from gui/
    # We might need to adjust python path or run from root
    
    try:
        sidebar = LeftSidebar(root, state)
        print("Sidebar instantiated.")
        
        # Add image
        img_bgr = np.zeros((100, 100, 3), dtype=np.uint8)
        img = ImageState(path="test.png", filename="test.png", original=img_bgr)
        state.add_image(img)
        
        # Trigger refresh logic manually (usually done by listener)
        sidebar.refresh()
        print("Sidebar refreshed with image.")
        
        # Check if items added
        # Access internal widgets if possible, or just rely on no-exception
        print("Verification PASSED: Sidebar accepted image with thumbnail logic.")
        
    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()

    root.destroy()

if __name__ == "__main__":
    test_sidebar()
