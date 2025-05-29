import reflex as rx
from ..state import PromptState, AppState # Use .. to go up one level

def prompt_variable_form() -> rx.Component:
    """A modal dialog sub-form for adding/editing variables for a prompt."""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header("Add/Edit Prompt Variable"), # Simplified header
                rx.modal_body(
                    rx.vstack(
                        rx.input(
                            placeholder="Variable Name (e.g., 'topic')",
                            value=PromptState.current_prompt_variable_data["name"],
                            on_change=lambda val: PromptState.set_current_prompt_variable_data_item("name", val),
                            width="100%"
                        ),
                        rx.select(
                            ["text", "number", "date"], # Simplified types for prompts
                            placeholder="Select Variable Type",
                            value=PromptState.current_prompt_variable_data["type"],
                            on_change=lambda val: PromptState.set_current_prompt_variable_data_item("type", val),
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Default Value (optional)",
                            value=PromptState.current_prompt_variable_data["default"],
                            on_change=lambda val: PromptState.set_current_prompt_variable_data_item("default", val),
                            width="100%"
                        ),
                        spacing="1em"
                    )
                ),
                rx.modal_footer(
                    rx.button(
                        "Cancel",
                        on_click=[
                            rx.set_val(AppState.show_variable_form, False), # Use shared flag
                            PromptState.reset_current_prompt_variable_data
                        ],
                        color_scheme="gray",
                        variant="soft"
                    ),
                    rx.button(
                        "Add Variable", # Simplified for prompts
                        on_click=PromptState.add_variable_to_prompt
                    ),
                ),
            )
        ),
        is_open=AppState.show_variable_form, # Using shared flag for simplicity
        on_close=rx.set_val(AppState.show_variable_form, False) 
    )

def prompt_form() -> rx.Component:
    """Form for creating or editing a prompt."""
    return rx.box(
        rx.form(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        PromptState.editing_prompt_original_name,
                        "Edit Prompt: " + PromptState.editing_prompt_original_name,
                        "Create New Prompt"
                    ),
                    size="lg",
                    margin_bottom="1em"
                ),
                rx.input(
                    placeholder="Prompt Name",
                    value=PromptState.prompt_name,
                    on_change=PromptState.set_prompt_name,
                    is_required=True,
                    width="100%"
                ),
                rx.text_area(
                    placeholder="Prompt Content (e.g., 'Summarize the following text: <text_input>')",
                    value=PromptState.prompt_content,
                    on_change=PromptState.set_prompt_content,
                    rows=10, # Good height for prompt content
                    width="100%"
                ),
                
                rx.heading("Variables", size="md", margin_top="1em", margin_bottom="0.5em"),
                rx.cond(
                    PromptState.prompt_variables.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            PromptState.prompt_variables,
                            lambda var_item: rx.hstack( # No index needed if removing by name
                                rx.text(f"{var_item['name']} ({var_item['type']})"),
                                rx.spacer(),
                                rx.button("Remove", on_click=lambda: PromptState.remove_variable_from_prompt(var_item["name"]), size="1", color_scheme="red", variant="soft"),
                                width="100%",
                                justify_content="space-between",
                                padding_y="0.25em"
                            )
                        ),
                        align_items="stretch",
                        width="100%",
                        border="1px solid #ddd",
                        border_radius="md",
                        padding="1em"
                    ),
                    rx.text("No variables defined for this prompt yet.", color_scheme="gray")
                ),

                rx.button(
                    "Add Variable",
                    on_click=[
                        PromptState.reset_current_prompt_variable_data, # Prepare for new variable
                        rx.set_val(AppState.show_variable_form, True) # Use shared flag
                    ],
                    margin_top="1em",
                    variant="outline"
                ),

                rx.hstack(
                    rx.button(
                        "Cancel",
                        on_click=PromptState.cancel_prompt_form,
                        color_scheme="gray",
                        variant="soft"
                    ),
                    rx.button(
                        "Save Prompt",
                        type="submit", 
                    ),
                    spacing="1em",
                    margin_top="2em",
                    justify_content="flex-end",
                    width="100%"
                ),
                width="100%",
                spacing="1em"
            ),
            on_submit=PromptState.save_prompt,
            width="100%"
        ),
        padding="1em",
        border="1px solid #ddd",
        border_radius="md",
        width="100%", 
    )

# Helper methods in PromptState that must exist:
# - PromptState.set_prompt_name(value)
# - PromptState.set_prompt_content(value)
# - PromptState.set_current_prompt_variable_data_item(key, value)
# - PromptState.reset_current_prompt_variable_data()
# These were added in the previous turn (state update).
