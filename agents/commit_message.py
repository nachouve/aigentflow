import os
import pyperclip
import sys
import io
import time
import argparse
import subprocess  # Added

class CommitMessage:
    def __init__(self, folder, chatmodel="Mistral"):
        self.name = "CommitMessage"
        
        if os.path.isdir(folder):
            os.chdir(folder)
            self.folder = folder
        else:
            raise Exception(f"Folder {folder} does not exist.")
        self.chatmodel = chatmodel

    def run(self, prompt, strings_to_find_in_win_titles=["Chrome"]):
        STATUS_CMD = ["git", "status", "--porcelain", "."]
        DIFF_CMD = ["git", "diff", "--no-color", "."]
        DEBUG = True

        # Use subprocess to capture output with correct encoding
        status_result = subprocess.run(STATUS_CMD, capture_output=True, text=True, encoding='utf-8')
        diff_result = subprocess.run(DIFF_CMD, capture_output=True, text=True, encoding='utf-8')

        status_txt = status_result.stdout if status_result.stdout else ""
        diff_txt = diff_result.stdout if diff_result.stdout else ""

        strings_to_find_in_win_titles.insert(0, self.chatmodel)
        
        prompt = f"""Here is the "git status" output:
        
```git_status
{status_txt}
```
        
And here is the "git diff" output: 
    
```git_diff	
{diff_txt}
```

Please review this information carefully. I need a clear and meaningful commit message written in "conventional commit" format.

Consider the changes and determine if they should be split into multiple commits for better organization. 
If so, provide a final summary listing the specific git commands for each commit along with its corresponding commit message (one per line).

Could you assist me in committing these changes? Provide only the final git commands in your response.
DO NOT explain that commands or give any additional justification. Just the final commands.

IMPORTANT: User is running the git commands in the folder:  "{self.folder}". So, please, adjust the paths accordingly in your response (use the fullpath in the commands, or just path from the folder used by the user) to avoid any error adding and commiting the changes in that folder.
Probably the user will execute the commands you provide in a terminal from that folder (do not assume that is the repo root).

"""
        
        if len(diff_txt) == 0:
            return "No changes to commit."
        
        import navwins_agent as nw
        import pyautogui
        
        manager = nw.get_window_manager()
        
        # Use a safer approach to list windows
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
                    # More delay for longer chunks
                    time.sleep(0.3)
                    
                    # Periodically check if we need to scroll down
                    if i > 0 and i % 10000 == 0:
                        pyautogui.press('pagedown')
                        time.sleep(0.2)
                
                return f"\nSuccessfully copied **{total_pasted} characters** to window.\n"
            except Exception as e:
                return f"Error while pasting text: {str(e)}"
        else:
            return f"Failed to find any suitable window. Searched for {strings_to_find_in_win_titles}\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default=None, help="Folder path to operate")
    parser.add_argument("--chatmodel", default="Mistral", help="Chat model to use")
    args = parser.parse_args()

    folder = args.folder
    if not folder:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory()
        if not folder:
            print("No folder selected.")
            sys.exit(1)
        print(f"Selected folder: {folder}")

    cm = CommitMessage(folder, chatmodel=args.chatmodel)
    print(cm.run(""))
