import tkinter as tk
from tkinter import ttk, messagebox


def create_start_window(start_callback, history_callback, n_games_to_show):
    """
    Creates the main application window with a title and buttons.
    :param start_callback: Function to call when 'Start Game' is clicked.
    :param history_callback: Function to call when 'Show History' is clicked.
    :param n_games_to_show: The number of games to show in the history window.
    """
    root = tk.Tk()
    root.title("City, Country, River")
    root.geometry("300x200")

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(expand=True, fill="both")

    start_button = ttk.Button(
        main_frame,
        text="Start Game",
        command=lambda: [root.destroy(), start_callback()],
    )
    start_button.pack(pady=5, fill="x")

    history_button = ttk.Button(
        main_frame, text=f"Show Last {n_games_to_show} Games", command=history_callback
    )
    history_button.pack(pady=5, fill="x")

    exit_button = ttk.Button(main_frame, text="Exit", command=root.destroy)
    exit_button.pack(pady=5, fill="x")

    root.mainloop()


def create_history_window(game_data, n_games_to_show):
    """
    Creates a new window to display the last n game results with grid lines.
    :param n_games_to_show: The number of games to show in the window title.
    """
    if game_data.empty:
        messagebox.showinfo("Game History", "No game history found.")
        return

    history_window = tk.Toplevel()
    history_window.title(f"Last {n_games_to_show} Games")
    history_window.geometry("800x300")
    history_window.transient()
    history_window.grab_set()

    style = ttk.Style()
    style.theme_use("clam")

    # --- Add a separator to the Treeview layout to force row lines ---
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    style.configure("Treeview", rowheight=25, font=("Helvetica", 9))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    frame = ttk.Frame(history_window, padding="10")
    frame.pack(expand=True, fill="both")

    tree = ttk.Treeview(frame, columns=list(game_data.columns), show="headings")
    tree.pack(side="left", expand=True, fill="both")

    # Define tags for alternating row colors. This helps with row separation.
    tree.tag_configure("oddrow", background="white")
    tree.tag_configure("evenrow", background="#E8E8E8")

    for col in game_data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    # Insert data with alternating tags
    for index, row in game_data.iterrows():
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree.insert("", "end", values=list(row.fillna("-")), tags=(tag,))

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)


def create_game_window(letter, categories, time_limit, submit_callback):
    root = tk.Tk()
    root.title(f"The Letter is: {letter.upper()}")
    root.attributes("-topmost", True)

    entries = {}
    time_left = tk.IntVar(value=time_limit)

    def submit_answers():
        results = {cat: entry.get() for cat, entry in entries.items()}
        root.destroy()
        submit_callback(results)

    def update_timer():
        current_time = time_left.get()
        if current_time > 0:
            time_left.set(current_time - 1)
            timer_label.config(text=f"Time Left: {current_time - 1}")
            root.after(1000, update_timer)
        else:
            timer_label.config(text="Time's Up!")
            submit_answers()

    main_frame = ttk.Frame(root, padding="20")
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

    root.after(1000, update_timer)  # Start the timer
    root.mainloop()
