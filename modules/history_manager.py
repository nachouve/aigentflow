import streamlit as st
import json
from pathlib import Path

HISTORY_DIR = Path(".aigentflow/history")

def load_history():
    history = []
    for history_file in HISTORY_DIR.glob("*.json"):
        with open(history_file, "r") as file:
            history.append(json.load(file))
    return history

def display_history():
    st.title("History")
    history = load_history()
    for record in history:
        st.write(record)
