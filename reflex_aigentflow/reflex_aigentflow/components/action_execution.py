import reflex as rx
from ..state import ActionState # Use .. to go up one level

def action_execution_form() -> rx.Component:
    """A modal dialog form for providing variable values before executing an action."""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.hstack(
                        rx.text("Execute Action:"),
                        rx.text(ActionState.action_to_execute_name, as_="b", margin_left="0.5em"),
                        align_items="center"
                    )
                ),
                rx.form(
                    rx.modal_body(
                        rx.vstack(
                            rx.cond(
                                ActionState.action_to_execute_variables.length() > 0,
                                rx.foreach(
                                    ActionState.action_to_execute_variables,
                                    lambda var_def: rx.vstack(
                                        rx.text(var_def["name"], as_="label", margin_bottom="0.25em"),
                                        rx.cond(
                                            var_def["type"] == "options",
                                            rx.select(
                                                var_def["options"], # Assuming options is a list of strings
                                                placeholder=f"Select {var_def['name']}",
                                                value=ActionState.action_variable_values[var_def["name"]],
                                                on_change=lambda val: ActionState.set_action_variable_value(var_def["name"], val),
                                                width="100%"
                                            ),
                                            rx.input(
                                                placeholder=f"Enter value for {var_def['name']}",
                                                value=ActionState.action_variable_values[var_def["name"]],
                                                on_change=lambda val: ActionState.set_action_variable_value(var_def["name"], val),
                                                type_=rx.cond(var_def["type"] == "number", "number", 
                                                             rx.cond(var_def["type"] == "date", "date", "text")),
                                                width="100%"
                                            )
                                        ),
                                        align_items="flex-start", # Align label to the start
                                        width="100%",
                                        margin_bottom="0.5em"
                                    )
                                ),
                                rx.text("No variables required for this action.", color_scheme="gray")
                            ),
                            spacing="1em",
                            width="100%"
                        )
                    ),
                    rx.modal_footer(
                        rx.button(
                            "Cancel",
                            on_click=rx.set_val(ActionState.show_action_execution_form, False),
                            color_scheme="gray",
                            variant="soft"
                        ),
                        rx.button(
                            "Run Action",
                            type_="submit" # Use type_ for HTML attribute
                        ),
                    ),
                    on_submit=ActionState.execute_action, # Call execute_action on form submission
                )
            )
        ),
        is_open=ActionState.show_action_execution_form,
        on_close=rx.set_val(ActionState.show_action_execution_form, False)
    )

def action_execution_results_display() -> rx.Component:
    """Displays the results (stdout, stderr, return code) of an executed action."""
    return rx.cond(
        ActionState.show_action_execution_results,
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.hstack(
                        rx.text("Execution Results for:"),
                        rx.text(ActionState.action_to_execute_name, as_="b", margin_left="0.5em"),
                        align_items="center"
                    ),
                    size="md", 
                    margin_bottom="0.5em"
                ),
                rx.hstack(
                    rx.text("Return Code:", weight="bold"),
                    rx.text(ActionState.action_execution_returncode.to_string()), # Convert int to string
                    spacing="1em"
                ),
                rx.cond(
                    ActionState.action_execution_returncode == 0,
                    rx.vstack(
                        rx.text("Stdout:", weight="bold", margin_top="0.5em"),
                        rx.code_block(
                            ActionState.action_execution_stdout,
                            language="bash", # Or "text", "json" etc. based on expected output
                            show_line_numbers=True,
                            can_copy=True,
                            width="100%",
                            max_height="300px", # Limit height and allow scrolling
                            overflow="auto"
                        ),
                        align_items="flex-start",
                        width="100%"
                    ),
                    rx.vstack(
                        rx.text("Stderr:", weight="bold", color_scheme="red", margin_top="0.5em"),
                        rx.code_block(
                            ActionState.action_execution_stderr,
                            language="bash", # Or "text"
                            show_line_numbers=True,
                            can_copy=True,
                            width="100%",
                            max_height="300px",
                            overflow="auto"
                        ),
                        align_items="flex-start",
                        width="100%"
                    )
                ),
                rx.button(
                    "Clear Results",
                    on_click=ActionState.clear_action_execution_results,
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
            margin_top="1em", # Space above the results box
            width="100%" # Or set a max_width and center
        )
    )
