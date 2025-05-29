import reflex as rx
from ..state import ActionState, AppState # Use .. to go up one level

def variable_form() -> rx.Component:
    """A modal dialog sub-form for adding/editing variables for an action."""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.cond(
                        ActionState.current_variable_data.contains("index"), # Simple check if we are editing
                        "Edit Variable",
                        "Add New Variable"
                    )
                ),
                rx.modal_body(
                    rx.vstack(
                        rx.input(
                            placeholder="Variable Name (e.g., 'filename')",
                            value=ActionState.current_variable_data["name"],
                            on_change=lambda val: ActionState.set_current_variable_data_item("name", val),
                            width="100%"
                        ),
                        rx.select(
                            ["text", "number", "date", "options"],
                            placeholder="Select Variable Type",
                            value=ActionState.current_variable_data["type"],
                            on_change=lambda val: ActionState.set_current_variable_data_item("type", val),
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Default Value (optional)",
                            value=ActionState.current_variable_data["default"],
                            on_change=lambda val: ActionState.set_current_variable_data_item("default", val),
                            width="100%"
                        ),
                        rx.cond(
                            ActionState.current_variable_data["type"] == "options",
                            rx.text_area(
                                placeholder="Options (comma-separated, e.g., 'opt1,opt2,opt3')",
                                value=ActionState.current_variable_data["options"], # Storing as string from textarea
                                on_change=lambda val: ActionState.set_current_variable_data_item("options", val),
                                width="100%"
                            ),
                        ),
                        spacing="1em"
                    )
                ),
                rx.modal_footer(
                    rx.button(
                        "Cancel",
                        on_click=[
                            rx.set_val(AppState.show_variable_form, False),
                            ActionState.reset_current_variable_data # Add this method to ActionState
                        ],
                        color_scheme="gray",
                        variant="soft"
                    ),
                    rx.button(
                        "Add/Update Variable", # Single handler for add/update for simplicity now
                        on_click=[
                            ActionState.add_variable_to_action, # This method will handle if it's new or update
                        ]
                    ),
                ),
            )
        ),
        is_open=AppState.show_variable_form,
        on_close=rx.set_val(AppState.show_variable_form, False) # Ensure it closes on escape/overlay click
    )

def action_form() -> rx.Component:
    """Form for creating or editing an action."""
    return rx.box(
        rx.form(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        ActionState.editing_action_original_name,
                        "Edit Action: " + ActionState.editing_action_original_name,
                        "Create New Action"
                    ),
                    size="lg",
                    margin_bottom="1em"
                ),
                rx.input(
                    placeholder="Action Name",
                    value=ActionState.action_name,
                    on_change=ActionState.set_action_name, # Assumes setter exists or use lambda
                    is_required=True,
                    width="100%"
                ),
                rx.text_area(
                    placeholder="Action Content (e.g., script, template)",
                    value=ActionState.action_content,
                    on_change=ActionState.set_action_content, # Assumes setter exists or use lambda
                    rows=8, # Give it some decent height
                    width="100%"
                ),
                
                rx.heading("Variables", size="md", margin_top="1em", margin_bottom="0.5em"),
                rx.cond(
                    ActionState.action_variables.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            ActionState.action_variables,
                            lambda var_item, index: rx.hstack(
                                rx.text(f"{var_item['name']} ({var_item['type']})"),
                                rx.spacer(),
                                # rx.button("Edit", on_click=lambda: ActionState.prepare_edit_variable(index), size="1", variant="outline"), # TODO: Implement edit variable
                                rx.button("Remove", on_click=lambda: ActionState.remove_variable_from_action(var_item["name"]), size="1", color_scheme="red", variant="soft"),
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
                    rx.text("No variables defined for this action yet.", color_scheme="gray")
                ),

                rx.button(
                    "Add Variable",
                    on_click=[
                        ActionState.reset_current_variable_data, # Prepare for new variable
                        rx.set_val(AppState.show_variable_form, True)
                    ],
                    margin_top="1em",
                    variant="outline"
                ),

                rx.hstack(
                    rx.button(
                        "Cancel",
                        on_click=ActionState.cancel_action_form,
                        color_scheme="gray",
                        variant="soft"
                    ),
                    rx.button(
                        "Save Action",
                        type="submit", # Important for form submission if we add native validation
                        # on_click=ActionState.save_action # This is handled by form on_submit
                    ),
                    spacing="1em",
                    margin_top="2em",
                    justify_content="flex-end",
                    width="100%"
                ),
                width="100%",
                spacing="1em"
            ),
            on_submit=ActionState.save_action, # Call save_action on form submission
            width="100%"
        ),
        padding="1em",
        border="1px solid #ddd",
        border_radius="md",
        width="100%", # Or set a max_width like "600px" and center it
        # margin_x="auto" # To center if max_width is set
    )

# Helper methods in ActionState to be added or ensured:
# - ActionState.set_current_variable_data_item(key, value) # To update dict items
# - ActionState.reset_current_variable_data() # To clear the variable sub-form
# - ActionState.set_action_name(value)
# - ActionState.set_action_content(value)
# - (Optional) ActionState.prepare_edit_variable(index) # For editing existing variables
# These setters are crucial for two-way binding with form inputs.
# If direct binding like `ActionState.current_variable_data["name"]` works for on_change for rx.input, then explicit setters might not be needed for every field.
# However, for `rx.select` and complex state, explicit setters or handler methods are often cleaner.
# The lambda `on_change=lambda val: ActionState.set_current_variable_data_item("name", val)` is a common pattern.
# Need to add `set_current_variable_data_item` and `reset_current_variable_data` to `ActionState`.
# Also, `set_action_name` and `set_action_content` are used.
# `prepare_edit_variable` is a TODO for future enhancement.
