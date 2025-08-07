from datetime import datetime
import pandas as pd
import logging
import os
from config import CATEGORIES, HISTORY_FILE, VERIFIED_TERMS_FILE

verified_terms_cache = pd.DataFrame()


# === Module-level utility functions ===
def _get_letter_from_row(row, categories):
    """Helper to infer the starting letter from the first valid entry in a row."""
    for cat in categories:
        if cat in row and pd.notna(row[cat]) and str(row[cat]).strip():
            return str(row[cat])[0].upper()
    return None


def _synchronize_history_with_config(history_df):
    """Removes obsolete columns from the history and adjusts points accordingly."""
    current_valid_columns = ["Date", "Letter"] + CATEGORIES + ["Points"]
    columns_to_drop = [
        col for col in history_df.columns if col not in current_valid_columns
    ]
    for col in columns_to_drop:
        mask = history_df[col].notna() & (history_df[col] != "")
        history_df.loc[mask, "Points"] -= 10
        history_df.drop(col, axis=1, inplace=True)
        logging.info(
            f"Removed obsolete category '{col}' and adjusted points for {mask.sum()} rows."
        )
    return history_df


def _reorder_columns(df):
    """Ensures column order: 'Date' is first, 'Letter' is second, 'Points' is last, and categories are sorted."""
    cols = df.columns.tolist()
    ordered_cols = []
    if "Date" in cols:
        ordered_cols.append("Date")
        cols.remove("Date")
    if "Letter" in cols:
        ordered_cols.append("Letter")
        cols.remove("Letter")
    if "Points" in cols:
        cols.remove("Points")
    ordered_cols.extend(sorted(cols))
    if "Points" in df.columns:
        ordered_cols.append("Points")
    return df[ordered_cols]


def _read_csv():
    """Safely reads the history CSV, returning a DataFrame or None."""
    if not os.path.isfile(HISTORY_FILE):
        return None
    try:
        return pd.read_csv(HISTORY_FILE)
    except pd.errors.EmptyDataError:
        logging.info("History CSV is empty.")
        return None
    except Exception as e:
        logging.error(f"Error reading game history from CSV: {e}")
        return None


def _read_and_sort_history():
    """Helper function to read the history CSV and sort it by date."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()

    df = pd.read_csv(HISTORY_FILE)
    # Convert 'Date' to datetime objects for correct sorting
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    # Sort by date, most recent first
    df = df.sort_values(by="Date", ascending=False)
    return df


# === Data Manager ===


def load_verified_terms():
    """Loads the verified terms from CSV into an in-memory DataFrame cache."""
    global verified_terms_cache
    if os.path.exists(VERIFIED_TERMS_FILE):
        verified_terms_cache = pd.read_csv(VERIFIED_TERMS_FILE)
        logging.info(f"Loaded {len(verified_terms_cache)} verified terms.")
    else:
        logging.info(
            f"'{VERIFIED_TERMS_FILE}' not found. Starting with an empty cache."
        )
        verified_terms_cache = pd.DataFrame(columns=["Term", "Category"])


def is_term_verified(term, category):
    """Checks if a term/category pair exists in the local cache."""
    if verified_terms_cache.empty:
        return False

    # Case-insensitive check
    match = verified_terms_cache[
        (verified_terms_cache["Term"].str.lower() == term.lower())
        & (verified_terms_cache["Category"] == category)
    ]
    return not match.empty


def add_verified_term(term, category):
    """Adds a newly verified term to the CSV and the in-memory cache."""
    global verified_terms_cache

    # Add to the CSV
    new_entry = pd.DataFrame([{"Term": term, "Category": category}])
    new_entry.to_csv(
        VERIFIED_TERMS_FILE,
        mode="a",
        header=not os.path.exists(VERIFIED_TERMS_FILE),
        index=False,
    )

    # Add to the in-memory cache to avoid reloading
    verified_terms_cache = pd.concat(
        [verified_terms_cache, new_entry], ignore_index=True
    )
    logging.info(f"Cached '{term}' for category '{category}'.")


def remove_verified_term(term, category):
    """Removes a term/category pair from the CSV and the in-memory cache."""
    global verified_terms_cache
    if verified_terms_cache.empty:
        return

    # Find the index of the row to remove (case-insensitive)
    initial_rows = len(verified_terms_cache)
    indices_to_drop = verified_terms_cache[
        (verified_terms_cache["Term"].str.lower() == term.lower())
        & (verified_terms_cache["Category"] == category)
    ].index

    if not indices_to_drop.empty:
        # Remove from the in-memory cache
        verified_terms_cache = verified_terms_cache.drop(indices_to_drop)

        # If something was actually dropped, rewrite the CSV file
        if len(verified_terms_cache) < initial_rows:
            verified_terms_cache.to_csv(VERIFIED_TERMS_FILE, index=False)
            logging.info(f"Removed '{term}' for category '{category}' from cache.")


def delete_game_by_index(index_to_delete):
    """Deletes a game record from the history CSV by its DataFrame index."""
    if not os.path.exists(HISTORY_FILE):
        logging.warning("Attempted to delete from a non-existent history file.")
        return

    df = pd.read_csv(HISTORY_FILE)
    if index_to_delete in df.index:
        df = df.drop(index_to_delete)
        # Save the updated dataframe back to the CSV, overwriting the old file.
        df.to_csv(HISTORY_FILE, index=False)
        logging.info(f"Deleted game record at index {index_to_delete}.")
    else:
        logging.warning(
            f"Attempted to delete non-existent index {index_to_delete} from history."
        )


def get_all_games():
    """Returns all game results from the CSV file, sorted by most recent."""
    return _read_and_sort_history()


def get_last_games(n):
    """Returns the last n game results from the CSV file, sorted by most recent."""
    df = _read_and_sort_history()
    return df.head(n)


def get_games_by_letter(letter):
    """Returns all games for a specific letter, sorted by most recent."""
    df = _read_and_sort_history()
    # Filter after sorting
    return df[df["Letter"].str.upper() == letter.upper()]


def get_letter_distribution():
    """Calculates the frequency of each starting letter from the game history."""
    df = _read_and_sort_history()
    if df.empty:
        return pd.Series(dtype=int)
    # Count occurrences and sort alphabetically for a clean chart
    return df["Letter"].value_counts().sort_index()


def save_results_to_csv(data):
    """Appends round results to the CSV, handling all synchronization and formatting."""
    try:
        round_df = pd.DataFrame([data])
        if not os.path.isfile(HISTORY_FILE):
            round_df.to_csv(HISTORY_FILE, index=False)
            logging.info(f"Created and saved results to {HISTORY_FILE}")
        else:
            history_df = pd.read_csv(HISTORY_FILE)
            combined_df = pd.concat([history_df, round_df], ignore_index=True)
            final_df = _reorder_columns(combined_df)
            final_df.to_csv(HISTORY_FILE, index=False)
            logging.info(f"Appended results and updated {HISTORY_FILE}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")


def _ensure_date_column(df):
    """Adds and fills the 'Date' column if it's missing or has nulls."""
    if "Date" not in df.columns:
        logging.info("Migrating data: 'Date' column not found. Adding column.")
        df["Date"] = None

    if df["Date"].isnull().any():
        logging.info("Found rows with missing dates. Assigning today's date.")
        today_date_str = datetime.now().strftime("%d-%m-%Y")
        df["Date"] = df["Date"].fillna(today_date_str)
    return df


def _ensure_letter_column(df):
    """Adds and infers the 'Letter' column if it's missing."""
    if "Letter" not in df.columns:
        logging.info("Migrating data: 'Letter' column not found. Inferring letters...")
        letters = df.apply(_get_letter_from_row, axis=1, categories=CATEGORIES)
        df.insert(0, "Letter", letters)
    return df


def synchronize_csv():
    """Checks and updates the CSV on app start to match the current config."""
    if not os.path.isfile(HISTORY_FILE):
        logging.info("CSV file not found. Nothing to synchronize.")
        return
    try:
        history_df = pd.read_csv(HISTORY_FILE)
        if history_df.empty:
            return

        original_df = history_df.copy()

        # Perform synchronization steps
        history_df = _ensure_date_column(history_df)
        history_df = _ensure_letter_column(history_df)
        history_df = _synchronize_history_with_config(history_df)

        # Check if any changes were made by comparing DataFrames
        if not original_df.equals(history_df):
            final_df = _reorder_columns(history_df)
            final_df.to_csv(HISTORY_FILE, index=False)
            logging.info("Successfully synchronized and saved CSV with current rules.")

    except Exception as e:
        logging.error(f"Failed to synchronize CSV on startup: {e}")
