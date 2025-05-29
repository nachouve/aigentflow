import reflex as rx
from ..state import ActionState, AppState # Use .. to go up one level to access state.py
from .action_form import action_form, variable_form # Import the action forms
from .action_execution import action_execution_form, action_execution_results_display # Import execution components

def action_list_item(action: rx.Var[dict]) -> rx.Component:
    """Displays a single action item in a card or box."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(action["name"], size="md"),
                rx.spacer(),
                rx.button(
                    "Edit",
                    on_click=ActionState.prepare_edit_action_form(action["name"]),
                    size="1"
                ),
                rx.button(
                    "Execute",
                    on_click=ActionState.prepare_action_execution(action),
                    size="1",
                    margin_left="0.5em"
                ),
                rx.button(
                    "Delete",
                    on_click=ActionState.confirm_delete_action_dialog(action["name"]),
                    color_scheme="red",
                    size="1",
                    margin_left="0.5em"
                ),
                align="center",
                width="100%"
            ),
            rx.text(
                rx.cond(
                    action["content"].length() > 100,
                    action["content"].to_string()[0:100] + "...",
                    action["content"].to_string()
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

def actions_display() -> rx.Component:
    """Displays the list of actions and the new action button."""
    return rx.vstack(
        rx.button(
            "New Action",
            on_click=ActionState.prepare_new_action_form,
            margin_bottom="1em",
            align_self="flex-start"
        ),
        rx.cond(
            ActionState.actions.length() > 0,
            rx.foreach(
                ActionState.actions,
                action_list_item
            ),
            rx.center(
                rx.text("No actions found. Click 'New Action' to create one.", color_scheme="gray")
            )
        )
    )

def actions_view_or_form() -> rx.Component:
    """Decides whether to show the list of actions or the action form."""
    return rx.vstack(
        rx.cond(
            AppState.show_action_form,
            action_form(),
            actions_list_display_content() # The content previously in actions_display
        ),
        action_execution_results_display(), # Display results if available (conditionally shown inside component)
        
        # Modals - these can be placed here as they are globally controlled by state
        variable_form(), 
        action_execution_form(),

        # Delete confirmation dialog, needs to be accessible whether form or list is shown
        rx.alert_dialog(
            rx.alert_dialog_overlay(
                rx.alert_dialog_content(
                    rx.alert_dialog_header("Delete Action"),
                    rx.alert_dialog_body(
                        "Are you sure you want to delete action: ",
                        rx.text(ActionState.action_to_delete_name, as_="b"),
                        "?"
                    ),
                    rx.alert_dialog_footer(
                        rx.button(
                            "Cancel",
                            on_click=rx.set_val(ActionState.show_delete_action_dialog, False),
                            color_scheme="gray",
                            variant="soft"
                        ),
                        rx.button(
                            "Delete",
                            on_click=[
                                ActionState.delete_action, # Call the background task
                                rx.set_val(ActionState.show_delete_action_dialog, False) # Ensure dialog closes
                            ],
                            color_scheme="red"
                        ),
                    ),
                )
            ),
            is_open=ActionState.show_delete_action_dialog,
        ),
        spacing="1em",
        width="100%",
        align_items="stretch"
    )

# Renamed original actions_display to actions_view_or_form
# and the content part to actions_list_display_content
# The main export will be actions_view_or_form now
def actions_display() -> rx.Component:
    return actions_view_or_form()
