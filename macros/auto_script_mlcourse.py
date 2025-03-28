import pyautogui as pyag
import time

# Delay between actions (in seconds)
PAUSE = 0.5

# Recorded points
NEXT_BUTTON = (3413, 925)
NEXT_BUTTON_2 = (3402, 966)
PLAY_BUTTON = (2854, 609)

def run_macro(repetitions=10, pause=PAUSE):
    # Move to a point and click
    for _ in range(repetitions):
        pyag.moveTo(PLAY_BUTTON)
        pyag.click()
        time.sleep(pause*2)
        pyag.moveTo(NEXT_BUTTON)
        pyag.click()
        pyag.moveTo(NEXT_BUTTON_2)
        pyag.click()
        time.sleep(pause)
    
    # Example of finding element (if elements were recorded)
    # try:
    #     location = pyag.locateOnScreen('element.png', region=ELEMENT_1)
    #     if location:
    #         pyag.click(location)
    # except:
    #     print("Element not found")
    
    # Add more actions here as needed

if __name__ == "__main__":
    run_macro(200, pause=0.3)
