import random
from wikipedia_scraper import validate_input
import logging
from config import CATEGORIES
import data_manager
from datetime import datetime


def get_letter():
    """Returns a random letter for the game round."""
    return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def get_categories():
    """Returns the list of categories for the current game."""
    return CATEGORIES


def process_game_inputs(inputs, letter, main_menu_callback):
    """
    Receives inputs, validates them, calculates points, saves the results,
    and then calls the callback to return to the main menu.
    """
    validated_count = 0
    today_date = datetime.now().strftime("%d-%m-%Y")
    round_data = {"Letter": letter.upper(), "Date": today_date}
    round_data.update({cat: "" for cat in CATEGORIES})

    for category, term in inputs.items():
        if term:
            if not term.lower().startswith(letter.lower()):
                logging.warning(
                    f"Skipping '{term}': Does not start with the letter '{letter}'."
                )
                continue

            if validate_input(term, category):
                validated_count += 1
                round_data[category] = term.title()

    points = validated_count * 10
    round_data["Points"] = points
    logging.info(f"Round Results: {inputs} -> Points: {points}")

    if points > 0:
        data_manager.save_results_to_csv(round_data)
        logging.info(f"Round with {points} points saved.")
    else:
        logging.info("Round with 0 points not saved.")

    main_menu_callback()
