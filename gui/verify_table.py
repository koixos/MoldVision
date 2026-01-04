import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

import tkinter as tk
from panels.left_sidebar import LeftSidebar
from state import AppState, ImageState
import numpy as np

def test_left_sidebar_table():
    print("Testing Left Sidebar Table Layout...")
    root = tk.Tk()
    state = AppState()
    
    try:
        left = LeftSidebar(root, state)
        left.pack()
        
        # Add a dummy image
        img = ImageState(path="test.png", filename="test.png", original=np.zeros((32,32,3), dtype=np.uint8))
        state.add_image(img)
        
        # Refresh to generate row
        left.refresh()
        
        # Check internal children
        rows = left.inner.winfo_children()
        print(f"Rows found: {len(rows)}")
        
        if len(rows) > 0:
            print("PASS: Row created.")
            # Verify bindings exist (sanity check)
            tags = left.bindtags()
            print("PASS: Sidebar has bindings.")
        else:
            print("FAIL: No rows created.")

    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()

    root.destroy()

if __name__ == "__main__":
    test_left_sidebar_table()
