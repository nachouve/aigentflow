import reflex as rx

from ..state import ActionState  # Use .. to go up one level


def action_execution_form() -> rx.Component:
    """A form for providing variable values before executing an action."""
    return rx.cond(
        ActionState.show_action_execution_form,
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.hstack(
                        rx.text("Execute Action:"),
                        rx.text(
                            ActionState.action_to_execute_name,
                            as_="b",
                            margin_left="0.5em",
                        ),
                        align_items="center",
                    ),
                    size="4",
                    margin_bottom="1em",
                ),
                rx.cond(
                    ActionState.action_to_execute_variables.length() > 0,
                    rx.text(
                        "Please provide values for the variables, then click Run Action."
                    ),
                    rx.text(
                        "No variables required for this action.", color_scheme="gray"
                    ),
                ),
                rx.hstack(
                    rx.button(
                        "Cancel",
                        on_click=ActionState.hide_action_execution_form,
                        color_scheme="gray",
                        variant="soft",
                    ),
                    rx.button(
                        "Run Action",
                        on_click=ActionState.execute_action,
                    ),
                    spacing="4",
                    margin_top="2em",
                    justify_content="flex-end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            padding="1em",
            border="1px solid #ddd",
            border_radius="md",
            width="100%",
        ),
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
                        rx.text(
                            ActionState.action_to_execute_name,
                            as_="b",
                            margin_left="0.5em",
                        ),
                        align_items="center",
                    ),
                    size="4",
                    margin_bottom="0.5em",
                ),
                rx.hstack(
                    rx.text("Return Code:", weight="bold"),
                    rx.text(
                        ActionState.action_execution_returncode.to_string()
                    ),  # Convert int to string
                    spacing="4",
                ),
                rx.cond(
                    ActionState.action_execution_returncode == 0,
                    rx.vstack(
                        rx.text("Stdout:", weight="bold", margin_top="0.5em"),
                        rx.code_block(
                            ActionState.action_execution_stdout,
                            language="bash",  # Or "text", "json" etc. based on expected output
                            show_line_numbers=True,
                            can_copy=True,
                            width="100%",
                            max_height="300px",  # Limit height and allow scrolling
                            overflow="auto",
                        ),
                        align_items="flex-start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "Stderr:",
                            weight="bold",
                            color_scheme="red",
                            margin_top="0.5em",
                        ),
                        rx.code_block(
                            ActionState.action_execution_stderr,
                            language="bash",  # Or "text"
                            show_line_numbers=True,
                            can_copy=True,
                            width="100%",
                            max_height="300px",
                            overflow="auto",
                        ),
                        align_items="flex-start",
                        width="100%",
                    ),
                ),
                rx.button(
                    "Clear Results",
                    on_click=ActionState.clear_action_execution_results,
                    margin_top="1em",
                    variant="outline",
                ),
                align_items="flex-start",
                width="100%",
                spacing="2",
            ),
            padding="1em",
            border="1px solid #ddd",
            border_radius="md",
            margin_top="1em",  # Space above the results box
            width="100%",  # Or set a max_width and center
        ),
    )
