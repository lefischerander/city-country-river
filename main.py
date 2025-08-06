import interface
import game_logic
import logging
from config import HISTORY_GAMES_TO_SHOW

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
        """Callback function to process the game inputs."""
        game_logic.process_game_inputs(inputs, letter, main)

    interface.create_game_window(
        letter, categories, time_limit=60, submit_callback=on_submit
    )


def show_history():
    """Fetches and displays the last n (HISTORY_GAMES_TO_SHOW) games."""
    logging.info("Fetching game history...")
    last_games = game_logic.get_last_games(HISTORY_GAMES_TO_SHOW)
    interface.create_history_window(last_games, HISTORY_GAMES_TO_SHOW)


def main():
    """Creates the main menu GUI and serves as the application's entry point."""
    # Pass both the start and history functions to the start window.
    interface.create_start_window(start_game, show_history, HISTORY_GAMES_TO_SHOW)


if __name__ == "__main__":
    main()
