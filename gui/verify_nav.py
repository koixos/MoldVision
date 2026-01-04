from state import AppState, ImageState
import numpy as np

def test_events():
    print("Testing AppState events...")
    state = AppState()
    
    events_triggered = 0
    def on_change():
        nonlocal events_triggered
        events_triggered += 1
        print(f"Event triggered! Active index: {state.active_index}")

    state.add_listener(on_change)

    # Test adding image
    img = ImageState(path="test.png", filename="test.png", original=np.zeros((10,10,3)))
    state.add_image(img)
    if events_triggered == 1:
        print("PASS: Add image triggered event")
    else:
        print(f"FAIL: Add image events: {events_triggered}")

    # Test setting active
    state.add_image(img) # Add another, index 1
    state.set_active(0)
    if events_triggered == 3: # 1 (first add) + 1 (second add) + 1 (set active)
        print("PASS: Set active triggered event")
    else:
        print(f"FAIL: Set active events: {events_triggered}")
        
    print("Logic verification complete.")

if __name__ == "__main__":
    test_events()
