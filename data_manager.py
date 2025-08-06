from datetime import datetime
import pandas as pd
import logging
import os
from config import CATEGORIES, FILEPATH


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


def get_last_games(n=5):
    """Reads the CSV file and returns the last n game results."""
    if not os.path.isfile(FILEPATH):
        return pd.DataFrame()
    try:
        history_df = pd.read_csv(FILEPATH)
        return history_df.tail(n)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error reading game history from CSV: {e}")
        return pd.DataFrame()


def get_all_games():
    """Reads the CSV file and returns all game results."""
    if not os.path.isfile(FILEPATH):
        return pd.DataFrame()
    try:
        return pd.read_csv(FILEPATH)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error reading all game history from CSV: {e}")
        return pd.DataFrame()


def get_games_by_letter(letter):
    """Reads the CSV and returns all games played with a specific letter."""
    if not os.path.isfile(FILEPATH):
        return pd.DataFrame()
    try:
        history_df = pd.read_csv(FILEPATH)
        return history_df[history_df["Letter"].str.upper() == letter.upper()]
    except (pd.errors.EmptyDataError, KeyError):
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error filtering games by letter: {e}")
        return pd.DataFrame()


def save_results_to_csv(data):
    """Appends round results to the CSV, handling all synchronization and formatting."""
    try:
        round_df = pd.DataFrame([data])
        if not os.path.isfile(FILEPATH):
            round_df.to_csv(FILEPATH, index=False)
            logging.info(f"Created and saved results to {FILEPATH}")
        else:
            history_df = pd.read_csv(FILEPATH)
            combined_df = pd.concat([history_df, round_df], ignore_index=True)
            final_df = _reorder_columns(combined_df)
            final_df.to_csv(FILEPATH, index=False)
            logging.info(f"Appended results and updated {FILEPATH}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")


def synchronize_csv_on_startup():
    """Checks and updates the CSV on app start to match the current config."""
    if not os.path.isfile(FILEPATH):
        logging.info("CSV file not found. Nothing to synchronize.")
        return
    try:
        history_df = pd.read_csv(FILEPATH)
        if history_df.empty:
            return

        original_columns = history_df.columns.tolist()
        made_changes = False

        if "Date" not in history_df.columns:
            logging.info("Migrating data: 'Date' column not found. Adding column.")
            history_df["Date"] = None
            made_changes = True

        if "Letter" not in history_df.columns:
            logging.info(
                "Migrating data: 'Letter' column not found. Inferring letters..."
            )
            letters = history_df.apply(
                _get_letter_from_row, axis=1, categories=CATEGORIES
            )
            history_df.insert(0, "Letter", letters)
            made_changes = True

        if history_df["Date"].isnull().any():
            logging.info(
                f"Found {history_df['Date'].isnull().sum()} rows with missing dates. Assigning today's date."
            )
            today_date_str = datetime.now().strftime("%d-%m-%Y")
            history_df["Date"] = history_df["Date"].fillna(today_date_str)
            made_changes = True

        cleaned_df = _synchronize_history_with_config(history_df)

        if (
            list(cleaned_df.columns) != original_columns
            or "Letter" not in original_columns
        ):
            made_changes = True

        if made_changes:
            final_df = _reorder_columns(cleaned_df)
            final_df.to_csv(FILEPATH, index=False)
            logging.info("Successfully synchronized CSV with current rules.")
    except Exception as e:
        logging.error(f"Failed to synchronize CSV on startup: {e}")
