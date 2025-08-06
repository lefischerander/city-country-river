import random
from wikipedia_scraper import validate_input
import logging
from config import CATEGORIES
import data_manager
from datetime import datetime


# === Module-level utility functions ===
def get_letter():
    """Selects a random letter that is common for starting words."""
    common_letters = "ABCDEFGHIJKLMNOPRST"
    return random.choice(common_letters)


# === Game Class ===
class Game:
    """Represents a single round of the game."""

    def __init__(self, letter):
        self.letter = letter.upper()
        self.categories = CATEGORIES
        self.initial_results = {}
        self.final_results = {}
        self.points = 0

    def validate_answers(self, inputs):
        """
        Performs initial validation of user inputs using a cache-first approach.
        """
        logging.info(
            f"Performing initial validation for game with letter '{self.letter}'..."
        )
        self.initial_results = {}

        for category, term in inputs.items():
            points = 0
            clean_term = term.strip() if term else ""

            if clean_term and clean_term.upper().startswith(self.letter):
                # Check the local cache first
                if data_manager.is_term_verified(clean_term, category):
                    logging.info(
                        f"Found '{clean_term}' in cache for category '{category}'."
                    )
                    points = 10
                # If not in cache, use Wikipedia validator
                elif validate_input(clean_term, category):
                    points = 10
                    # Add the newly validated term to the cache
                    data_manager.add_verified_term(clean_term, category)

            self.initial_results[category] = {"term": clean_term, "points": points}

        return self.initial_results

    def save_final_results(self, reviewed_results):
        """Calculates final points from reviewed results and saves to CSV."""
        logging.info("Saving final results after user review...")

        total_points = sum(result["points"] for result in reviewed_results.values())
        self.points = total_points

        round_data = {
            "Letter": self.letter,
            "Date": datetime.now().strftime("%d-%m-%Y"),
        }

        for category, result in reviewed_results.items():
            round_data[category] = result["term"]

        round_data["Points"] = self.points
        self.final_results = round_data

        data_manager.save_results_to_csv(self.final_results)
        logging.info(f"Game saved with {self.points} points.")
