import pandas as pd
import random
from wikipedia_scraper import validate_input
import logging
import os
from config import CATEGORIES


def get_letter():
    return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def get_last_games(n=5):
    """
    Reads the CSV file and returns the last n game results.
    Returns an empty DataFrame if the file doesn't exist or is empty.
    """
    filepath = "game_results_by_round.csv"
    if not os.path.isfile(filepath):
        return pd.DataFrame()

    try:
        history_df = pd.read_csv(filepath)
        return history_df.tail(n)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error reading game history from CSV: {e}")
        return pd.DataFrame()


def _synchronize_history_with_config(history_df):
    """
    Removes obsolete columns from the history and adjusts points accordingly.
    Returns the cleaned DataFrame.
    """
    current_valid_columns = CATEGORIES + ["Points"]
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
    """
    Sorts category columns alphabetically and ensures 'Points' is the last column.
    Returns the reordered DataFrame.
    """
    if "Points" in df.columns:
        cols = df.columns.tolist()
        cols.remove("Points")
        category_cols = sorted(cols)
        return df[category_cols + ["Points"]]
    return df


def save_results_to_csv(data):
    """
    Appends round results to the CSV, handling all synchronization and formatting.
    """
    try:
        round_df = pd.DataFrame([data])
        filepath = "game_results_by_round.csv"

        if not os.path.isfile(filepath):
            round_df.to_csv(filepath, index=False)
            logging.info(f"Created and saved results to {filepath}")
        else:
            # Read, clean, combine, reorder, and save
            history_df = pd.read_csv(filepath)
            cleaned_history_df = _synchronize_history_with_config(history_df)
            combined_df = pd.concat([cleaned_history_df, round_df], ignore_index=True)
            final_df = _reorder_columns(combined_df)
            final_df.to_csv(filepath, index=False)
            logging.info(f"Appended results and updated {filepath}")

    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")


def process_game_inputs(inputs, letter, main_menu_callback):
    """
    Receives inputs from the game window, validates them, updates the score,
    and then calls the provided callback to return to the main menu.
    """
    global values
    validated_count = 0
    round_data_for_csv = {cat: "" for cat in CATEGORIES}
    round_data_for_csv["Points"] = 0

    for category, term in inputs.items():
        if term:
            # First, check if the term starts with the correct letter.
            if not term.lower().startswith(letter.lower()):
                logging.warning(
                    f"Skipping '{term}': Does not start with the letter '{letter}'."
                )
                continue  # Move to the next term

            # If the letter is correct, then validate online.
            if validate_input(term, category):
                round_data_for_csv[category] = term
                validated_count += 1

    # Calculate points (10 points per valid input)
    points = validated_count * 10
    round_data_for_csv["Points"] = points

    # Log the results for debugging
    debug_results = inputs.copy()
    debug_results["Points"] = points
    logging.debug(f"Round Results: {debug_results}")

    if points > 0:
        save_results_to_csv(round_data_for_csv)
        logging.info(f"Round with {points} points saved to CSV.")
    else:
        logging.info("Round with 0 points not saved.")

    main_menu_callback()
