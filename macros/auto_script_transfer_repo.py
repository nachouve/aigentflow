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
TARGET_WINDOW = "nachouve"  # Window name to focus on (leave empty to skip)

# Points will be inserted here by the generator
# Recorded points as a list
all_points = [
    ["click", "p01_settings", 100, 607], ["click", "02_details", 64, 346], 
    ["click", "03_manage", 1436, 210], ["click", "04_transfer", 1447, 254], 
    ["click", "05_click_ws_name", 715, 302], ["click", "09_back_to_repos", 395, 115],]

# Named points for direct access
p01_settings = ('click', 100, 607)  # Click coordinates
p02_details = ('click', 64, 346)  # Click coordinates
p03_manage = ('click', 1436, 210)  # Click coordinates
p04_transfer = ('click', 1447, 254)  # Click coordinates
p05_click_ws_name = ('click', 715, 302)  # Click coordinates


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
        
        if p01_settings[0] == 'click':
            x, y = p01_settings[1], p01_settings[2]
            pyag.moveTo(x, y)
            pyag.click()
            print(f"Clicked on p01_settings")
            
            for point in all_points[1:-1]:
                if point[0] == 'click':
                    x, y = point[2], point[3]
                    pyag.moveTo(x, y)
                    pyag.click()
                    print(f"Clicked on {point[1]}")
                    time.sleep(pause*3)
            
            pyag.typewrite('NachoConcha', interval=0.02)
            pyag.press('enter')
            
            time.sleep(pause)
            pyag.press('tab')
            time.sleep(pause)
            pyag.press('tab')
            time.sleep(pause)
            pyag.press('enter')
            
            time.sleep(pause*2)
            pyag.moveTo(all_points[-1][2], all_points[-1][3])
            pyag.click()
            print("DONE!")
        
        time.sleep(pause)
        
if __name__ == "__main__":
    
    x=110
    y=365
    for i in range(10):
        y2 = y + (i*62)
        pyag.moveTo(x, y2)
        pyag.click()
        time.sleep(1)
        run_macro(repetitions=1, pause=PAUSE)
        time.sleep(0.4)
        p10_sort_by_date = (1427, 328)
        pyag.moveTo(p10_sort_by_date[0], p10_sort_by_date[1])
        pyag.click()
        time.sleep(0.4)
