VALIDATION_KEYWORDS = {
    "City": {
        "whole_words": [
            "city",
            "town",
            "settlement",
            "municipality",
            "gemeinde",
            "siedlung",
            "ortschaft",
        ],
        "suffixes": ["stadt", "dorf", "burg", "hafen"],
    },
    "Country": {
        "whole_words": [
            "country",
            "nation",
            "state",
            "republic",
            "land",
            "staat",
            "nation",
            "republik",
        ],
        "suffixes": ["reich"],
    },
    "River": {
        "whole_words": [
            "river",
            "watercourse",
            "strom",
            "wasserlauf",
            "nebenfluss",
            "fluss",
        ],
        "suffixes": ["fluss", "bach", "nebenfluss"],
    },
    "Plant": {
        "whole_words": [
            "plant",
            "flora",
            "tree",
            "flower",
            "fungus",
            "pflanze",
            "baum",
            "blume",
            "pilz",
            "gewächs",
            "gewächse",
            "gewächsarten",
            "pflanzenart",
        ],
        "suffixes": ["gattung", "familie", "gewächs", "gewächse"],
    },
    "Animal": {
        "whole_words": [
            "animal",
            "fauna",
            "mammal",
            "bird",
            "insect",
            "tier",
            "säugetier",
            "vogel",
            "insekt",
            "fisch",
            "reptil",
            "tiere",
            "frosch",
        ],
        "suffixes": ["katze", "gattung", "familie", "tiere", "tier", "rasse"],
    },
}

CATEGORIES = list(VALIDATION_KEYWORDS.keys())
HISTORY_GAMES_TO_SHOW = 10
TIME_LIMIT = 60
HISTORY_FILE = "game_history.csv"
VERIFIED_TERMS_FILE = "verified_terms.csv"
