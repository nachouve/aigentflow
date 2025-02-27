# AIgentFlow

> ⚠️ **WARNING: EXPERIMENTAL PROJECT**  
> This project is currently in experimental stage. Features may be unstable, APIs could change without notice, and there might be unexpected behavior. Use at your own risk.

**AIgentFlow** is an intuitive desktop application designed for single users to effortlessly manage AI agents, execute function calls, and streamline prompt-based workflows. It offers the following features:

- **File-based storage**: Uses JSON files stored in `.aigentflow_agent/prompts/`.
- **Prompt Management**: Define new prompts with name, datetime, and content containing variables like `<variable1>`, `<variable2>`, etc.
- **Dynamic Forms**: Automatically generates forms with inputs for variables.
- **Action Execution**: Combo box to select an action and a button to execute the prompt.
- **Prompt and Action Creation**: Buttons for creating new prompts and actions.
- **History Logging**: Stores prompt history and executed action logs in JSON format.
- **JSON Validation**: Ensures the integrity of JSON data.
- **Shell and Python Execution**: Executes actions as shell commands and Python functions.
- **Action Definition**: Actions have a name, description, and a launch sentence with `$1` as a placeholder for variables.
- **User Interface**: Layout includes a left menu to select Prompts, Actions, or History, and a right panel for lists, forms, buttons, etc.

## Configuration and Running

1. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

2. **Run the Application**:
    ```sh
    streamlit run main.py
    ```

3. **Directory Structure**:
    Ensure the following directory structure for storing prompts, actions, and history:
    ```
    .aigentflow/
        prompts/
        actions/
        history/
    ```

## Creating Agents

1. Place your Python agent file in the "agents/" folder. 
2. Implement your logic as a class or function that can be called by other modules.
3. Ensure it handles necessary parameters (e.g., folder path, prompt text) for execution.

## Creating Manually Actions

You can use the AigentFlow interface to create actions (and prompts). But it is also possible
to do it manually following these steps:

1. Add a new JSON file in the ".aigentflow_agent/actions/" folder. 
2. The file must include a "name", "content", and (optionally) a "variables" list. 
3. The "content" typically contains the command to run the agent, like "python agents\\agentname.py --someflag".
4. Once created, open the UI, select your new action, fill in any variables, and click "Execute".
