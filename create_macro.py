import pyautogui as pyag
import keyboard
import time
import os
import json

def main():
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
        
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_macros")
    os.makedirs(save_dir, exist_ok=True)
    
    file_path = os.path.join(save_dir, f"{name}.json")
    with open(file_path, "w") as f:
        json.dump(points, f)
        
    print(f"Points saved as '{name}'")

def load_points():
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_macros")
    os.makedirs(save_dir, exist_ok=True)
    
    saved_files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
    
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
        file_path = os.path.join(save_dir, selected_file)
        
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

def generate_script(points):
    if not points:
        print("No points to generate script.")
        return

    script_content = """import pyautogui as pyag
import time
from create_macro import find_window_and_focus

# Delay between actions (in seconds)
PAUSE = 0.5

# Window name to focus on
windows_name = "F240003MC"

# Recorded points
"""
    # Embed points directly in script
    script_content += "all_points = " + json.dumps(points) + "\n\n"
    # Add named point definitions
    for point in points:
        if point[0] == 'click':
            script_content += f"{point[1]} = ('{point[0]}', {point[2]}, {point[3]})\n"
        elif point[0] == 'element':
            script_content += f"{point[1]} = ('{point[0]}', {point[2]}, {point[3]}, {point[4]}, {point[5]})\n"

    script_content += f"""
# Example macro using the first recorded point
def run_macro(repetitions=10, pause=PAUSE):
    if not all_points:
        print("No points to run.")
        return

    #first_point = all_points[0]
    for rep_idx in range(repetitions):
        # find_window_and_focus(windows_name)
        if {points[0]}[0] == 'click':
            pyag.moveTo(*{points[0][1]}[1:])
            pyag.click()
            print(f"Clicked on {points[0][1]} ({{rep_idx+1}}/{{repetitions}})")
            time.sleep(pause)

if __name__ == "__main__":
    run_macro(repetitions=200, pause=1.2)
"""

    with open("auto_script.py", "w") as f:
        f.write(script_content)

    print("\nScript generated as 'auto_script.py'")
    print("Ready to use!")

if __name__ == "__main__":
    main()