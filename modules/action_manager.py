import streamlit as st
import json
from pathlib import Path
from utils.string_utils import decode_output
import subprocess

ACTION_DIR = Path(".aigentflow/actions")

def load_actions():
    actions = []
    for action_file in ACTION_DIR.glob("*.json"):
        with open(action_file, "r") as file:
            actions.append(json.load(file))
    return actions

def initialize_session_state():
    defaults = {
        "show_form": False,
        "edit_action": None,
        "show_variable_form": False,
        "variables": [],
        "action_name": None,
        "action_content": None,
        "execution_result": None,
        "execution_stdout": None,
        "execution_stderr": None,
        "execution_returncode": None,
        "executed_action_name": None,
        "execute_submit": False,
        "run_action": False,
        "variable_values": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def execute_action_test(action_name, content, variable_values):
    try:
        modified_content = content
        for var_name, var_value in variable_values.items():
            modified_content = modified_content.replace(f"<{var_name}>", str(var_value))
        # Your execution logic here
        st.session_state.execution_result = True
        st.session_state.executed_action_name = action_name
        st.session_state.execution_stdout = f"Action executed: {modified_content}"
        st.session_state.execution_returncode = 0
    except Exception as e:
        st.session_state.execution_result = True
        st.session_state.executed_action_name = action_name
        st.session_state.execution_stderr = str(e)
        st.session_state.execution_returncode = 1

def execute_action(action_name, content, variable_values):
    try:
        modified_content = content
        for var_name, var_value in variable_values.items():
            modified_content = modified_content.replace(f"<{var_name}>", str(var_value))
        
        # Execute the command
        result = subprocess.run(modified_content, shell=True, capture_output=True, text=True)
        
        st.session_state.execution_result = True
        st.session_state.executed_action_name = action_name
        st.session_state.execution_stdout = result.stdout
        st.session_state.execution_stderr = result.stderr
        st.session_state.execution_returncode = result.returncode
    except Exception as e:
        st.session_state.execution_result = True
        st.session_state.executed_action_name = action_name
        st.session_state.execution_stderr = str(e)
        st.session_state.execution_returncode = 1

def display_execution_results():
    if st.session_state.execution_result:
        output_text = f"Executed action [{st.session_state.executed_action_name}]\n\n OUTPUT (returncode={st.session_state.execution_returncode}):\n\n"
        if st.session_state.execution_returncode == 0:
            st.success(output_text)
            if st.session_state.execution_stdout and st.session_state.execution_stdout.strip():
                st.success(st.session_state.execution_stdout)
            else:
                st.info("Command executed successfully but produced no output.")
        else:
            st.error(output_text)
            st.error(st.session_state.execution_stderr)
        if st.button("Clear Results", key="clear_results"):
            for key in ["execution_result", "execution_stdout", "execution_stderr", "execution_returncode", "executed_action_name"]:
                st.session_state[key] = None
            st.rerun()
    else:
        st.info("No action results to display. Execute an action to see results here.")

def display_action_form(action=None):
    if action:
        st.header("Edit Action")
        action_name = st.text_input("Action Name", value=action["name"])
        action_content = st.text_area("Action Content (use <variable_name> for variables)", value=action["content"])
        variables = st.session_state.variables or action["variables"]
    else:
        st.header("Create New Action")
        action_name = st.text_input("Action Name")
        action_content = st.text_area("Action Content (use <variable_name> for variables)")
        variables = st.session_state.variables

    if st.session_state.show_variable_form:
        display_variable_form(variables)
    
    if st.button("New Variable", key="action_new_variable"):
        st.session_state.show_variable_form = True

    for var in variables:
        with st.expander(f"Variable: {var['name']}({var['type']})"):
            st.write(f"Type: {var['type']}")
            st.write(f"Default: {var['default']}")
            if var["type"] == "options":
                st.write(f"Options: {', '.join(var['options'])}")
            if st.button("Edit Variable", key=f"edit_var_{var['name']}"):
                st.session_state.show_variable_form = True
                st.session_state.variables.remove(var)
                st.session_state.edit_var = var
            if st.button("Delete Variable", key=f"delete_var_{var['name']}"):
                st.session_state.variables.remove(var)

    if action:
        if st.button("Update and Save"):
            action["name"] = action_name
            action["content"] = action_content
            action["variables"] = variables
            safe_action_name = "".join([c if c.isalnum() else "_" for c in action_name])
            with open(ACTION_DIR / f"{safe_action_name}.json", "w") as file:
                json.dump(action, file)
            st.success("Action updated successfully!")
            st.session_state.show_form = False
            st.session_state.edit_action = None
            st.session_state.variables = []
    else:
        if st.button("Save Action"):
            new_action = {
                "name": action_name,
                "content": action_content,
                "variables": variables
            }
            ACTION_DIR.mkdir(parents=True, exist_ok=True)
            safe_action_name = "".join([c if c.isalnum() else "_" for c in action_name])
            with open(ACTION_DIR / f"{safe_action_name}.json", "w") as file:
                json.dump(new_action, file)
            st.success("Action saved successfully!")
            st.session_state.show_form = False
            st.session_state.variables = []

    if action_content:
        st.subheader("Preview")
        preview_content = action_content
        for var in variables:
            preview_content = preview_content.replace(f"<{var['name']}>", var['default'])
        st.write(preview_content)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", key="cancel_action_form"):
            st.session_state.show_form = False
            st.session_state.edit_action = None
            st.session_state.variables = []
    with col2:
        if st.button("Execute", key="execute_action_form"):
            st.session_state.execute_submit = True
            st.session_state.action_name = action_name
            st.session_state.action_content = action_content
            st.session_state.variables = variables

def display_variable_form(variables):
    if "edit_var" in st.session_state and st.session_state.edit_var:
        var_name = st.text_input("Variable Name", value=st.session_state.edit_var["name"])
        var_type = st.selectbox("Variable Type", ["text", "number", "date", "options"], index=["text", "number", "date", "options"].index(st.session_state.edit_var.get("type", "text")))
        if var_type == "options":
            var_options = st.text_area("Options (one per line)", value="\n".join(st.session_state.edit_var.get("options", [])))
            var_default = st.selectbox("Default Option", options=var_options.split("\n") if var_options else [""], index=0 if not var_options else var_options.split("\n").index(st.session_state.edit_var.get("default", "")) if st.session_state.edit_var.get("default", "") in var_options.split("\n") else 0)
        else:
            var_default = st.text_input("Default Value", value=st.session_state.edit_var.get("default", ""))
            var_options = []
    else:
        var_name = st.text_input("Variable Name")
        var_type = st.selectbox("Variable Type", ["text", "number", "date", "options"])
        if var_type == "options":
            var_options = st.text_area("Options (one per line)")
            options_list = var_options.split("\n") if var_options else [""]
            var_default = st.selectbox("Default Option", options=options_list, index=0)
        else:
            var_default = st.text_input("Default Value")
            var_options = []

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add/Update Variable", key="add_update_variable"):
            if var_type == "options":
                variables.append({
                    "name": var_name,
                    "type": var_type,
                    "default": var_default,
                    "options": var_options.split("\n") if var_options else []
                })
            else:
                variables.append({
                    "name": var_name,
                    "type": var_type,
                    "default": var_default
                })
            st.session_state.show_variable_form = False
            st.session_state.edit_var = None
    with col2:
        if st.button("Cancel", key="cancel_variable_form"):
            st.session_state.show_variable_form = False
            st.session_state.edit_var = None

def display_actions():
    st.title("Actions")
    actions = load_actions()
    initialize_session_state()

    if st.session_state.run_action:
        st.error(f"Debug: Form submit flag is {st.session_state.execute_submit}")
        st.error(f"Action content: {st.session_state.action_content}")
        variable_values = {key[4:]: st.session_state[key] for key in st.session_state.keys() if key.startswith("var_")}
        execute_action(st.session_state.action_name, st.session_state.action_content, variable_values)
        st.session_state.run_action = False 
        st.rerun()

    display_execution_results()

    if st.session_state.show_form:
        display_action_form(st.session_state.edit_action)
    else:
        st.button("New Action", on_click=lambda: setattr(st.session_state, 'show_form', True), key="new_action")
        st.header("Existing Actions")
        if actions:
            for action in actions:
                with st.expander(action["name"]):
                    description = action.get("description", action["content"][:200])
                    st.write(description)
                    if st.button("Edit", key=f"edit_{action['name']}"):
                        st.session_state.show_form = True
                        st.session_state.edit_action = action
                        st.session_state.variables = action["variables"]
                    if st.button("Execute", key=f"execute_{action['name']}"):
                        st.session_state.execute_submit = True
                        st.session_state.action_name = action["name"]
                        st.session_state.action_content = action["content"]
                        st.session_state.variables = action["variables"]
        else:
            st.write("No actions found.")

    if st.session_state.execute_submit:
        action_name = st.session_state.action_name
        content = st.session_state.action_content
        st.subheader(f"Execute Action: {action_name}")
        with st.form(key="execute_action_form"):
            variable_values = {}
            for var in st.session_state.variables:
                if var["type"] == "text":
                    variable_values[var["name"]] = st.text_input(f"{var['name']}", value=var["default"])
                elif var["type"] == "number":
                    variable_values[var["name"]] = st.number_input(f"{var['name']}", value=float(var["default"]) if var["default"] else 0)
                elif var["type"] == "date":
                    variable_values[var["name"]] = st.date_input(f"{var['name']}")
                elif var["type"] == "options":
                    options = var.get("options", [])
                    default_idx = options.index(var["default"]) if var["default"] in options else 0
                    variable_values[var["name"]] = st.selectbox(f"{var['name']}", options=options, index=default_idx)
            if st.form_submit_button("Run Action"):
                for key, value in variable_values.items():
                    st.session_state[f"var_{key}"] = value
                st.session_state.run_action = True
                st.session_state.action_content = content
                st.session_state.action_name = action_name
                st.rerun()

#display_actions()
