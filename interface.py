import tkinter as tk
from tkinter import ttk, messagebox
import data_manager
import pandas as pd
from config import HISTORY_GAMES_TO_SHOW

# === Helper Functions ===


def show_info(title, message):
    """
    Displays a simple, silent informational message box without the bell sound.
    """
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("300x120")
    dialog.resizable(False, False)
    dialog.transient()
    dialog.grab_set()

    main_frame = ttk.Frame(dialog, padding="15")
    main_frame.pack(expand=True, fill="both")

    message_label = ttk.Label(
        main_frame, text=message, wraplength=270, justify="center"
    )
    message_label.pack(expand=True, fill="both")

    ok_button = ttk.Button(main_frame, text="OK", command=dialog.destroy)
    ok_button.pack(pady=5)
    ok_button.focus_set()

    dialog.update_idletasks()
    try:
        parent = dialog.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = (
            parent.winfo_y()
            + (parent.winfo_height() // 2)
            - (dialog.winfo_height() // 2)
        )
        dialog.geometry(f"+{x}+{y}")
    except Exception:
        pass

    dialog.wait_window()


def _populate_treeview(tree, df):
    """Clears and populates a Treeview with data from a DataFrame."""
    display_df = df.copy()

    if "Date" in display_df.columns and pd.api.types.is_datetime64_any_dtype(
        display_df["Date"]
    ):
        display_df["Date"] = display_df["Date"].dt.strftime("%d-%m-%Y")

    for item in tree.get_children():
        tree.delete(item)
    for i, row in display_df.iterrows():
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", iid=i, values=list(row.fillna("-")), tags=(tag,))


def _create_history_sort_controls(parent_frame, tree, game_data):
    """Creates and packs the sorting buttons for the history window."""
    sort_frame = ttk.Frame(parent_frame, padding=(10, 0, 10, 10))
    sort_frame.pack(fill="x", side="bottom")

    # === State Management for Sorting ===
    sort_criteria = []  # List of tuples (column_name, ascending)
    original_df = game_data.copy()
    original_df["Date"] = pd.to_datetime(
        original_df["Date"], format="%d-%m-%Y", errors="coerce"
    )

    # === UI for Displaying Current Sort ===
    status_frame = ttk.Frame(sort_frame)
    status_frame.pack(fill="x", pady=(0, 5))
    ttk.Label(status_frame, text="Sorted by:").pack(side="left")
    sort_status_label = ttk.Label(
        status_frame, text="Default", font=("Helvetica", 9, "italic")
    )
    sort_status_label.pack(side="left", padx=5)

    # === Core Sorting Logic ===
    def apply_sort():
        """Applies the current sort_criteria list to the DataFrame and updates the tree."""
        if not sort_criteria:
            _populate_treeview(tree, original_df)
            sort_status_label.config(text="Default")
            return

        sort_by_cols = [col for col, asc in sort_criteria]
        sort_ascending = [asc for col, asc in sort_criteria]

        # Perform the multi-level sort
        sorted_df = original_df.sort_values(by=sort_by_cols, ascending=sort_ascending)
        _populate_treeview(tree, sorted_df)

        # Update the status label for user feedback
        status_text = ", ".join(
            [f"{col} ({'A-Z' if asc else 'Z-A'})" for col, asc in sort_criteria]
        )
        sort_status_label.config(text=status_text)

    # === Button Command Logic ===
    def add_sort_criterion(column_name, ascending=True):
        """Adds a new column to the sort criteria list and applies the sort."""
        # Remove any existing sort for this column to avoid duplicates
        nonlocal sort_criteria
        sort_criteria = [(col, asc) for col, asc in sort_criteria if col != column_name]
        # Add the new criterion to the front (making it the primary sort)
        sort_criteria.insert(0, (column_name, ascending))
        apply_sort()

    def clear_sort():
        """Resets the sorting to the default order."""
        nonlocal sort_criteria
        sort_criteria = []
        apply_sort()

    # === Create and Pack Widgets ===
    button_frame = ttk.Frame(sort_frame)
    button_frame.pack(fill="x")

    ttk.Button(
        button_frame,
        text="Letter (A-Z)",
        command=lambda: add_sort_criterion("Letter", True),
    ).pack(side="left", padx=5)
    ttk.Button(
        button_frame,
        text="Points (High-Low)",
        command=lambda: add_sort_criterion("Points", False),
    ).pack(side="left", padx=5)
    ttk.Button(
        button_frame,
        text="Points (Low-High)",
        command=lambda: add_sort_criterion("Points", True),
    ).pack(side="left", padx=5)
    ttk.Button(
        button_frame,
        text="Most Recent",
        command=lambda: add_sort_criterion("Date", False),
    ).pack(side="left", padx=5)
    ttk.Button(
        button_frame,
        text="Least Recent",
        command=lambda: add_sort_criterion("Date", True),
    ).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Clear Sort", command=clear_sort).pack(
        side="right", padx=5
    )


# === UI Functions ===


def create_start_window(
    start_callback, history_callback, search_callback, show_all_callback
):
    """
    Creates the main application window with a title and buttons.
    :param start_callback: Function to call when 'Start Game' is clicked.
    :param history_callback: Function to call when 'Show History' is clicked.
    :param n_games_to_show: The number of games to show in the history window.
    """
    root = tk.Tk()
    root.title("City, Country, River")
    root.geometry("300x230")

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(expand=True, fill="both")

    start_button = ttk.Button(
        main_frame,
        text="Start Game",
        command=start_callback,
    )
    start_button.pack(pady=5, fill="x")

    show_all_button = ttk.Button(
        main_frame, text="Show All Games", command=show_all_callback
    )
    show_all_button.pack(pady=5, fill="x")

    history_button = ttk.Button(
        main_frame,
        text=f"Show Last {HISTORY_GAMES_TO_SHOW} Games",
        command=history_callback,
    )
    history_button.pack(pady=5, fill="x")

    search_button = ttk.Button(
        main_frame, text="Search by Letter", command=search_callback
    )
    search_button.pack(pady=5, fill="x")

    exit_button = ttk.Button(main_frame, text="Exit", command=root.destroy)
    exit_button.pack(pady=5, fill="x")

    root.mainloop()


def create_history_window(game_data, title="Game History"):
    """Creates a new window to display game results with a delete option."""
    if game_data.empty:
        show_info("Game History", "No game results found for this search.")
        return

    history_window = tk.Toplevel()
    history_window.title(title)
    history_window.geometry("800x450")  # Increased height for the new button
    history_window.transient()
    history_window.grab_set()

    # --- Treeview Frame ---
    tree_frame = ttk.Frame(history_window, padding="10")
    tree_frame.pack(expand=True, fill="both")

    # Setup Treeview style
    style = ttk.Style()
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    style.configure("Treeview", rowheight=25, font=("Helvetica", 9))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.configure("oddrow", background="white")
    style.configure("evenrow", background="#E8E8E8")

    # --- Create Treeview and Scrollbar ---
    tree = ttk.Treeview(tree_frame, columns=list(game_data.columns), show="headings")
    tree.pack(side="left", expand=True, fill="both")
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # Configure columns
    for col in game_data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    # --- Initial data population ---
    _populate_treeview(tree, game_data)

    # --- Sorting Controls ---
    _create_history_sort_controls(history_window, tree, game_data)

    # --- Action Buttons (Delete) ---
    def delete_selected_game():
        """Deletes the selected item from the treeview and the CSV file."""
        selected_items = tree.selection()
        if not selected_items:
            show_info("No Selection", "Please select a game to delete.")
            return

        # We only handle single deletion here
        selected_iid = int(selected_items[0])

        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to permanently delete this game?"
        ):
            data_manager.delete_game_by_index(selected_iid)
            tree.delete(selected_iid)
            show_info("Success", "The selected game has been deleted.")

    action_frame = ttk.Frame(history_window, padding=(10, 0, 10, 10))
    action_frame.pack(fill="x", side="bottom")
    delete_button = ttk.Button(
        action_frame, text="Delete Selected Game", command=delete_selected_game
    )
    delete_button.pack(side="right")


def create_review_window(results, letter, confirm_callback):
    """
    Creates a window for the user to review and override validation results.
    """
    review_window = tk.Toplevel()
    review_window.title(f"Review Results for Letter '{letter}'")
    review_window.geometry("500x450")
    review_window.transient()
    review_window.grab_set()

    main_frame = ttk.Frame(review_window, padding="10")
    main_frame.pack(fill="both", expand=True)

    ttk.Label(
        main_frame,
        text="Review your answers and correct any mistakes.",
        font=("Helvetica", 11),
    ).pack(pady=(0, 10))

    check_vars = {}

    for category, result in results.items():
        frame = ttk.Frame(main_frame, padding=5)
        frame.pack(fill="x")

        is_correct = tk.IntVar(value=(1 if result["points"] > 0 else 0))
        check_vars[category] = is_correct

        chk = ttk.Checkbutton(frame, variable=is_correct)
        chk.pack(side="left", padx=(0, 10))

        label_text = (
            f"{category}: '{result['term']}'" if result["term"] else f"{category}: -"
        )
        ttk.Label(frame, text=label_text).pack(side="left")

    def on_confirm():
        """Gathers the final results and passes them to the callback."""
        final_results = {}
        for category, result in results.items():
            is_checked = check_vars[category].get() == 1
            final_results[category] = {
                "term": result["term"],
                "points": 10 if is_checked else 0,
            }

        review_window.destroy()
        confirm_callback(final_results)

    ttk.Button(main_frame, text="Confirm and Save", command=on_confirm).pack(pady=20)


def create_search_window(search_callback):
    """
    Creates a window to get a letter input from the user.
    :param search_callback: Function to call with the entered letter.
    """
    search_window = tk.Toplevel()
    search_window.title("Search by Letter")
    search_window.geometry("300x120")
    search_window.transient()
    search_window.grab_set()

    frame = ttk.Frame(search_window, padding="10")
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="Enter a letter:").pack(pady=5)

    entry = ttk.Entry(frame, width=5, justify="center")
    entry.pack(pady=5)
    entry.focus()

    def on_submit():
        letter = entry.get()
        if letter and letter.isalpha() and len(letter) == 1:
            search_window.destroy()
            search_callback(letter)
        else:
            messagebox.showwarning("Invalid Input", "Please enter a single letter.")

    submit_button = ttk.Button(frame, text="Search", command=on_submit)
    submit_button.pack(pady=10)
    search_window.bind("<Return>", lambda event: on_submit())


def create_game_window(letter, categories, time_limit, submit_callback):
    """Creates a game window for the current round.
    :param letter: The letter for the current game round.
    :param categories: List of categories for the game.
    :param time_limit: Time limit for the game round in seconds.
    :param submit_callback: Function to call with the user's answers.
    """
    game_window = tk.Toplevel()
    game_window.title(f"The Letter is: {letter.upper()}")
    game_window.attributes("-topmost", True)
    game_window.transient()
    game_window.grab_set()

    entries = {}
    time_left = tk.IntVar(value=time_limit)

    def submit_answers():
        results = {cat: entry.get() for cat, entry in entries.items()}
        game_window.destroy()
        submit_callback(results)

    def update_timer():
        current_time = time_left.get()
        if current_time > 0:
            time_left.set(current_time - 1)
            timer_label.config(text=f"Time Left: {current_time - 1}")
            game_window.after(1000, update_timer)
        else:
            timer_label.config(text="Time's Up!")
            submit_answers()

    main_frame = ttk.Frame(game_window, padding="20")
    main_frame.pack(expand=True, fill="both")

    # Header with Letter and Timer
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill="x", pady=10)
    letter_label = ttk.Label(
        header_frame, text=f"Letter: {letter.upper()}", font=("Helvetica", 16, "bold")
    )
    letter_label.pack(side="left")
    timer_label = ttk.Label(
        header_frame, text=f"Time Left: {time_left.get()}", font=("Helvetica", 12)
    )
    timer_label.pack(side="right")

    # Create an entry for each category
    for category in categories:
        label = ttk.Label(main_frame, text=f"{category}:")
        label.pack(anchor="w", padx=5, pady=(10, 0))
        entry = ttk.Entry(main_frame, width=50)
        entry.pack(fill="x", padx=5)
        entries[category] = entry

    submit_button = ttk.Button(
        main_frame, text="Submit Answers", command=submit_answers
    )
    submit_button.pack(pady=20)

    game_window.after(1000, update_timer)  # Start the timer
    game_window.mainloop()
