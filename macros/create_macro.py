"""
AIgentFlow Macro Recorder
-------------------------

A tool to create automation macros by recording mouse actions and screen elements.

Usage:
    1. Run the script and use the menu to record mouse positions and screen elements
    2. Each recorded point should be given a meaningful name
    3. Save points for future use or generate runnable Python scripts
    4. The generated scripts can be customized for specific automation tasks

Requirements:
    - pyautogui
    - keyboard
"""

import pyautogui as pyag
import keyboard
import time
import os
import json
import shutil

# Constants
TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_template.py")
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_macros")

def main():
    """Main function - displays menu and handles user input"""
    print("\nWelcome to AIgentFlow Macro Recorder")
    print("------------------------------------")
    print("Record mouse positions and generate automation scripts")
    
    # Ensure directories exist
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    recorded_points = []
    
    while True:
        print("\n--- Main Menu ---")
        print("1) Record XY position")
        print("2) Record screen element (without cursor)")
        print("3) Show recorded points")
        print("4) Generate script")
        print("5) Save points")
        print("6) Load points")
        print("7) Exit")
    
        option = input("Select an option: ")
        
        if option == "1":
            record_xy(recorded_points)
        elif option == "2":
            record_element(recorded_points)
        elif option == "3":
            show_points(recorded_points)
        elif option == "4":
            generate_script(recorded_points)
        elif option == "5":
            save_points(recorded_points)
        elif option == "6":
            loaded = load_points()
            if loaded:
                recorded_points = loaded
        elif option == "7":
            print("Exiting program...")
            break
        else:
            print("Invalid option. Please try again.")

def record_xy(points):
    print("\nMove cursor to desired position and press 's' to record.")
    print("Press 'q' to cancel.")
    
    while True:
        x, y = pyag.position()
        print(f"\rCurrent position: X={x}, Y={y}", end="", flush=True)
        
        if keyboard.is_pressed('s'):
            name = input("\nEnter a name for this point: ")
            # Default name if user doesn't provide one
            if not name:
                name = f"point_{len(points) + 1}"
            points.append(('click', name, x, y))
            print(f"\nPoint '{name}' recorded: X={x}, Y={y}")
            time.sleep(0.3)  # Small delay to avoid multiple recordings
            break
        elif keyboard.is_pressed('q'):
            print("\nRecording canceled.")
            time.sleep(0.3)
            break

def record_element(points):
    print("\nSelect the element area (drag with mouse).")
    print("Press 'q' to cancel.")
    
    try:
        region = pyag.locateOnScreen(pyag.screenshot())
        if region:
            x, y, w, h = region
            name = input("\nEnter a name for this element: ")
            # Default name if user doesn't provide one
            if not name:
                name = f"element_{len(points) + 1}"
            points.append(('element', name, x, y, w, h))
            print(f"Element '{name}' recorded: X={x}, Y={y}, Width={w}, Height={h}")
    except Exception as e:
        print(f"Failed to record element: {e}")

def show_points(points):
    print("\n--- Recorded Points ---")
    for i, point in enumerate(points, 1):
        if point[0] == 'click':
            print(f"{i}) '{point[1]}': Click at X={point[2]}, Y={point[3]}")
        elif point[0] == 'element':
            print(f"{i}) '{point[1]}': Element at X={point[2]}, Y={point[3]}, Width={point[4]}, Height={point[5]}")

def save_points(points):
    if not points:
        print("No points to save.")
        return
        
    name = input("Enter name for this set of points: ")
    if not name:
        print("Save canceled.")
        return
        
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    file_path = os.path.join(SAVE_DIR, f"{name}.json")
    with open(file_path, "w") as f:
        json.dump(points, f)
        
    print(f"Points saved as '{name}'")

def load_points():
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    saved_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
    
    if not saved_files:
        print("No saved points found.")
        return None
        
    print("\n--- Saved Point Sets ---")
    for i, file in enumerate(saved_files, 1):
        print(f"{i}) {os.path.splitext(file)[0]}")
        
    try:
        choice = int(input("\nSelect a file (0 to cancel): "))
        if choice == 0:
            return None
            
        selected_file = saved_files[choice-1]
        file_path = os.path.join(SAVE_DIR, selected_file)
        
        with open(file_path, "r") as f:
            points = json.load(f)
            
        print(f"Loaded points from '{os.path.splitext(selected_file)[0]}'")
        return points
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

def find_window_and_focus(window_name):
    """
    Find a window by its title and bring it to the foreground.
    
    Args:
        window_name (str): Title of the window to find and focus
        
    Returns:
        bool: True if window was found and focused, False otherwise
    """
    try:
        windows = pyag.getWindowsWithTitle(window_name)
        if not windows:
            print(f"Window '{window_name}' not found.")
            return False
        window = windows[0]
        window.activate()
        print(f"Focused on window: {window_name}")
    except IndexError:
        print(f"Window '{window_name}' not found.")
        return False
    return True

def create_template_if_missing():
    """Create the template file if it doesn't exist"""
    if os.path.exists(TEMPLATE_FILE):
        return
        
    template = """import pyautogui as pyag
import time
import os
import json

def find_window_and_focus(window_name):
    \"\"\"Find a window by its title and bring it to the foreground.\"\"\"
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
# POINTS_PLACEHOLDER

def run_macro(repetitions=10, pause=PAUSE):
    \"\"\"Run the recorded macro the specified number of times\"\"\"
    if TARGET_WINDOW:
        find_window_and_focus(TARGET_WINDOW)
    
    for rep in range(repetitions):
        print(f"Repetition {rep+1}/{repetitions}")
        
        # Point execution code will be inserted here
        # EXECUTION_PLACEHOLDER
        
        time.sleep(pause)
        
if __name__ == "__main__":
    run_macro(repetitions=10, pause=PAUSE)
"""
    
    os.makedirs(os.path.dirname(TEMPLATE_FILE), exist_ok=True)
    with open(TEMPLATE_FILE, "w") as f:
        f.write(template)

def generate_script(points):
    """
    Generate an executable Python script from recorded points
    
    Args:
        points (list): List of recorded points (clicks and elements)
    """
    if not points:
        print("No points to generate script.")
        return

    # Ensure template file exists
    create_template_if_missing()
    
    # Read template
    try:
        with open(TEMPLATE_FILE, "r") as f:
            template = f.read()
    except FileNotFoundError:
        print("Template file not found. Using default template.")
        template = "# Default template used\n\nimport pyautogui as pyag\nimport time\n\n# POINTS_PLACEHOLDER\n\n# EXECUTION_PLACEHOLDER\n"
    
    # Create points definitions
    points_code = "# Recorded points as a list\nall_points = " + json.dumps(points) + "\n\n"
    points_code += "# Named points for direct access\n"
    
    for point in points:
        if point[0] == 'click':
            points_code += f"{point[1]} = ('click', {point[2]}, {point[3]})  # Click coordinates\n"
        elif point[0] == 'element':
            points_code += f"{point[1]} = ('element', {point[2]}, {point[3]}, {point[4]}, {point[5]})  # Element region (x, y, w, h)\n"
    
    # Create execution code
    execution_code = f"""
        # Execute each point
        #for point in all_points:
        #   if point[0] == 'click':
        #        x, y = point[2], point[3]
        #        pyag.moveTo(x, y)
        #        pyag.click()
        
        if {points[0][1]}[0] == 'click':
            x, y = {points[0][1]}[1], {points[0][1]}[2]
            pyag.moveTo(x, y)
            pyag.click()
            print(f"Clicked on {points[0][1]}")
        elif {points[0][1]} == 'element':
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
    """
    
    # Replace placeholders in template
    script_content = template.replace("# POINTS_PLACEHOLDER", points_code)
    script_content = script_content.replace("# EXECUTION_PLACEHOLDER", execution_code)
    
    # Get target window name
    window_name = input("Enter window name to focus on (leave empty to skip): ")
    if window_name:
        script_content = script_content.replace('TARGET_WINDOW = ""', f'TARGET_WINDOW = "{window_name}"')
    
    # Save generated script
    script_name = input("Enter name for the script (default: auto_script.py): ")
    if not script_name:
        script_name = "auto_script.py"
    elif not script_name.endswith(".py"):
        script_name += ".py"
        
    with open(script_name, "w") as f:
        f.write(script_content)
    
    print(f"\nScript generated as '{script_name}'")
    print("Ready to use!")

if __name__ == "__main__":
    main()