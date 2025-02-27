import streamlit as st
import json
from pathlib import Path

PROMPT_DIR = Path(".aigentflow/prompts")

def load_prompts():
    prompts = []
    for prompt_file in PROMPT_DIR.glob("*.json"):
        with open(prompt_file, "r") as file:
            prompts.append(json.load(file))
    return prompts

def initialize_session_state():
    defaults = {
        "show_form": False,
        "edit_prompt": None,
        "show_variable_form": False,
        "variables": [],
        "prompt_name": None,
        "prompt_content": None,
        "execute_submit": False,
        "run_prompt": False,
        "variable_values": {},
        "action": None,
        "target_variable": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def prepare_prompt(prompt_content, variable_values, action=None, target_variable=None):
    content = prompt_content
    for var_name, var_value in variable_values.items():
        content = content.replace(f"<{var_name}>", str(var_value))
    return content    

def display_prompt_form(prompt=None):
    if prompt:
        st.header("Edit Prompt")
        prompt_name = st.text_input("Prompt Name", value=prompt["name"])
        prompt_content = st.text_area("Prompt Content (use <variable_name> for variables)", value=prompt["content"])
        variables = st.session_state.variables or prompt["variables"]
    else:
        st.header("Create New Prompt")
        prompt_name = st.text_input("Prompt Name")
        prompt_content = st.text_area("Prompt Content (use <variable_name> for variables)")
        variables = st.session_state.variables

    if st.session_state.show_variable_form:
        display_variable_form(variables)
    
    if st.button("New Variable", key="prompt_new_variable"):
        st.session_state.show_variable_form = True

    for var in variables:
        with st.expander(f"Variable: {var['name']}({var['type']})"):
            st.write(f"Type: {var['type']}")
            st.write(f"Default: {var['default']}")
            if st.button("Edit Variable", key=f"edit_var_{var['name']}"):
                st.session_state.show_variable_form = True
                st.session_state.variables.remove(var)
                st.session_state.edit_var = var
            if st.button("Delete Variable", key=f"delete_var_{var['name']}"):
                st.session_state.variables.remove(var)

    action = st.selectbox("Action", ["Show in Window", "Use as Input"])
    target_variable = None
    available_actions = ["Action1", "Action2"]  # Replace with actual actions
    if action == "Use as Input":
        selected_action = st.selectbox("Select Action", available_actions)
        target_variable = st.selectbox("Target Variable", ["var1", "var2"])  # Replace with actual variables

    if prompt:
        if st.button("Update and Save"):
            prompt["name"] = prompt_name
            prompt["content"] = prompt_content
            prompt["variables"] = variables
            with open(PROMPT_DIR / f"{prompt_name}.json", "w") as file:
                json.dump(prompt, file)
            st.success("Prompt updated successfully!")
            st.session_state.show_form = False
            st.session_state.edit_prompt = None
            st.session_state.variables = []
    else:
        if st.button("Save Prompt"):
            new_prompt = {
                "name": prompt_name,
                "content": prompt_content,
                "variables": variables
            }
            PROMPT_DIR.mkdir(parents=True, exist_ok=True)
            with open(PROMPT_DIR / f"{prompt_name}.json", "w") as file:
                json.dump(new_prompt, file)
            st.success("Prompt saved successfully!")
            st.session_state.show_form = False
            st.session_state.variables = []

    if prompt_content:
        st.subheader("Preview")
        preview_content = prompt_content
        for var in variables:
            preview_content = preview_content.replace(f"<{var['name']}>", var['default'])
        st.write(preview_content)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", key="cancel_prompt_form"):
            st.session_state.show_form = False
            st.session_state.edit_prompt = None
            st.session_state.variables = []
    with col2:
        if st.button("Execute", key="execute_prompt_form"):
            st.session_state.execute_submit = True
            st.session_state.prompt_name = prompt_name
            st.session_state.prompt_content = prompt_content
            st.session_state.variables = variables
            st.session_state.action = action
            st.session_state.target_variable = target_variable

def display_variable_form(variables):
    if "edit_var" in st.session_state and st.session_state.edit_var:
        var_name = st.text_input("Variable Name", value=st.session_state.edit_var["name"])
        var_type = st.selectbox("Variable Type", ["text", "number", "date"], index=["text", "number", "date"].index(st.session_state.edit_var["type"]))
        var_default = st.text_input("Default Value", value=st.session_state.edit_var["default"])
    else:
        var_name = st.text_input("Variable Name")
        var_type = st.selectbox("Variable Type", ["text", "number", "date"])
        var_default = st.text_input("Default Value")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add/Update Variable", key="add_update_variable"):
            variables.append({"name": var_name, "type": var_type, "default": var_default})
            st.session_state.show_variable_form = False
            st.session_state.edit_var = None
    with col2:
        if st.button("Cancel", key="cancel_variable_form"):
            st.session_state.show_variable_form = False
            st.session_state.edit_var = None

def display_prompts():
    st.title("Prompts")
    prompts = load_prompts()
    initialize_session_state()

    if st.session_state.run_prompt: # and st.session_state.action_type == "Show in Window":
        variable_values = st.session_state.variable_values
        content = prepare_prompt(st.session_state.prompt_content, variable_values, st.session_state.action, st.session_state.target_variable)
        st.info(content)
        st.session_state.run_prompt = False
        
        if st.session_state.run_prompt and st.session_state.action_type == "Use as Input":
            st.error("Action not implemented yet.")
            
    if st.session_state.show_form:
        display_prompt_form(st.session_state.edit_prompt)
    else:
        st.button("New Prompt", on_click=lambda: setattr(st.session_state, 'show_form', True), key="pr_new_prompt")
        st.header("Existing Prompts")
        if prompts:
            for idx, prompt in enumerate(prompts):
                with st.expander(prompt["name"]):
                    description = prompt.get("description", prompt["content"][:200])
                    st.write(description)
                    if st.button("Edit", key=f"edit_{prompt['name']}_{idx}"):
                        st.session_state.show_form = True
                        st.session_state.edit_prompt = prompt
                        st.session_state.variables = prompt["variables"]
                    if st.button("Execute", key=f"execute_{prompt['name']}_{idx}"):
                        st.session_state.execute_submit = True
                        st.session_state.prompt_name = prompt["name"]
                        st.session_state.prompt_content = prompt["content"]
                        st.session_state.variables = prompt["variables"]
        else:
            st.write("No prompts found.")

    if st.session_state.execute_submit:
        prompt_name = st.session_state.prompt_name
        content = st.session_state.prompt_content
        action_type = st.session_state.action
        target_variable = st.session_state.target_variable
        st.subheader(f"Execute Prompt: {prompt_name}")
        with st.form(key="execute_prompt_form"):
            variable_values = {}
            for var in st.session_state.variables:
                if var["type"] == "text":
                    variable_values[var["name"]] = st.text_input(f"{var['name']}", value=var["default"])
                elif var["type"] == "number":
                    variable_values[var["name"]] = st.number_input(f"{var['name']}", value=float(var["default"]) if var["default"] else 0)
                elif var["type"] == "date":
                    variable_values[var["name"]] = st.date_input(f"{var['name']}")
            action_type = st.selectbox("Action", ["Show in Window", "Use as Input"])
            target_variable = None
            from .action_manager import load_actions
            actions = load_actions()
            available_actions = [action["name"] for action in actions]
            if action_type == "Use as Input":
                selected_action = st.selectbox("Select Action", available_actions)
                if selected_action:
                    action_obj = [act for act in actions if act["name"] == selected_action][0]
                    possible_variables = [var["name"] for var in action_obj["variables"]]
                    if possible_variables:
                        target_variable = st.selectbox("Target Variable", possible_variables)
            if st.form_submit_button("Run Prompt"):
                for key, value in variable_values.items():
                    st.session_state[f"var_{key}"] = value
                st.session_state.run_prompt = True
                st.session_state.prompt_content = content
                st.session_state.prompt_name = prompt_name
                st.session_state.action_type = action_type
                st.session_state.variable_values = variable_values
                if action_type == "Use as Input":
                    st.session_state.action = selected_action
                    st.session_state.target_variable = target_variable
                else:
                    st.session_state.action = None
                    st.session_state.target_variable = None
                if action_type == "Show in Window":
                    st.info(content)  # Ensure content is shown immediately
                st.rerun()

#display_prompts()