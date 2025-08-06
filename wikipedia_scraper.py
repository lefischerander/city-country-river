import wikipedia
import logging
from config import VALIDATION_KEYWORDS

wikipedia.set_lang("de")


def validate_input(term, category):
    """
    Validates a given term against a category using the German Wikipedia.
    Handles basic disambiguation.
    """
    if not term:
        return False

    try:
        # Use the page's summary, which is more reliable than a generic search
        page = wikipedia.page(term, auto_suggest=False)
        return check_summary_for_keywords(page.summary, category, term)

    except wikipedia.exceptions.DisambiguationError as e:
        # If the term is ambiguous (e.g., "Golf"), try the first option
        first_option = e.options[0]
        logging.info(
            f"'{term}' is ambiguous. Trying the first suggestion: '{first_option}'."
        )
        try:
            page = wikipedia.page(first_option, auto_suggest=False)
            return check_summary_for_keywords(page.summary, category, first_option)
        except Exception as inner_e:
            logging.warning(
                f"Validation failed for '{term}': Could not resolve disambiguation. Error: {inner_e}"
            )
            return False

    except wikipedia.exceptions.PageError:
        logging.warning(f"Validation failed for '{term}': Wikipedia page not found.")
        return False
    except Exception as e:
        logging.error(
            f"An unexpected error occurred during validation for '{term}': {e}"
        )
        return False


def check_summary_for_keywords(summary, category, term_used):
    """
    Helper function to check if a summary contains required keywords.
    """
    summary_lower = summary.lower()
    keywords = VALIDATION_KEYWORDS.get(category, [])

    if any(keyword.lower() in summary_lower for keyword in keywords):
        logging.info(
            f"Validation successful for '{term_used}' in category '{category}'."
        )
        return True
    else:
        logging.warning(
            f"Validation failed for '{term_used}': Could not confirm it belongs to the category '{category}'. Summary did not contain keywords."
        )
        logging.debug(f"Summary for '{term_used}': {summary_lower[:200]}...")
        return False
