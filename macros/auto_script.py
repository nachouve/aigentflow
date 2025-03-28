import pyautogui as pyag
import time
import os
import json

def find_window_and_focus(window_name):
    """Find a window by its title and bring it to the foreground."""
    try:
        windows = pyag.getWindowsWithTitle(window_name)
        if not windows:
            print(f"Window '{window_name}' not found.")
            return False
        window = windows[0]
        window.activate()
        print(f"Focused on window: {window_name}")
        return True
    except Exception as e:
        print(f"Error focusing window: {e}")
        return False

# Configuration
PAUSE = 0.5  # Delay between actions (in seconds)
TARGET_WINDOW = ""  # Window name to focus on (leave empty to skip)

# Points will be inserted here by the generator
# Recorded points as a list
all_points = [["click", "aa", 3422, 914], ["click", "s", 2858, 587]]

# Named points for direct access
aa = ("click", 3422, 914)  # Click coordinates
ss = ("click", 2858, 587)  # Click coordinates


def run_macro(repetitions=10, pause=PAUSE):
    """Run the recorded macro the specified number of times"""
    if TARGET_WINDOW:
        find_window_and_focus(TARGET_WINDOW)
    
    for rep in range(repetitions):
        print(f"Repetition {rep+1}/{repetitions}")
        
        # Point execution code will be inserted here
        
        # Execute each point
        #for point in all_points:
        #   if point[0] == 'click':
        #        x, y = point[2], point[3]
        #        pyag.moveTo(x, y)
        #        pyag.click()
        
        if aa[0] == 'click':
            x, y = aa[1], aa[2]
            pyag.moveTo(x, y)
            pyag.click()
            x, y = ss[1], ss[2]
            pyag.moveTo(x, y)  # Move to the same position again (optional)
            print(f"Clicked on aa")
        elif aa == 'element':
            # TODO and TEST
            try:
                x, y, w, h = point[2], point[3], point[4], point[5]
                # Take screenshot of just that region
                region_img = pyag.screenshot(region=(x, y, w, h))
                # Try to find that image on screen
                location = pyag.locate(region_img, pyag.screenshot())
                if location:
                    center = pyag.center(location)
                    pyag.click(center)
                else:
                    pass
            except Exception as e:
                print(f"Error with element ...")
        time.sleep(pause)
    
        
        time.sleep(pause)
        
if __name__ == "__main__":
    run_macro(repetitions=10, pause=0.25)
