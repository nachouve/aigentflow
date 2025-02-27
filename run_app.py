# run_app.py
import os
import subprocess
import sys

# Set the working directory to the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
print(sys.path)

# Run the Streamlit app
subprocess.run(["streamlit", "run", "main.py"])