import reflex as rx

from ..state import PromptState  # Import ActionState to get actions list


def prompt_execution_form() -> rx.Component:
    """A form for providing variable values and choosing execution type."""
    return rx.cond(
        PromptState.show_prompt_execution_form,
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.hstack(
                        rx.text("Execute Prompt:"),
                        rx.text(
                            PromptState.prompt_to_execute_name,
                            as_="b",
                            margin_left="0.5em",
                        ),
                        align_items="center",
                    ),
                    size="4",
                    margin_bottom="1em",
                ),
                # Variable inputs - simplified for now
                rx.cond(
                    PromptState.prompt_to_execute_variables.length() > 0,
                    rx.text(
                        "Please provide variable values, then select action type and run."
                    ),
                    rx.text(
                        "No variables required for this prompt.", color_scheme="gray"
                    ),
                ),
                # Execution type selection
                rx.text(
                    "Execution Type:",
                    as_="label",
                    margin_top="1em",
                    margin_bottom="0.25em",
                ),
                rx.select(
                    ["Show in Window", "Use as Input"],
                    placeholder="Select Execution Type",
                    value=PromptState.prompt_execution_action_type,
                    on_change=PromptState.set_prompt_execution_action_type,
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Cancel",
                        on_click=PromptState.hide_prompt_execution_form,
                        color_scheme="gray",
                        variant="soft",
                    ),
                    rx.button(
                        "Run Prompt",
                        on_click=PromptState.execute_prompt_show_in_window,
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


def prompt_execution_output_display() -> rx.Component:
    """Displays the formatted output of a prompt."""
    return rx.cond(
        PromptState.show_prompt_execution_output,
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.hstack(
                        rx.text("Formatted Prompt Output:"),
                        rx.text(
                            PromptState.prompt_to_execute_name,
                            as_="b",
                            margin_left="0.5em",
                        ),
                        align_items="center",
                    ),
                    size="4",
                    margin_bottom="0.5em",
                ),
                rx.text_area(  # Using text_area for potentially long formatted prompts
                    value=PromptState.prompt_execution_output,
                    read_only=True,
                    rows="10",  # Good default height
                    width="100%",
                    font_family="monospace",  # Good for preserving formatting
                ),
                rx.button(
                    "Clear Output",
                    on_click=PromptState.clear_prompt_execution_output,
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
            margin_top="1em",
            width="100%",
        ),
    )


# Need to add to PromptState:
# - set_prompt_execution_action_type(self, type: str)
# - set_selected_action_for_prompt_input(self, action_name: str)
# - set_selected_target_variable_for_prompt_input(self, var_name: str)
# - execute_prompt_use_as_input(self) # Placeholder method for now
