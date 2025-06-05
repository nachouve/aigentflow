"""Main application file for AigentFlow"""

import reflex as rx

# from .components.action_form import action_form # Placeholder for action form
# from .components.prompt_form import prompt_form # Placeholder for prompt form
# Assuming styles are defined in reflex_aigentflow/styles.py as per standard Reflex template
from reflex_aigentflow import styles

from .components.action_list import actions_display
from .components.history_display import (
    history_view,  # Import the history_view component
)
from .components.prompt_list import prompts_display
from .state import (  # Import necessary states
    AppState,
)


def sidebar_button(text: str, view: str) -> rx.Component:
    """A helper function to create a sidebar button."""
    return rx.button(
        text,
        on_click=lambda: AppState.set_current_view(view),
        width="100%",
        variant=rx.cond(AppState.current_view == view, "solid", "outline"),
        color_scheme=rx.cond(AppState.current_view == view, "accent", "gray"),
    )


def main_layout() -> rx.Component:
    """The main layout of the application."""
    return rx.hstack(
        # Sidebar for navigation
        rx.vstack(
            rx.heading(
                "AigentFlow", size="7", padding_bottom="1em", padding_top="0.5em"
            ),
            sidebar_button("Actions", "Actions"),
            sidebar_button("Prompts", "Prompts"),
            sidebar_button("History", "History"),
            rx.spacer(),
            rx.color_mode.button(),  # Keep color mode switcher
            spacing="4",
            align_items="flex-start",
            border_right=f"1px solid {rx.color_mode_cond(light='var(--gray-4)', dark='var(--gray-a4)')}",
            padding="1em",
            height="100vh",  # Full height sidebar
            width="250px",
            position="fixed",  # Fixed position for sidebar
            left="0px",
            top="0px",
            bg=rx.color_mode_cond(
                light="var(--gray-1)", dark="var(--gray-2)"
            ),  # Background color for sidebar
        ),
        # Main content area
        rx.box(
            rx.vstack(
                rx.cond(
                    AppState.current_view == "Actions",
                    actions_display(),
                    rx.cond(
                        AppState.current_view == "Prompts",
                        prompts_display(),  # Display prompts view
                        rx.cond(
                            AppState.current_view == "History",
                            history_view(),  # Display history view
                            rx.text(
                                "Other View - Placeholder"
                            ),  # Fallback for other views if any
                        ),
                    ),
                ),
                # Adding placeholders for forms which might be shown in the main content area
                # rx.cond(AppState.show_action_form, action_form()),
                # rx.cond(AppState.show_prompt_form, prompt_form()),
                width="100%",
                padding="2em",
                align_items="flex-start",
            ),
            margin_left="250px",  # Offset by sidebar width
            width="calc(100% - 250px)",  # Take remaining width
            height="100vh",
            overflow_y="auto",  # Allow scrolling in content area
        ),
        width="100%",
        height="100vh",
        spacing="0",
    )


def index() -> rx.Component:
    # Main page - In Reflex v0.7.x, we trigger data loading from components
    return rx.fragment(
        main_layout(),
    )


# Add state and page to the app.
# Ensure that the AppState (and by extension ActionState etc.) is used by the app.
# Reflex automatically discovers states used in components.
app = rx.App(style=styles.base_style)
app.add_page(index)
