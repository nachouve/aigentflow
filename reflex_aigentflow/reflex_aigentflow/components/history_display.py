import json  # Import json for dumps

import reflex as rx

from ..state import HistoryState  # Use .. to go up one level


def history_record_card(record: rx.Var[dict], index: rx.Var[int]) -> rx.Component:
    """Displays a single history record in a card."""
    # Attempt to get a title or use the filename (via index from history_record_files)
    # This assumes history_record_files[index] corresponds to history_records[index]
    record_title = HistoryState.history_record_files[index]

    return rx.box(
        rx.vstack(
            rx.heading(record_title, size="4", margin_bottom="0.5em"),
            rx.code_block(
                # Use rx.Var.create to handle the dict -> str conversion for code_block
                # json.dumps is a standard Python function, needs to be wrapped for rx.Var if record is a Var
                # However, record itself is already a Var[dict], so we need to handle its string representation.
                # A computed var in the state or a direct string conversion might be cleaner.
                # For simplicity, let's try to pass it directly if rx.code_block can handle it,
                # or use a helper in the state if needed.
                # The safest way is to ensure it's a string.
                # Since 'record' is rx.Var[dict], json.dumps(record) won't work directly in the component.
                # We will create a string representation.
                # A simple approach for now, assuming record is serializable:
                rx.Var.create(json.dumps(record.to_js(), indent=2)),
                language="json",
                show_line_numbers=True,
                can_copy=True,
                width="100%",
                max_height="400px",  # Limit height for long records
                overflow="auto",
            ),
            align_items="flex-start",
            width="100%",
        ),
        border="1px solid #ddd",
        padding="1em",
        border_radius="md",
        width="100%",
        margin_bottom="1em",  # Space between cards
    )


def history_view() -> rx.Component:
    """Displays the list of history records."""
    return rx.vstack(
        rx.heading("History Records", size="6", margin_bottom="1em"),
        rx.cond(
            HistoryState.history_records.length() > 0,
            rx.vstack(
                # Use rx.foreach with index to access filenames from history_record_files
                rx.foreach(
                    HistoryState.history_records,
                    lambda record, index: history_record_card(record, index),
                ),
                align_items="stretch",  # Ensure cards take full width
                width="100%",
                spacing="4",  # Spacing between cards if rx.vstack is used for the list
            ),
            rx.center(rx.text("No history records found.", color_scheme="gray")),
        ),
        width="100%",
        padding="1em",  # Padding for the overall history view area
        align_items="flex-start",
    )


# A note on rx.Var.create(json.dumps(record.to_js(), indent=2)):
# record.to_js() is used because `record` is an rx.Var[dict].
# json.dumps needs a Python dict, not an rx.Var.
# .to_js() or similar mechanism (like a computed var in state that does the dump) is needed.
# If rx.code_block can directly take an rx.Var[dict] and format it, that's simpler,
# but explicit string conversion is safer.
# The subtask mentions `rx.Var.create(json.dumps(record, indent=2))`. If `record` here
# is already a plain Python dict (e.g. if the `rx.foreach` provides it as such), then
# `record.to_js()` is not needed. Let's assume `record` within the lambda of `rx.foreach`
# is the actual Python dict element from the list. If it's an rx.Var, .to_js() is needed.
# Reflex's `rx.foreach` usually passes the item directly.
# Let's refine history_record_card assuming `record` is a Python dict within the lambda.


# Refined history_record_card based on typical rx.foreach behavior:
def history_record_card_refined(record: rx.Var[dict], index: int) -> rx.Component:
    """Displays a single history record in a card. Assumes 'record' is a Var[dict]."""
    record_title = HistoryState.history_record_files[index]  # Accessing via state

    return rx.box(
        rx.vstack(
            rx.heading(record_title, size="4", margin_bottom="0.5em"),
            rx.text_area(
                value=record.to(str),  # Convert the Var to string representation
                read_only=True,
                rows="15",
                width="100%",
                font_family="monospace",
            ),
            align_items="flex-start",
            width="100%",
        ),
        border="1px solid #ddd",
        padding="1em",
        border_radius="md",
        width="100%",
        margin_bottom="1em",
    )


# Update history_view to use the refined card structure for clarity
def history_view() -> rx.Component:
    """Displays the list of history records."""
    return rx.vstack(
        rx.heading(
            "History Records", size="6", margin_bottom="1em", align_self="flex-start"
        ),
        rx.cond(
            HistoryState.history_records.length() > 0,
            rx.vstack(
                rx.foreach(
                    # Pass index along with the record
                    rx.Var.range(HistoryState.history_records.length()),
                    lambda i: history_record_card_refined(
                        HistoryState.history_records[i], i
                    ),
                ),
                align_items="stretch",
                width="100%",
                spacing="4",
            ),
            rx.center(rx.text("No history records found.", color_scheme="gray")),
        ),
        width="100%",
        padding="1em",
        align_items="flex-start",
    )
