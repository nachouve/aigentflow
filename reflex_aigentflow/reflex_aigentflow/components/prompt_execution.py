import reflex as rx
from ..state import PromptState, ActionState # Import ActionState to get actions list

def prompt_execution_form() -> rx.Component:
    """A modal dialog form for providing variable values and choosing execution type."""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.hstack(
                        rx.text("Execute Prompt:"),
                        rx.text(PromptState.prompt_to_execute_name, as_="b", margin_left="0.5em"),
                        align_items="center"
                    )
                ),
                rx.form(
                    rx.modal_body(
                        rx.vstack(
                            # Variable inputs
                            rx.cond(
                                PromptState.prompt_to_execute_variables.length() > 0,
                                rx.foreach(
                                    PromptState.prompt_to_execute_variables,
                                    lambda var_def: rx.vstack(
                                        rx.text(var_def["name"], as_="label", margin_bottom="0.25em"),
                                        rx.input(
                                            placeholder=f"Enter value for {var_def['name']}",
                                            value=PromptState.prompt_variable_values[var_def["name"]],
                                            on_change=lambda val: PromptState.set_prompt_variable_value(var_def["name"], val),
                                            type_=rx.cond(var_def["type"] == "number", "number", 
                                                         rx.cond(var_def["type"] == "date", "date", "text")),
                                            width="100%"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="0.5em"
                                    )
                                ),
                                rx.text("No variables required for this prompt.", color_scheme="gray", margin_bottom="1em")
                            ),
                            
                            # Execution type selection
                            rx.text("Execution Type:", as_="label", margin_bottom="0.25em", margin_top="1em"),
                            rx.select(
                                ["Show in Window", "Use as Input"],
                                value=PromptState.prompt_execution_action_type,
                                on_change=PromptState.set_prompt_execution_action_type, # Add this setter to PromptState
                                width="100%"
                            ),

                            # Conditional UI for "Use as Input"
                            rx.cond(
                                PromptState.prompt_execution_action_type == "Use as Input",
                                rx.vstack(
                                    rx.text("Target Action:", as_="label", margin_top="1em", margin_bottom="0.25em"),
                                    rx.select(
                                        ActionState.actions.map(lambda act: act["name"]), # Get action names
                                        placeholder="Select Action",
                                        value=PromptState.selected_action_for_prompt_input,
                                        on_change=PromptState.set_selected_action_for_prompt_input, # Add setter
                                        width="100%"
                                    ),
                                    rx.text("Target Variable:", as_="label", margin_top="1em", margin_bottom="0.25em"),
                                    rx.input( # Simplified: text input for target variable name for now
                                        placeholder="Enter Target Variable Name in Selected Action",
                                        value=PromptState.selected_target_variable_for_prompt_input,
                                        on_change=PromptState.set_selected_target_variable_for_prompt_input, # Add setter
                                        width="100%"
                                    ),
                                    # Note: Dynamically populating target variable select based on chosen action is complex
                                    # and deferred as per subtask instructions.
                                    align_items="flex-start",
                                    width="100%",
                                    spacing="0.5em" # Spacing within the "Use as Input" block
                                )
                            ),
                            spacing="1em",
                            width="100%"
                        )
                    ),
                    rx.modal_footer(
                        rx.button(
                            "Cancel",
                            on_click=rx.set_val(PromptState.show_prompt_execution_form, False),
                            color_scheme="gray",
                            variant="soft"
                        ),
                        rx.button(
                            "Run Prompt",
                            type_="submit"
                        ),
                    ),
                    # This on_submit needs to be smarter or call a dispatcher in PromptState
                    on_submit=rx.cond(
                        PromptState.prompt_execution_action_type == "Show in Window",
                        PromptState.execute_prompt_show_in_window,
                        # Placeholder for "Use as Input" logic - for now, can also call a new state method
                        PromptState.execute_prompt_use_as_input # Add this method to PromptState
                    ),
                )
            )
        ),
        is_open=PromptState.show_prompt_execution_form,
        on_close=rx.set_val(PromptState.show_prompt_execution_form, False)
    )

def prompt_execution_output_display() -> rx.Component:
    """Displays the formatted output of a prompt."""
    return rx.cond(
        PromptState.show_prompt_execution_output,
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.hstack(
                        rx.text("Formatted Prompt Output:"),
                        rx.text(PromptState.prompt_to_execute_name, as_="b", margin_left="0.5em"),
                        align_items="center"
                    ),
                    size="md", 
                    margin_bottom="0.5em"
                ),
                rx.text_area( # Using text_area for potentially long formatted prompts
                    value=PromptState.prompt_execution_output,
                    read_only=True,
                    rows=10, # Good default height
                    width="100%",
                    font_family="monospace" # Good for preserving formatting
                ),
                rx.button(
                    "Clear Output",
                    on_click=PromptState.clear_prompt_execution_output,
                    margin_top="1em",
                    variant="outline"
                ),
                align_items="flex-start",
                width="100%",
                spacing="0.5em"
            ),
            padding="1em",
            border="1px solid #ddd",
            border_radius="md",
            margin_top="1em", 
            width="100%"
        )
    )

# Need to add to PromptState:
# - set_prompt_execution_action_type(self, type: str)
# - set_selected_action_for_prompt_input(self, action_name: str)
# - set_selected_target_variable_for_prompt_input(self, var_name: str)
# - execute_prompt_use_as_input(self) # Placeholder method for now
