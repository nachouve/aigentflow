import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import reflex as rx

# (Keep .aigentflow at the root, so paths will be relative from there)
ACTION_DIR = Path(".aigentflow/actions")
# PROMPT_DIR = Path(".aigentflow/prompts") # Will be used later
# HISTORY_DIR = Path(".aigentflow/history") # Will be used later
PROMPT_DIR = Path(".aigentflow/prompts")
HISTORY_DIR = Path(".aigentflow/history")
# These paths will be used later when implementing file I/O logic.


class Variable(rx.Base):
    name: str = ""
    type: str = "text"  # e.g., text, number, date, options
    default: str = ""
    options: List[str] = []


class AppState(rx.State):
    current_view: str = "Actions"  # "Actions", "Prompts", "History"

    show_action_form: bool = False
    editing_action_name: Optional[str] = None

    show_prompt_form: bool = False
    editing_prompt_name: Optional[str] = None

    show_variable_form: bool = (
        False  # For managing variables within action/prompt forms
    )

    def set_current_view(self, view: str):
        """Set the current view - replaces rx.set_val functionality"""
        self.current_view = view

    def set_show_variable_form(self, show: bool):
        """Set whether to show the variable form dialog"""
        self.show_variable_form = show

    def show_variable_form_dialog(self):
        """Show the variable form dialog"""
        self.show_variable_form = True

    def hide_variable_form_dialog(self):
        """Hide the variable form dialog"""
        self.show_variable_form = False

    # current_variable_being_edited: Optional[Dict] = None # To store variable data when editing it. Using Dict as per instruction, can refine to Variable later if needed.
    # The example snippet had current_variable_being_edited, but subtask point 1 did not explicitly list it under AppState.
    # Will add it if form logic dictates it's needed at AppState level, otherwise it might be local to Action/Prompt states if variable editing is tied to them.
    # For now, keeping AppState lean as per explicit requirements.


class ActionState(AppState):
    actions: List[Dict] = []
    actions_loaded: bool = False

    # current_action_data: dict to hold data for a new or edited action
    # This will be represented by individual fields for clarity in form binding
    action_name: str = ""
    action_content: str = ""
    action_variables: List[
        Dict
    ]  # As per subtask item 2: "action_variables: list[dict]"

    # For executing an action and displaying results
    action_to_execute_name: Optional[str] = None
    action_to_execute_content: Optional[str] = None
    action_to_execute_variables: List[
        Dict
    ]  # Storing as list of dicts, can be converted to Variable objects if needed at execution time
    action_variable_values: Dict[
        str, str
    ] = {}  # Stores user-provided values for variables for execution

    action_execution_result: Dict = {}  # As per subtask item 2. To store stdout, stderr, returncode.
    show_action_execution_results: bool = False

    # Add individual execution result fields for easier access
    action_execution_stdout: str = ""
    action_execution_stderr: str = ""
    action_execution_returncode: Optional[int] = None

    # For action forms (create/edit)
    # action_name, action_content, action_variables are already defined above for current_action_data
    editing_action_original_name: Optional[str] = None
    current_variable_data: Dict = {
        "name": "",
        "type": "text",
        "default": "",
        "options": "",
    }  # options as comma-separated string

    # For delete confirmation
    show_delete_action_dialog: bool = False
    action_to_delete_name: Optional[str] = None

    def prepare_new_action_form(self):
        self.action_name = ""
        self.action_content = ""
        self.action_variables = []
        self.editing_action_original_name = None
        self.current_variable_data = {
            "name": "",
            "type": "text",
            "default": "",
            "options": "",
        }
        self.show_variable_form = False  # Ensure variable form is hidden
        self.show_action_form = True
        self.current_view = "Action Form"  # Or a more specific view like "New Action"

    async def prepare_edit_action_form(self, action_name_to_edit: str):
        async with self:
            # Ensure actions are loaded if not already
            if not self.actions:
                await self.load_actions()  # Assuming load_actions is an async method

            action_to_edit = next(
                (
                    action
                    for action in self.actions
                    if action.get("name") == action_name_to_edit
                ),
                None,
            )
            if action_to_edit:
                self.action_name = action_to_edit.get("name", "")
                self.action_content = action_to_edit.get("content", "")
                # Ensure variables are loaded correctly, handling potential format differences if any
                loaded_vars = action_to_edit.get("variables", [])
                self.action_variables = [
                    {
                        "name": v.get("name", ""),
                        "type": v.get("type", "text"),
                        "default": v.get("default", ""),
                        "options": v.get("options", []),
                    }
                    for v in loaded_vars
                ]
                self.editing_action_original_name = action_name_to_edit
                self.current_variable_data = {
                    "name": "",
                    "type": "text",
                    "default": "",
                    "options": "",
                }
                self.show_variable_form = False
                self.show_action_form = True
                self.current_view = "Action Form"  # Or "Edit Action"
            else:
                print(f"Error: Action '{action_name_to_edit}' not found for editing.")
                # Optionally, set an error message state variable to display in UI

    def add_variable_to_action(self):
        var_name = self.current_variable_data.get("name", "").strip()
        var_type = self.current_variable_data.get("type", "text")
        if not var_name:
            # TODO: Add user-facing error (e.g., toast or message)
            print("Error: Variable name cannot be empty.")
            return

        # Check for duplicate variable names
        if any(v["name"] == var_name for v in self.action_variables):
            # TODO: Add user-facing error
            print(f"Error: Variable '{var_name}' already exists.")
            return

        new_var = {
            "name": var_name,
            "type": var_type,
            "default": self.current_variable_data.get("default", ""),
            "options": [],
        }
        if var_type == "options":
            options_str = self.current_variable_data.get("options", "")
            new_var["options"] = [
                opt.strip() for opt in options_str.split(",") if opt.strip()
            ]

        self.action_variables.append(new_var)
        self.current_variable_data = {
            "name": "",
            "type": "text",
            "default": "",
            "options": "",
        }  # Reset form
        self.show_variable_form = False

    def remove_variable_from_action(self, variable_name: str):
        self.action_variables = [
            v for v in self.action_variables if v.get("name") != variable_name
        ]

    async def save_action(self):
        async with self:
            if not self.action_name.strip():
                # TODO: Add user-facing error (e.g., via a state var for a toast/alert)
                print("Error: Action name cannot be empty.")
                return

            action_data_to_save = {
                "name": self.action_name.strip(),
                "content": self.action_content,
                "variables": self.action_variables,
            }

            # Sanitize action_name for filename
            safe_action_name = "".join(
                [c if c.isalnum() else "_" for c in self.action_name.strip()]
            )
            filename = ACTION_DIR / f"{safe_action_name}.json"

            # Handle renaming: If editing_action_original_name exists and is different from current sanitized name
            if self.editing_action_original_name:
                safe_original_name = "".join(
                    [
                        c if c.isalnum() else "_"
                        for c in self.editing_action_original_name
                    ]
                )
                original_filename = ACTION_DIR / f"{safe_original_name}.json"
                if original_filename != filename and original_filename.exists():
                    original_filename.unlink()

            if not ACTION_DIR.exists():
                ACTION_DIR.mkdir(parents=True, exist_ok=True)

            with open(filename, "w") as f:
                json.dump(action_data_to_save, f, indent=4)

            # Reset form state
            self.show_action_form = False
            self.show_variable_form = False
            self.action_name = ""
            self.action_content = ""
            self.action_variables = []
            self.editing_action_original_name = None
            self.current_variable_data = {
                "name": "",
                "type": "text",
                "default": "",
                "options": "",
            }
            self.current_view = "Actions"  # Switch back to the actions list view

        await self.load_actions()  # Reload actions to reflect changes

    def cancel_action_form(self):
        self.show_action_form = False
        self.show_variable_form = False
        self.action_name = ""
        self.action_content = ""
        self.action_variables = []
        self.editing_action_original_name = None
        self.current_variable_data = {
            "name": "",
            "type": "text",
            "default": "",
            "options": "",
        }
        self.current_view = "Actions"  # Switch back

    # Action Execution State Variables (ensure they are here, some might be repeats from above but ensure defaults)
    # action_to_execute_name, action_to_execute_content, action_to_execute_variables, action_variable_values,
    # action_execution_stdout, action_execution_stderr, action_execution_returncode, show_action_execution_results
    # were largely defined in previous steps. Confirming and adding show_action_execution_form.
    show_action_execution_form: bool = False

    # Helper methods for form input bindings
    def set_action_name(self, name: str):
        self.action_name = name

    def set_action_content(self, content: str):
        self.action_content = content

    def set_current_variable_data_item(self, key: str, value: str):
        self.current_variable_data[key] = value

    def reset_current_variable_data(self):
        self.current_variable_data = {
            "name": "",
            "type": "text",
            "default": "",
            "options": "",
        }
        # self.show_variable_form = False # Optionally control visibility here too

    # Event handlers for Action Execution
    def prepare_action_execution(self, action: Dict):
        self.action_to_execute_name = action.get("name", "Unknown Action")
        self.action_to_execute_content = action.get("content", "")
        variables_for_execution = action.get("variables", [])
        self.action_to_execute_variables = variables_for_execution

        # Initialize action_variable_values with defaults
        self.action_variable_values = {
            var.get("name"): var.get("default", "")
            for var in variables_for_execution
            if var.get("name")
        }

        # Clear previous results
        self.action_execution_stdout = ""
        self.action_execution_stderr = ""
        self.action_execution_returncode = None

        self.show_action_execution_form = True
        self.show_action_execution_results = False
        # self.current_view = "Execute Action" # Optionally change main view or handle via modal

    def set_action_variable_value(self, var_name: str, value: str):
        self.action_variable_values[var_name] = value

    async def execute_action(self):
        async with self:
            if self.action_to_execute_content is None:
                self.action_execution_stderr = "Error: No action content to execute."
                self.action_execution_returncode = -1
                self.show_action_execution_results = True
                self.show_action_execution_form = False
                return

            modified_content = self.action_to_execute_content
            for var_name, var_value in self.action_variable_values.items():
                # Ensure var_value is a string, especially if it might be None or other types
                str_var_value = str(var_value) if var_value is not None else ""
                # Basic shell safety for variable values injected into commands
                # Replace double quotes with single quotes to prevent breaking out of string literals in many shell contexts
                # More robust shell escaping might be needed for complex scenarios (e.g., using `shlex.quote`)
                # but for simple placeholder replacement, this is a common first step.
                safe_var_value = str_var_value.replace('"', "'")
                modified_content = modified_content.replace(
                    f"<{var_name}>", safe_var_value
                )

            self.action_execution_stdout = ""  # Clear previous stdout
            self.action_execution_stderr = ""  # Clear previous stderr

            try:
                # Using import subprocess inside the method as it's a background task

                result = subprocess.run(
                    modified_content,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.action_execution_stdout = result.stdout
                self.action_execution_stderr = result.stderr
                self.action_execution_returncode = result.returncode
            except FileNotFoundError as e:  # Specific error for command not found
                self.action_execution_stderr = (
                    f"Error: Command not found or path is incorrect. Details: {str(e)}"
                )
                self.action_execution_returncode = (
                    e.errno if hasattr(e, "errno") else -1
                )
            except PermissionError as e:  # Specific error for permission issues
                self.action_execution_stderr = f"Error: Permission denied. Cannot execute the command. Details: {str(e)}"
                self.action_execution_returncode = (
                    e.errno if hasattr(e, "errno") else -1
                )
            except Exception as e:
                self.action_execution_stderr = (
                    f"An unexpected error occurred during execution: {str(e)}"
                )
                self.action_execution_returncode = (
                    -1
                )  # Generic error code for other exceptions

            self.show_action_execution_results = True
            self.show_action_execution_form = False

    def clear_action_execution_results(self):
        self.action_execution_stdout = ""
        self.action_execution_stderr = ""
        self.action_execution_returncode = None
        self.show_action_execution_results = False
        self.action_to_execute_name = None  # Optionally clear these too
        self.action_to_execute_content = None
        self.action_to_execute_variables = []
        self.action_variable_values = {}

    async def load_actions(self):
        async with self:  # ensures state updates are processed correctly
            if self.actions_loaded:
                return  # Don't reload if already loaded

            if not ACTION_DIR.exists():
                ACTION_DIR.mkdir(parents=True, exist_ok=True)

            self.actions = []
            for action_file in ACTION_DIR.glob("*.json"):
                with open(action_file, "r") as file:
                    try:
                        action_data = json.load(file)
                        # Ensure basic structure, add name from filename if not present
                        if "name" not in action_data:
                            action_data["name"] = action_file.stem
                        if "content" not in action_data:
                            action_data["content"] = ""  # Default content
                        if "variables" not in action_data:
                            action_data["variables"] = []  # Default variables
                        self.actions.append(action_data)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {action_file}")
            self.actions.sort(key=lambda x: x.get("name", ""))
            self.actions_loaded = True

    def confirm_delete_action_dialog(self, action_name: str):
        self.action_to_delete_name = action_name
        self.show_delete_action_dialog = True

    async def delete_action(self):
        async with self:
            if self.action_to_delete_name:
                # Ensure filename sanitization matches saving logic, or store filename in action dict
                # For now, assume action_name is the stem and matches the file name (common practice)
                # A more robust approach would be to store the filename in the action_data if it can differ from action_name
                safe_action_name = "".join(
                    [
                        c if c.isalnum() or c in (" ", "_", "-") else "_"
                        for c in self.action_to_delete_name
                    ]
                ).replace(" ", "_")
                action_file_to_delete = ACTION_DIR / f"{safe_action_name}.json"

                if action_file_to_delete.exists():
                    action_file_to_delete.unlink()
                else:
                    print(
                        f"Warning: Action file {action_file_to_delete} not found for deletion."
                    )

                # Reset dialog state
                self.show_delete_action_dialog = False
                self.action_to_delete_name = None
        # Reload actions
        await self.load_actions()

    def show_delete_action_dialog_method(self, action_name: str):
        """Show the delete action dialog"""
        self.show_delete_action_dialog = True
        self.action_to_delete_name = action_name

    def hide_delete_action_dialog(self):
        """Hide the delete action dialog"""
        self.show_delete_action_dialog = False
        self.action_to_delete_name = None

    def show_action_execution_form_method(self):
        """Show the action execution form"""
        self.show_action_execution_form = True

    def hide_action_execution_form(self):
        """Hide the action execution form"""
        self.show_action_execution_form = False


class PromptState(AppState):
    prompts: List[Dict] = []
    prompts_loaded: bool = False  # Flag to track if prompts have been loaded

    # current_prompt_data: dict to hold data for a new or edited prompt
    # Represented by individual fields
    prompt_name: str = ""
    prompt_content: str = ""
    prompt_variables: List[
        Dict
    ]  # As per subtask item 3: "prompt_variables: list[dict]"

    # For executing a prompt
    prompt_to_execute_name: Optional[str] = None
    prompt_to_execute_content: Optional[str] = None
    prompt_to_execute_variables: List[Dict] = []  # Storing as list of dicts
    prompt_variable_values: Dict[
        str, str
    ] = {}  # Stores user-provided values for variables for execution

    prompt_execution_output: str = ""  # As per subtask item 3. For "Show in Window"
    show_prompt_execution_output: bool = False

    # For prompt forms (create/edit)
    editing_prompt_original_name: Optional[str] = None
    current_prompt_variable_data: Dict = {"name": "", "type": "text", "default": ""}

    # For prompt execution
    # prompt_to_execute_name: Optional[str] = None # Already exists
    # prompt_to_execute_content: Optional[str] = None # Already exists
    # prompt_to_execute_variables: List[Dict] = [] # Already exists
    # prompt_variable_values: Dict[str, str] = {} # Already exists
    # prompt_execution_output: Optional[str] = None # Already exists, ensure it's Optional
    show_prompt_execution_form: bool = False
    # show_prompt_execution_output: bool = False # Already exists
    prompt_execution_action_type: str = "Show in Window"

    # For "Use as Input" (basic state, full logic later)
    selected_action_for_prompt_input: Optional[str] = None
    selected_target_variable_for_prompt_input: Optional[str] = None

    # For delete confirmation
    show_delete_prompt_dialog: bool = False
    prompt_to_delete_name: Optional[str] = None

    # Event handlers for prompt forms
    def prepare_new_prompt_form(self):
        self.prompt_name = ""
        self.prompt_content = ""
        self.prompt_variables = []
        self.editing_prompt_original_name = None
        self.current_prompt_variable_data = {"name": "", "type": "text", "default": ""}
        self.show_variable_form = False  # Assuming shared flag for variable modal
        self.show_prompt_form = True
        self.current_view = "Prompt Form"  # Or "New Prompt"

    async def prepare_edit_prompt_form(self, prompt_name_to_edit: str):
        async with self:
            if not self.prompts:  # Ensure prompts are loaded
                await self.load_prompts()

            prompt_to_edit = next(
                (p for p in self.prompts if p.get("name") == prompt_name_to_edit), None
            )
            if prompt_to_edit:
                self.prompt_name = prompt_to_edit.get("name", "")
                self.prompt_content = prompt_to_edit.get("content", "")
                # Ensure variables are loaded correctly
                loaded_vars = prompt_to_edit.get("variables", [])
                self.prompt_variables = [
                    {
                        "name": v.get("name", ""),
                        "type": v.get("type", "text"),
                        "default": v.get("default", ""),
                    }
                    for v in loaded_vars
                ]
                self.editing_prompt_original_name = prompt_name_to_edit
                self.current_prompt_variable_data = {
                    "name": "",
                    "type": "text",
                    "default": "",
                }
                self.show_variable_form = False
                self.show_prompt_form = True
                self.current_view = "Prompt Form"  # Or "Edit Prompt"
            else:
                print(f"Error: Prompt '{prompt_name_to_edit}' not found for editing.")

    def add_variable_to_prompt(self):
        var_name = self.current_prompt_variable_data.get("name", "").strip()
        if not var_name:
            print("Error: Variable name cannot be empty.")  # TODO: User-facing error
            return
        if any(v["name"] == var_name for v in self.prompt_variables):
            print(
                f"Error: Variable '{var_name}' already exists."
            )  # TODO: User-facing error
            return

        new_var = {
            "name": var_name,
            "type": self.current_prompt_variable_data.get("type", "text"),
            "default": self.current_prompt_variable_data.get("default", ""),
        }
        self.prompt_variables.append(new_var)
        self.current_prompt_variable_data = {"name": "", "type": "text", "default": ""}
        self.show_variable_form = False  # Hide variable modal

    def remove_variable_from_prompt(self, variable_name: str):
        self.prompt_variables = [
            v for v in self.prompt_variables if v.get("name") != variable_name
        ]

    async def save_prompt(self):
        async with self:
            if not self.prompt_name.strip():
                print("Error: Prompt name cannot be empty.")  # TODO: User-facing error
                return

            prompt_data_to_save = {
                "name": self.prompt_name.strip(),
                "content": self.prompt_content,
                "variables": self.prompt_variables,
            }

            safe_prompt_name = "".join(
                [c if c.isalnum() else "_" for c in self.prompt_name.strip()]
            )
            filename = PROMPT_DIR / f"{safe_prompt_name}.json"

            if self.editing_prompt_original_name:
                safe_original_name = "".join(
                    [
                        c if c.isalnum() else "_"
                        for c in self.editing_prompt_original_name
                    ]
                )
                original_filename = PROMPT_DIR / f"{safe_original_name}.json"
                if original_filename != filename and original_filename.exists():
                    original_filename.unlink()

            if not PROMPT_DIR.exists():
                PROMPT_DIR.mkdir(parents=True, exist_ok=True)

            with open(filename, "w") as f:
                json.dump(prompt_data_to_save, f, indent=4)

            # Reset form state
            self.show_prompt_form = False
            self.show_variable_form = False  # Ensure this is also reset
            self.prompt_name = ""
            self.prompt_content = ""
            self.prompt_variables = []
            self.editing_prompt_original_name = None
            self.current_prompt_variable_data = {
                "name": "",
                "type": "text",
                "default": "",
            }
            self.current_view = "Prompts"

        await self.load_prompts()

    def cancel_prompt_form(self):
        self.show_prompt_form = False
        self.show_variable_form = False
        self.prompt_name = ""
        self.prompt_content = ""
        self.prompt_variables = []
        self.editing_prompt_original_name = None
        self.current_prompt_variable_data = {"name": "", "type": "text", "default": ""}
        self.current_view = "Prompts"

    # Helper methods for prompt form input bindings
    def set_prompt_name(self, name: str):
        self.prompt_name = name

    def set_prompt_content(self, content: str):
        self.prompt_content = content

    def set_current_prompt_variable_data_item(self, key: str, value: str):
        self.current_prompt_variable_data[key] = value

    def reset_current_prompt_variable_data(self):
        self.current_prompt_variable_data = {"name": "", "type": "text", "default": ""}

    # Setters for prompt execution form
    def set_prompt_execution_action_type(self, type_str: str):
        self.prompt_execution_action_type = type_str

    def set_selected_action_for_prompt_input(self, action_name: str):
        self.selected_action_for_prompt_input = action_name
        # Future: could try to load variables of this action here
        # For now, target variable is a text input or static select

    def set_selected_target_variable_for_prompt_input(self, var_name: str):
        self.selected_target_variable_for_prompt_input = var_name

    # Placeholder for "Use as Input" logic
    def execute_prompt_use_as_input(self):
        # This is where the logic for taking prompt_execution_output
        # and setting it as a variable in a chosen action would go.
        # For now, we can just log or set a message.
        print(
            f"Attempting to use prompt output for action: {self.selected_action_for_prompt_input}, variable: {self.selected_target_variable_for_prompt_input}"
        )
        # For user feedback, could set a toast/alert message here via another state var
        self.show_prompt_execution_form = False  # Close form after attempting
        # Optionally, could display the formatted prompt output as well
        # self.execute_prompt_show_in_window() # if we want to also see it

    # Event handlers for Prompt Execution
    def prepare_prompt_execution(self, prompt: Dict):
        self.prompt_to_execute_name = prompt.get("name", "Unknown Prompt")
        self.prompt_to_execute_content = prompt.get("content", "")
        variables_for_execution = prompt.get("variables", [])
        self.prompt_to_execute_variables = variables_for_execution

        # Initialize prompt_variable_values with defaults
        self.prompt_variable_values = {
            var.get("name"): var.get("default", "")
            for var in variables_for_execution
            if var.get("name")
        }

        self.prompt_execution_output = ""  # Clear previous output
        self.show_prompt_execution_form = True
        self.show_prompt_execution_output = False
        self.prompt_execution_action_type = "Show in Window"  # Default action type
        # Reset "Use as Input" specific fields
        self.selected_action_for_prompt_input = None
        self.selected_target_variable_for_prompt_input = None

    def set_prompt_variable_value(self, var_name: str, value: str):
        self.prompt_variable_values[var_name] = value

    def execute_prompt_show_in_window(self):
        if self.prompt_to_execute_content is None:
            self.prompt_execution_output = "Error: No prompt content to format."
        else:
            modified_content = self.prompt_to_execute_content
            for var_name, var_value in self.prompt_variable_values.items():
                str_var_value = str(var_value) if var_value is not None else ""
                modified_content = modified_content.replace(
                    f"<{var_name}>", str_var_value
                )
            self.prompt_execution_output = modified_content

        self.show_prompt_execution_output = True
        self.show_prompt_execution_form = False

    def clear_prompt_execution_output(self):
        self.prompt_execution_output = ""
        self.show_prompt_execution_output = False
        # Optionally clear other execution-related fields if desired
        # self.prompt_to_execute_name = None
        # self.prompt_to_execute_content = None
        # self.prompt_to_execute_variables = []
        # self.prompt_variable_values = {}

    async def load_prompts(self):
        async with self:
            if self.prompts_loaded:
                return  # Don't reload if already loaded

            if not PROMPT_DIR.exists():
                PROMPT_DIR.mkdir(parents=True, exist_ok=True)

            self.prompts = []
            for prompt_file in PROMPT_DIR.glob("*.json"):
                with open(prompt_file, "r") as file:
                    try:
                        prompt_data = json.load(file)
                        if "name" not in prompt_data:
                            prompt_data["name"] = prompt_file.stem
                        if "content" not in prompt_data:
                            prompt_data["content"] = ""
                        if "variables" not in prompt_data:
                            prompt_data["variables"] = []
                        self.prompts.append(prompt_data)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {prompt_file}")
            self.prompts.sort(key=lambda x: x.get("name", ""))
            self.prompts_loaded = True

    def confirm_delete_prompt_dialog(self, prompt_name: str):
        self.prompt_to_delete_name = prompt_name
        self.show_delete_prompt_dialog = True

    async def delete_prompt(self):
        async with self:
            if self.prompt_to_delete_name:
                # Basic sanitization, align with how names are saved if different
                safe_prompt_name = "".join(
                    [
                        c if c.isalnum() or c in (" ", "_", "-") else "_"
                        for c in self.prompt_to_delete_name
                    ]
                ).replace(" ", "_")
                prompt_file_to_delete = PROMPT_DIR / f"{safe_prompt_name}.json"
                if prompt_file_to_delete.exists():
                    prompt_file_to_delete.unlink()
                else:
                    print(
                        f"Warning: Prompt file {prompt_file_to_delete} not found for deletion."
                    )

                self.show_delete_prompt_dialog = False
                self.prompt_to_delete_name = None
        await self.load_prompts()

    def show_delete_prompt_dialog_method(self, prompt_name: str):
        """Show the delete prompt dialog"""
        self.show_delete_prompt_dialog = True
        self.prompt_to_delete_name = prompt_name

    def hide_delete_prompt_dialog(self):
        """Hide the delete prompt dialog"""
        self.show_delete_prompt_dialog = False
        self.prompt_to_delete_name = None

    def show_prompt_execution_form_method(self):
        """Show the prompt execution form"""
        self.show_prompt_execution_form = True

    def hide_prompt_execution_form(self):
        """Hide the prompt execution form"""
        self.show_prompt_execution_form = False


class HistoryState(AppState):
    history_records: List[Dict] = []
    history_loaded: bool = False  # Flag to track if history has been loaded
    # To store filenames alongside records if needed for display or sorting
    history_record_files: List[str] = []

    async def load_history(self):
        async with self:
            if self.history_loaded:
                return  # Don't reload if already loaded

            if not HISTORY_DIR.exists():
                HISTORY_DIR.mkdir(parents=True, exist_ok=True)

            self.history_records = []
            self.history_record_files = []  # Clear previous list of files

            # Get all json files and sort them, e.g., by modification time (newest first) or name
            # For now, sorting by name as a simple default.
            history_files = sorted(
                HISTORY_DIR.glob("*.json"), key=lambda f: f.name, reverse=True
            )

            for history_file in history_files:
                with open(history_file, "r") as file:
                    try:
                        record_data = json.load(file)
                        self.history_records.append(record_data)
                        self.history_record_files.append(
                            history_file.name
                        )  # Store filename
                    except json.JSONDecodeError:
                        print(
                            f"Warning: Could not decode JSON from history file {history_file}"
                        )
            # If sorting by an internal timestamp is needed later, it would be done here.
            self.history_loaded = True


# Combined state for easier access if needed, though components can specify.
# For now, components will use specific states like ActionState, PromptState.
