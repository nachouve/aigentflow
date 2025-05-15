# GUI dialog to alert user to do something
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Any

def show_dialog(title: str, message: str, parent: Optional[tk.Tk] = None,
               callback: Optional[Callable[[Any], None]] = None,
               button_text: str = "OK") -> None:
    """
    Show a dialog with a message and an OK button.

    Parameters:
        title (str): The title of the dialog.
        message (str): The message to display in the dialog.
        parent (Optional[tk.Tk]): The parent window for the dialog. If None, the dialog is not modal.
        callback (Optional[Callable[[Any], None]]): A callback function to call when the user clicks the button.
        button_text (str): The text to display on the button. Defaults to "OK".
    """
    if parent is None:
        parent = tk.Tk()
        parent.withdraw()  # Hide the root window

    def on_button_click():
        if callback:
            callback(None)
        if parent is not None:
            parent.destroy()

    messagebox.showinfo(title, message, parent=parent)
  
    