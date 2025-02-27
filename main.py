import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from modules import prompt_manager, action_manager, history_manager

def main():
    st.sidebar.title("AIgentFlow")
    menu = ["Prompts", "Actions", "History"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Prompts":
        prompt_manager.display_prompts()
    elif choice == "Actions":
        action_manager.display_actions()
    elif choice == "History":
        history_manager.display_history()

if __name__ == "__main__":
    main()
