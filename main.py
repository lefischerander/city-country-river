import data_manager
import interface
import game_logic
import logging
from config import (
    HISTORY_GAMES_TO_SHOW,
)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("wikipedia").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def start_game():
    """Starts a new game round."""
    logging.info("Starting a new game...")
    letter = game_logic.get_letter()
    categories = game_logic.get_categories()

    def on_submit(inputs):
        def processing_finished():
            logging.info("Game processing finished. Returning to main menu.")

        game_logic.process_game_inputs(inputs, letter, processing_finished)

    interface.create_game_window(
        letter, categories, time_limit=60, submit_callback=on_submit
    )


def show_history():
    """Fetches and displays the last n games."""
    logging.info("Fetching game history...")
    last_games = data_manager.get_last_games(HISTORY_GAMES_TO_SHOW)
    interface.create_history_window(
        last_games, title=f"Last {HISTORY_GAMES_TO_SHOW} Games"
    )


def search_by_letter():
    """Opens a window to search for games by letter."""

    def on_search_submit(letter):
        logging.info(f"Searching for games with letter '{letter.upper()}'...")
        games = data_manager.get_games_by_letter(letter)
        interface.create_history_window(
            games, title=f"Games for Letter '{letter.upper()}'"
        )

    interface.create_search_window(on_search_submit)


def show_all_games():
    """Fetches and displays all games from the history."""
    logging.info("Fetching all game history...")
    all_games = data_manager.get_all_games()
    interface.create_history_window(all_games, title="All Games")


def main():
    """Creates the main menu GUI and serves as the application's entry point."""
    logging.info("Application starting up. Checking data file for updates...")
    data_manager.synchronize_csv_on_startup()
    interface.create_start_window(
        start_game, show_history, search_by_letter, show_all_games
    )


if __name__ == "__main__":
    main()
