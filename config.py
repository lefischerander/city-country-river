VALIDATION_KEYWORDS = {
    "City": ["city", "cities", "town", "settlement", "municipality"],
    "Country": [
        "country",
        "countries",
        "nation",
        "state",
        "republic",
        "sovereign state",
    ],
    "River": ["river", "rivers", "watercourse"],
    "Plant": ["plant", "flora", "tree", "flower", "fungus", "shrub", "species of"],
    "Animal": [
        "animal",
        "fauna",
        "mammal",
        "bird",
        "insect",
        "fish",
        "reptile",
        "amphibian",
        "species of",
    ],
}

CATEGORIES = list(VALIDATION_KEYWORDS.keys())  # list of valid categor ies
HISTORY_GAMES_TO_SHOW = 10  # number of games to show in history
TIME_LIMIT = 60  # seconds for each round
