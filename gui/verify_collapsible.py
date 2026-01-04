import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

import tkinter as tk
from panels.left_sidebar import LeftSidebar
from state import AppState, ImageState
import numpy as np

def test_collapsible_sidebar():
    print("Testing Collapsible Sidebar...")
    root = tk.Tk()
    state = AppState()
    
    try:
        left = LeftSidebar(root, state)
        left.pack()
        
        # Add basic img
        img = ImageState(path="test.png", filename="test.png", original=np.zeros((32,32,3), dtype=np.uint8))
        state.add_image(img)
        left.refresh()
        
        print(f"Initial Width: {left.winfo_width()} (Expected ~380, depends on pack/update)")
        # Note: winfo_width needs update
        root.update()
        print(f"Width after update: {left.winfo_width()}")
        
        # Toggle
        print("Toggling...")
        left._toggle_sidebar()
        root.update()
        
        width_collapsed = left.winfo_width()
        print(f"Collapsed Width: {width_collapsed}")
        
        if width_collapsed < 100:
            print("PASS: Sidebar collapsed correctly.")
        else:
            print("FAIL: Sidebar did not collapse.")

        # Toggle Back
        print("Expanding...")
        left._toggle_sidebar()
        root.update()
        print(f"Expanded Width: {left.winfo_width()}")

    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()

    root.destroy()

if __name__ == "__main__":
    test_collapsible_sidebar()
