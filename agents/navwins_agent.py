import logging
import platform
import sys
from abc import ABC, abstractmethod

import pyautogui

# Configure console to use UTF-8 encoding
if platform.system() == "Windows":
    import os

    os.system("chcp 65001 >nul")  # Set console to UTF-8 mode
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)


class WindowManager(ABC):
    @abstractmethod
    def list_windows(self):
        """List all open windows"""
        pass

    @abstractmethod
    def activate_window(self, title_name=None, title_must_contain=[], ignore_case=True):
        """Activate a window based on title criteria"""
        pass

    def _matches_criteria(
        self, window_title, title_name, title_must_contain, ignore_case
    ):
        window_title = window_title.upper() if ignore_case else window_title
        if (
            title_name
            and (title_name.upper() if ignore_case else title_name) in window_title
        ):
            return True
        if title_must_contain and all(
            (title.upper() if ignore_case else title) in window_title
            for title in title_must_contain
        ):
            return True
        return False


class WindowsManager(WindowManager):
    def __init__(self):
        try:
            import pygetwindow as gw

            self.gw = gw
        except ImportError:
            logger.error("pygetwindow not installed. Run: pip install pygetwindow")
            raise

    def list_windows(self):
        return [window.title for window in self.gw.getAllWindows()]

    def activate_window(self, title_name=None, title_must_contain=[], ignore_case=True):
        for window in self.gw.getAllWindows():
            if self._matches_criteria(
                window.title, title_name, title_must_contain, ignore_case
            ):
                window.activate()
                return True, window
        return False, None


class LinuxManager(WindowManager):
    def __init__(self):
        try:
            import ewmh

            self.ewmh = ewmh.EWMH()
        except ImportError:
            logger.error("ewmh not installed. Run: pip install ewmh")
            raise

    def list_windows(self):
        return self.ewmh.getClientList()

    def activate_window(self, title_name=None, title_must_contain=[], ignore_case=True):
        for window in self.ewmh.getClientList():
            if self._matches_criteria(
                window, title_name, title_must_contain, ignore_case
            ):
                self.ewmh.setActiveWindow(window)
                return True, window
        return False, window


class MacManager(WindowManager):
    def __init__(self):
        try:
            import appscript

            self.appscript = appscript
        except ImportError:
            logger.error("appscript not installed. Run: pip install appscript")
            raise

    def list_windows(self):
        return (
            self.appscript.app("System Events").processes.whose(visible=True).name.get()
        )

    def activate_window(self, title_name=None, title_must_contain=[], ignore_case=True):
        for window in self.list_windows():
            if self._matches_criteria(
                window, title_name, title_must_contain, ignore_case
            ):
                self.appscript.app("System Events").processes[window].windows[0].focus()
                return True, window
        return False, None


def get_window_manager():
    os_type = platform.system()
    if os_type == "Windows":
        return WindowsManager()
    elif os_type == "Linux":
        return LinuxManager()
    elif os_type == "Darwin":
        return MacManager()
    else:
        raise NotImplementedError(f"Unsupported OS: {os_type}")


def safe_print_title(index, title):
    """Safely print window title regardless of special characters."""
    try:
        print(f"- [{index}]: {title}")
    except UnicodeEncodeError:
        # If we still have encoding issues, try to print as raw representation
        try:
            print(f"- [{index}]: {repr(title)}")
        except:
            print(f"- [{index}]: <Unprintable window title>")
    except Exception as e:
        print(f"- [{index}]: Error reading window title ({str(e)})")


def go_down_and_click(window, down_num=20, pixel_from_bottom=100):
    try:
        window.activate()
    except:
        print(f"Error activating window: {window.title if window else 'None'}")
        return

    ## press adv page
    [pyautogui.press("pagedown") for i in range(down_num)]
    # calculate 50 pixels in the bottom of the window activated
    right_bottom = (
        window.left + window.width // 2,
        window.top + window.height - pixel_from_bottom,
    )
    pyautogui.moveTo(*right_bottom)
    pyautogui.click()


if __name__ == "__main__":
    import sys

    DEBUG = False
    print(f"syst.argv: {sys.argv}")
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            DEBUG = True
            ## IMPORTANT It returns the window with the first string found.
            ##     If executing this script from the command line, maybe the title of the terminal is the first one found.
            strings_to_find = input(
                "Enter the strings to find separated by comma: "
            ).split(",")
    else:
        strings_to_find = ["Google Chrome", "Deepseek"]

    manager = get_window_manager()

    if DEBUG:
        print("Open Windows:")
    for i, win_name in enumerate(manager.list_windows(), start=1):
        safe_print_title(i, win_name)

    if DEBUG:
        print(f"Let's activate a window with titles containing {strings_to_find}")
    success, window = manager.activate_window(title_must_contain=strings_to_find)
    if DEBUG:
        print(f"Window activated: {success}")
    go_down_and_click(window)
    pyautogui.typewrite("Hello World")
    # pyautogui.press('enter')
