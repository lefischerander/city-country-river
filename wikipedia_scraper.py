import wikipedia
import logging
import re
from config import VALIDATION_KEYWORDS

wikipedia.set_lang("de")


def _find_best_page(term):
    """
    Tries to find a Wikipedia page with a more robust, prioritized strategy.
    Lets DisambiguationError propagate.
    """
    try:
        # Try a direct match first. This is the most reliable.
        return wikipedia.page(term, auto_suggest=False)
    except wikipedia.exceptions.PageError:
        try:
            # If that fails, try with auto_suggest for typos.
            logging.debug(f"Direct match for '{term}' failed, trying auto-suggest...")
            return wikipedia.page(term, auto_suggest=True)
        except wikipedia.exceptions.PageError:
            # As a last resort, search and take the top result.
            logging.debug(f"Auto-suggest for '{term}' failed, trying a search...")
            search_results = wikipedia.search(term)
            if not search_results:
                return None
            try:
                return wikipedia.page(search_results[0], auto_suggest=False)
            except Exception:
                return None


def validate_input(term, category):
    """
    Validates a given term against a category using the German Wikipedia.
    Handles typos and disambiguation intelligently with a fallback search.
    """
    if not term:
        return False

    wikipedia.set_lang("de")

    def _check_options(options_list):
        """Helper to loop through a list of page titles and validate the first match."""
        for option in options_list:
            try:
                page = wikipedia.page(option, auto_suggest=False)
                if check_summary_for_keywords(
                    page.summary, category, option, is_checking_option=True
                ):
                    logging.info(
                        f"Validation successful. Chose '{option}' for '{term}'."
                    )
                    return True
            except Exception:
                continue
        return False

    try:
        # This might raise DisambiguationError, which is handled below.
        page = _find_best_page(term)

        # If a page was found, check it first.
        if page and check_summary_for_keywords(page.summary, category, term):
            return True

        # If the direct page was wrong or not found, we can still
        # perform a search and check the results as a fallback.
        logging.info(
            f"Initial check for '{term}' failed. Performing a targeted search..."
        )
        search_results = wikipedia.search(term)
        if search_results and _check_options(search_results):
            return True

        # If we're here, nothing has worked.
        logging.warning(f"Validation failed for '{term}': No suitable page found.")
        return False

    except wikipedia.exceptions.DisambiguationError as e:
        # This handles cases where the term itself is a disambiguation page.
        logging.info(f"'{term}' is ambiguous. Checking options: {e.options[:5]}...")
        if _check_options(e.options):
            return True

        logging.warning(
            f"Validation failed for '{term}': No suitable option found in disambiguation."
        )
        return False

    except Exception as e:
        logging.error(
            f"An unexpected error occurred during validation for '{term}': {e}"
        )
        return False


def check_summary_for_keywords(summary, category, term_used, is_checking_option=False):
    """
    Helper function to check if a summary contains required keywords using multiple matching strategies.
    """
    summary_lower = summary.lower()
    keyword_strategies = VALIDATION_KEYWORDS.get(category, {})

    # Whole Word Matching
    for keyword in keyword_strategies.get("whole_words", []):
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, summary_lower):
            if not is_checking_option:
                logging.info(
                    f"Validation successful for '{term_used}' (whole word: '{keyword}')."
                )
            return True

    # Suffix Matching
    for keyword in keyword_strategies.get("suffixes", []):
        # This pattern looks for a word ending with the keyword.
        pattern = r"\w+" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, summary_lower):
            if not is_checking_option:
                logging.info(
                    f"Validation successful for '{term_used}' (suffix: '{keyword}')."
                )
            return True

    if not is_checking_option:
        logging.warning(
            f"Validation failed for '{term_used}': Could not confirm it belongs to the category '{category}'. Summary did not contain keywords."
        )
        logging.debug(f"Summary for '{term_used}': {summary_lower[:200]}...")
    return False
