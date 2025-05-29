"""Main application file for AigentFlow"""

import reflex as rx
from .state import AppState, ActionState, PromptState, HistoryState # Import necessary states
from .components.action_list import actions_display
from .components.prompt_list import prompts_display 
from .components.history_display import history_view # Import the history_view component
# from .components.action_form import action_form # Placeholder for action form
# from .components.prompt_form import prompt_form # Placeholder for prompt form

# Assuming styles are defined in reflex_aigentflow/styles.py as per standard Reflex template
from reflex_aigentflow import styles 


def sidebar_button(text: str, view: str) -> rx.Component:
    """A helper function to create a sidebar button."""
    return rx.button(
        text,
        on_click=rx.set_val(AppState.current_view, view),
        # is_active=AppState.current_view == view, # is_active is not a standard rx.button prop
        width="100%",
        variant=rx.cond(AppState.current_view == view, "solid", "outline"),
        color_scheme=rx.cond(AppState.current_view == view, "accent", "gray"),
    )

def main_layout() -> rx.Component:
    """The main layout of the application."""
    return rx.hstack(
        # Sidebar for navigation
        rx.vstack(
            rx.heading("AigentFlow", size="7", padding_bottom="1em", padding_top="0.5em"),
            sidebar_button("Actions", "Actions"),
            sidebar_button("Prompts", "Prompts"),
            sidebar_button("History", "History"),
            rx.spacer(),
            rx.color_mode.button(), # Keep color mode switcher
            spacing="1em",
            align_items="flex-start",
            border_right=f"1px solid {rx.color_mode_cond(light='var(--gray-4)', dark='var(--gray-a4)')}",
            padding="1em",
            height="100vh", # Full height sidebar
            width="250px",
            position="fixed", # Fixed position for sidebar
            left="0px",
            top="0px",
            bg=rx.color_mode_cond(light="var(--gray-1)", dark="var(--gray-2)"), # Background color for sidebar
        ),
        # Main content area
        rx.box(
            rx.vstack(
                rx.cond(
                    AppState.current_view == "Actions",
                    actions_display(),
                    rx.cond(
                        AppState.current_view == "Prompts",
                        prompts_display(), # Display prompts view
                        rx.cond(
                            AppState.current_view == "History",
                            history_view(), # Display history view
                            rx.text("Other View - Placeholder") # Fallback for other views if any
                        )
                    )
                ),
                # Adding placeholders for forms which might be shown in the main content area
                # rx.cond(AppState.show_action_form, action_form()),
                # rx.cond(AppState.show_prompt_form, prompt_form()),
                width="100%",
                padding="2em",
                align_items="flex-start" 
            ),
            margin_left="250px", # Offset by sidebar width
            width="calc(100% - 250px)", # Take remaining width
            height="100vh",
            overflow_y="auto" # Allow scrolling in content area
        ),
        width="100%",
        height="100vh",
        spacing="0" 
    )

def index() -> rx.Component:
    # Main page - loads actions and shows the main layout
    return rx.fragment(
        # Load actions only if they haven't been loaded or the list is empty.
        # Using .length() < 1 might cause issues if items are loaded but then all deleted.
        # A more robust flag like `*_loaded: bool` in each state would be better,
        # but for now, this is simpler based on current state structure.
        rx.call_on_load(ActionState.load_actions, ActionState.actions.length() < 1),
        rx.call_on_load(PromptState.load_prompts, PromptState.prompts.length() < 1), 
        rx.call_on_load(HistoryState.load_history, HistoryState.history_records.length() < 1), # Load history
        main_layout(),
    )


# Add state and page to the app.
# Ensure that the AppState (and by extension ActionState etc.) is used by the app.
# Reflex automatically discovers states used in components.
app = rx.App(style=styles.base_style)
app.add_page(index)
