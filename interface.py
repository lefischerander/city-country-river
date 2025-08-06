import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
from config import HISTORY_GAMES_TO_SHOW

# === Helper Functions ===


def _populate_treeview(tree, df):
    """Clears and populates a Treeview with data from a DataFrame."""
    # Clear existing items from the tree
    for item in tree.get_children():
        tree.delete(item)
    # Insert new sorted items
    for i, row in df.iterrows():
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", values=list(row.fillna("-")), tags=(tag,))


def _create_history_sort_controls(parent_frame, tree, game_data):
    """Creates and packs the sorting buttons for the history window."""
    sort_frame = ttk.Frame(parent_frame, padding=(10, 0, 10, 10))
    sort_frame.pack(fill="x", side="bottom")

    # Prepare DataFrame for sorting
    game_data["Date"] = pd.to_datetime(game_data["Date"], errors="coerce")
    original_df = game_data.copy()

    # Define sorting commands
    def sort_by_points_asc():
        _populate_treeview(tree, original_df.sort_values(by="Points", ascending=True))

    def sort_by_points_desc():
        _populate_treeview(tree, original_df.sort_values(by="Points", ascending=False))

    def sort_by_recent():
        _populate_treeview(tree, original_df.sort_values(by="Date", ascending=False))

    def sort_by_least_recent():
        _populate_treeview(tree, original_df.sort_values(by="Date", ascending=True))

    # Create and pack widgets
    ttk.Label(sort_frame, text="Sort by:").pack(side="left", padx=(0, 10))
    ttk.Button(sort_frame, text="Points (Low-High)", command=sort_by_points_asc).pack(
        side="left", padx=5
    )
    ttk.Button(sort_frame, text="Points (High-Low)", command=sort_by_points_desc).pack(
        side="left", padx=5
    )
    ttk.Button(sort_frame, text="Most Recent", command=sort_by_recent).pack(
        side="left", padx=5
    )
    ttk.Button(sort_frame, text="Least Recent", command=sort_by_least_recent).pack(
        side="left", padx=5
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
    """Creates a new window to display game results with grid lines and sorting options."""
    if game_data.empty:
        messagebox.showinfo("Game History", "No game results found for this search.")
        return

    history_window = tk.Toplevel()
    history_window.title(title)
    history_window.geometry("800x400")
    history_window.transient()
    history_window.grab_set()

    tree_frame = ttk.Frame(history_window, padding="10")
    tree_frame.pack(expand=True, fill="both")

    # Setup Treeview style
    style = ttk.Style()
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    style.configure("Treeview", rowheight=25, font=("Helvetica", 9))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.configure("oddrow", background="white")
    style.configure("evenrow", background="#E8E8E8")

    # Create Treeview and Scrollbar
    tree = ttk.Treeview(tree_frame, columns=list(game_data.columns), show="headings")
    tree.pack(side="left", expand=True, fill="both")
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # Configure columns
    for col in game_data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    # Initial data population
    _populate_treeview(tree, game_data)

    # Create the sorting controls at the bottom
    _create_history_sort_controls(history_window, tree, game_data)


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
