import reflex as rx

from ..state import (  # Use .. to go up one level to access state.py
    AppState,
    PromptState,
)
from .prompt_execution import (  # Import execution components
    prompt_execution_form,
    prompt_execution_output_display,
)
from .prompt_form import prompt_form, prompt_variable_form  # Import the prompt forms


def prompt_list_item(prompt: rx.Var[dict]) -> rx.Component:
    """Displays a single prompt item in a card or box."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(prompt["name"], size="4"),
                rx.spacer(),
                rx.button(
                    "Edit",
                    on_click=PromptState.prepare_edit_prompt_form(prompt["name"]),
                    size="1",
                    variant="outline",  # Example styling
                ),
                rx.button(
                    "Execute",
                    on_click=PromptState.prepare_prompt_execution(prompt),
                    size="1",
                    margin_left="0.5em",
                    variant="outline",  # Example styling
                ),
                rx.button(
                    "Delete",
                    on_click=PromptState.confirm_delete_prompt_dialog(prompt["name"]),
                    color_scheme="red",
                    size="1",
                    margin_left="0.5em",
                ),
                align="center",
                width="100%",
            ),
            rx.text(
                prompt["content"],
                size="3",
                color_scheme="gray",
                margin_top="0.5em",
            ),
            align_items="flex-start",
            width="100%",
        ),
        border="1px solid #ddd",
        padding="1em",
        border_radius="md",
        width="100%",
    )


def prompts_list_content() -> rx.Component:
    """Displays the list of prompts and the new prompt button."""
    return rx.vstack(
        rx.button(
            "New Prompt",
            on_click=PromptState.prepare_new_prompt_form,
            margin_bottom="1em",
            align_self="flex-start",
        ),
        rx.cond(
            PromptState.prompts.length() > 0,
            rx.foreach(PromptState.prompts.to(rx.Var[dict]), prompt_list_item),
            rx.center(
                rx.text(
                    "No prompts found. Click 'New Prompt' to create one.",
                    color_scheme="gray",
                )
            ),
        ),
    )


def prompts_view_or_form() -> rx.Component:
    """Decides whether to show the list of prompts or the prompt form."""
    return rx.vstack(
        rx.cond(
            AppState.show_prompt_form,
            prompt_form(),
            prompts_list_content(),  # Fixed function name
        ),
        prompt_execution_output_display(),  # Display output if available
        # Modals - these can be placed here as they are globally controlled by state
        prompt_variable_form(),
        prompt_execution_form(),
        # Delete confirmation dialog - simplified
        rx.cond(
            PromptState.show_delete_prompt_dialog,
            rx.box(
                rx.vstack(
                    rx.heading("Delete Prompt", size="4"),
                    rx.text(
                        "Are you sure you want to delete prompt: ",
                        rx.text(PromptState.prompt_to_delete_name, as_="b"),
                        "?",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=PromptState.hide_delete_prompt_dialog,
                            color_scheme="gray",
                            variant="soft",
                        ),
                        rx.button(
                            "Delete",
                            on_click=[
                                PromptState.delete_prompt,
                                PromptState.hide_delete_prompt_dialog,
                            ],
                            color_scheme="red",
                        ),
                        spacing="4",
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
        ),
        spacing="4",
        width="100%",
        align_items="stretch",
    )


# Renamed original prompts_display to prompts_view_or_form
# and the content part to prompts_list_display_content
# The main export will be prompts_view_or_form, aliased as prompts_display for consistency
def prompts_display() -> rx.Component:
    return prompts_view_or_form()
