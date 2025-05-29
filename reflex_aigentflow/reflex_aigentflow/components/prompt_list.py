import reflex as rx
from ..state import PromptState, AppState # Use .. to go up one level to access state.py
from .prompt_form import prompt_form, prompt_variable_form # Import the prompt forms
from .prompt_execution import prompt_execution_form, prompt_execution_output_display # Import execution components

def prompt_list_item(prompt: rx.Var[dict]) -> rx.Component:
    """Displays a single prompt item in a card or box."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(prompt["name"], size="md"),
                rx.spacer(),
                rx.button(
                    "Edit",
                    on_click=PromptState.prepare_edit_prompt_form(prompt["name"]),
                    size="1",
                    variant="outline" # Example styling
                ),
                rx.button(
                    "Execute",
                    on_click=PromptState.prepare_prompt_execution(prompt),
                    size="1",
                    margin_left="0.5em",
                    variant="outline" # Example styling
                ),
                rx.button(
                    "Delete",
                    on_click=PromptState.confirm_delete_prompt_dialog(prompt["name"]),
                    color_scheme="red",
                    size="1",
                    margin_left="0.5em"
                ),
                align="center",
                width="100%"
            ),
            rx.text(
                rx.cond(
                    prompt["content"].length() > 100,
                    prompt["content"].to_string()[0:100] + "...",
                    prompt["content"].to_string()
                ),
                size="sm",
                color_scheme="gray",
                margin_top="0.5em"
            ),
            align_items="flex-start",
            width="100%"
        ),
        border="1px solid #ddd",
        padding="1em",
        border_radius="md",
        width="100%"
    )

def prompts_display() -> rx.Component:
    """Displays the list of prompts and the new prompt button."""
    return rx.vstack(
        rx.button(
            "New Prompt",
            on_click=PromptState.prepare_new_prompt_form,
            margin_bottom="1em",
            align_self="flex-start"
        ),
        rx.cond(
            PromptState.prompts.length() > 0,
            rx.foreach(
                PromptState.prompts,
                prompt_list_item
            ),
            rx.center(
                rx.text("No prompts found. Click 'New Prompt' to create one.", color_scheme="gray")
            )
        )
    )

def prompts_view_or_form() -> rx.Component:
    """Decides whether to show the list of prompts or the prompt form."""
    return rx.vstack(
        rx.cond(
            AppState.show_prompt_form,
            prompt_form(),
            prompts_list_display_content() # The content previously in prompts_display
        ),
        prompt_execution_output_display(), # Display output if available

        # Modals - these can be placed here as they are globally controlled by state
        prompt_variable_form(), 
        prompt_execution_form(),

        # Delete confirmation dialog, needs to be accessible whether form or list is shown
        rx.alert_dialog(
            rx.alert_dialog_overlay(
                rx.alert_dialog_content(
                    rx.alert_dialog_header("Delete Prompt"),
                    rx.alert_dialog_body(
                        "Are you sure you want to delete prompt: ",
                        rx.text(PromptState.prompt_to_delete_name, as_="b"),
                        "?"
                    ),
                    rx.alert_dialog_footer(
                        rx.button(
                            "Cancel",
                            on_click=rx.set_val(PromptState.show_delete_prompt_dialog, False),
                            color_scheme="gray",
                            variant="soft"
                        ),
                        rx.button(
                            "Delete",
                            on_click=[
                                PromptState.delete_prompt, # Call the background task
                                rx.set_val(PromptState.show_delete_prompt_dialog, False) # Ensure dialog closes
                            ],
                            color_scheme="red"
                        ),
                    ),
                )
            ),
            is_open=PromptState.show_delete_prompt_dialog,
        ),
        spacing="1em",
        width="100%",
        align_items="stretch"
    )

# Renamed original prompts_display to prompts_view_or_form
# and the content part to prompts_list_display_content
# The main export will be prompts_view_or_form, aliased as prompts_display for consistency
def prompts_display() -> rx.Component:
    return prompts_view_or_form()
