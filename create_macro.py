import pyautogui as pyag
import time
import os

def main():
    recorded_points = []
    
    while True:
        print("\n--- Main Menu ---")
        print("1) Record XY position")
        print("2) Record screen element (without cursor)")
        print("3) Exit and generate script")
        
        option = input("Select an option: ")
        
        if option == "1":
            record_xy(recorded_points)
        elif option == "2":
            record_element(recorded_points)
        elif option == "3":
            show_points(recorded_points)
            generate_script(recorded_points)
            break
        else:
            print("Invalid option. Please try again.")

def record_xy(points):
    print("\nMove cursor to desired position and press 's' to record.")
    print("Press 'q' to cancel.")
    
    while True:
        x, y = pyag.position()
        print(f"Current position: X={x}, Y={y}", end="\r")
        
        if pyag.keyDown('s'):
            points.append(('click', x, y))
            print(f"\nPoint recorded: X={x}, Y={y}")
            time.sleep(0.3)  # Small delay to avoid multiple recordings
            break
        elif pyag.keyDown('q'):
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
            points.append(('element', x, y, w, h))
            print(f"Element recorded: X={x}, Y={y}, Width={w}, Height={h}")
    except Exception as e:
        print(f"Failed to record element: {e}")

def show_points(points):
    print("\n--- Recorded Points ---")
    for i, point in enumerate(points, 1):
        if point[0] == 'click':
            print(f"{i}) Click at X={point[1]}, Y={point[2]}")
        elif point[0] == 'element':
            print(f"{i}) Element at X={point[1]}, Y={point[2]}, Width={point[3]}, Height={point[4]}")

def generate_script(points):
    script_content = """import pyautogui as pyag
import time

# Delay between actions (in seconds)
PAUSE = 0.5

# Recorded points
"""
    
    # Add recorded points to the script
    for i, point in enumerate(points, 1):
        if point[0] == 'click':
            script_content += f"POINT_{i} = ({point[1]}, {point[2]})\n"
        elif point[0] == 'element':
            script_content += f"ELEMENT_{i} = ({point[1]}, {point[2]}, {point[3]}, {point[4]})\n"
    
    script_content += """
# Example macro using recorded points
def run_macro():
    # Move to a point and click
    pyag.moveTo(POINT_1)
    pyag.click()
    time.sleep(PAUSE)
    
    # Example of finding element (if elements were recorded)
    # try:
    #     location = pyag.locateOnScreen('element.png', region=ELEMENT_1)
    #     if location:
    #         pyag.click(location)
    # except:
    #     print("Element not found")
    
    # Add more actions here as needed

if __name__ == "__main__":
    run_macro()
"""
    
    with open("auto_script.py", "w") as f:
        f.write(script_content)
    
    print("\nScript generated as 'auto_script.py'")
    print("Ready to use!")

if __name__ == "__main__":
    main()