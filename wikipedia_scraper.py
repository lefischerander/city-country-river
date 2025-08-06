import wikipedia
import logging
from config import VALIDATION_KEYWORDS

wikipedia.set_lang("en")


def validate_input(term, category):
    """
    Validates an input term by checking the summary of its Wikipedia page.
    This single function now handles all categories uniformly.
    """
    try:
        search_results = wikipedia.search(term, results=3)
        if not search_results:
            logging.warning(
                f"Validation failed for '{term}': No Wikipedia results found."
            )
            return False

        keywords_to_check = VALIDATION_KEYWORDS.get(category, [category.lower()])

        for page_title in search_results:
            try:
                page = wikipedia.page(page_title, auto_suggest=False, redirect=True)
                summary = page.summary.lower()

                # The check is now simpler: just look for the category keyword.
                if any(key in summary for key in keywords_to_check):
                    logging.info(
                        f"Successfully validated '{term}' as a '{category}' by checking page '{page.title}'."
                    )
                    return True
            except wikipedia.exceptions.DisambiguationError:
                continue
            except wikipedia.exceptions.PageError:
                continue

        logging.warning(
            f"Validation failed for '{term}': Could not confirm it belongs to the category '{category}'."
        )
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while validating '{term}': {e}")
        return False
