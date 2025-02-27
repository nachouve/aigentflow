import pyperclip
import sys
import io
import time
import argparse
import pyautogui

import navwins_agent as nw

DEBUG =True


def paste_text_in_window(prompt, window):
    time.sleep(0.3)
    nw.go_down_and_click(window)
    
    # For large diffs, use more reliable chunking
    chunk_size = 2000  # Smaller chunks for better reliability
    total_pasted = 0
    
    try:
        # Clear any existing text
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        
        for i in range(0, len(prompt), chunk_size):
            chunk = prompt[i:i+chunk_size]
            pyperclip.copy(chunk)
            pyautogui.hotkey('ctrl', 'v')
            total_pasted += len(chunk)
            time.sleep(0.3)
            
            # Periodically check if we need to scroll down
            if i > 0 and i % 10000 == 0:
                pyautogui.press('pagedown')
                time.sleep(0.2)
        
        return f"Successfully copied **{total_pasted} characters** to window.\n"
    except Exception as e:
        return f"Error while pasting text: {str(e)}"
    

def run(prompt, chatmodel="Mistral"): 
    
    strings_to_find_in_win_titles = [chatmodel, "Chrome"]
    
    manager = nw.get_window_manager()
    
    # Use a safer approach to list windows
    # TODO move to navwins_agent
    def safe_print(text, fallback="[Content cannot be displayed]"):
        try:
            # Try to print to string first to catch encoding issues
            test_buf = io.StringIO()
            print(text, file=test_buf)
            test_buf.close()
            # If that worked, print to actual stdout
            print(text)
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            print(fallback)
            return False
    
    # List all windows with better error handling
    print("Available windows:")
    window_list = manager.list_windows()
    for i, window_title in enumerate(window_list):
        safe_print(f"[{i}]: {window_title}\n")
    
    success, window = manager.activate_window(title_must_contain=strings_to_find_in_win_titles)
    if not success:
        # Try multiple search strings for better results
        for search_terms in [strings_to_find_in_win_titles]:
            if DEBUG: print(f"Trying to find window with: {search_terms}")
            success, window = manager.activate_window(title_must_contain=search_terms)
            if success:
                break
    
    if DEBUG: print(f"Window activated: {success}")
    
    if success:
        # Give window time to focus
        output = paste_text_in_window(prompt, window)
        print(output)
        pyautogui.press('enter')
    else:
        return f"Failed to find any suitable window. Searched for {strings_to_find_in_win_titles}\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hello! I need some help.", help="Prompt to use")
    parser.add_argument("--chatmodel", default="Mistral", help="Chat model to use")
    args = parser.parse_args()

    run(prompt=args.prompt, chatmodel=args.chatmodel)