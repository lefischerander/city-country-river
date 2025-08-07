import data_manager
import interface
import warnings
from game_logic import Game, get_letter
import logging
from config import HISTORY_GAMES_TO_SHOW, CATEGORIES


class App:
    """The main application class that manages state and control flow."""

    def __init__(self):
        self.setup_logging()
        logging.info("Application starting up...")
        data_manager.synchronize_csv()
        data_manager.load_verified_terms()

    def setup_logging(self):
        """Configures the application-wide logging."""
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S",
        )
        # Suppress warnings and logs from external libraries to keep logs clean.
        logging.getLogger("wikipedia").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        warnings.filterwarnings("ignore", category=UserWarning, module="wikipedia")
        warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

    def run(self):
        """Starts the main application UI."""
        interface.create_start_window(
            start_callback=self.start_game,
            history_callback=self.show_history,
            search_callback=self.search_by_letter,
            show_all_callback=self.show_all_games,
            stats_callback=self.show_stats,
        )

    def start_game(self):
        """Starts a new game round."""
        logging.info("Starting a new game...")
        letter = get_letter()
        categories = CATEGORIES

        def on_submit(inputs):
            """Callback that handles game submission and review flow."""
            game = Game(letter)
            initial_results = game.validate_answers(inputs)

            def on_review_confirmed(final_results):
                """Callback for when the user confirms their reviewed scores."""
                # Compare initial and final results to update the cache
                for category, final_result in final_results.items():
                    initial_result = initial_results[category]
                    term = final_result["term"]

                    if not term:
                        continue

                    was_correct = initial_result["points"] > 0
                    is_now_correct = final_result["points"] > 0

                    if was_correct and not is_now_correct:
                        # User unchecked a valid term, so remove it from the cache.
                        data_manager.remove_verified_term(term, category)
                    elif not was_correct and is_now_correct:
                        # User checked an invalid term, so add it to the cache.
                        data_manager.add_verified_term(term, category)

                game.save_final_results(final_results)
                logging.info("Game processing finished. Returning to main menu.")
                interface.show_info(
                    "Game Saved", f"Your final score is {game.points} points."
                )

            interface.create_review_window(initial_results, letter, on_review_confirmed)

        interface.create_game_window(
            letter, categories, time_limit=60, submit_callback=on_submit
        )

    def show_history(self):
        """Fetches and displays the last n games."""
        logging.info("Fetching game history...")
        last_games = data_manager.get_last_games(HISTORY_GAMES_TO_SHOW)
        interface.create_history_window(
            last_games, title=f"Last {HISTORY_GAMES_TO_SHOW} Games"
        )

    def search_by_letter(self):
        """Opens a window to search for games by letter."""

        def on_search_submit(letter):
            logging.info(f"Searching for games with letter '{letter.upper()}'...")
            games = data_manager.get_games_by_letter(letter)
            interface.create_history_window(
                games, title=f"Games for Letter '{letter.upper()}'"
            )

        interface.create_search_window(on_search_submit)

    def show_all_games(self):
        """Fetches and displays all games from the history."""
        logging.info("Fetching all game history...")
        all_games = data_manager.get_all_games()
        interface.create_history_window(all_games, title="All Games")

    def show_stats(self):
        """Fetches game statistics and displays them in a new window."""
        logging.info("Fetching game statistics...")
        letter_distribution = data_manager.get_letter_distribution()
        interface.create_stats_window(letter_distribution)


if __name__ == "__main__":
    app = App()
    app.run()
