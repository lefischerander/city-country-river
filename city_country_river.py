import pandas as pd
import random
import time
import os
import matplotlib.pyplot as plt

category_dict = {
    "c": "City",
    "l": "Country",
    "r": "River",
    "a": "Animal",
    "b": "Brand",
    "f": "Food",
}

value_path = "D:\\slf\\values.csv"
rounds_path = "D:\\slf\\rounds.csv"
values = pd.DataFrame(columns=["Value", "Category"])
rounds = pd.DataFrame(columns=["Letter", "All Values", "Points"])


def get_letter():
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return random.choice(alphabet)


def collect_inputs(letter):
    inputs = []
    start_time = time.time()
    print("You have 40 seconds to enter your inputs. Press Enter after each input.")

    while time.time() - start_time < 40:
        user_input = input().title()
        inputs.append(user_input)

    inputs = [x for x in inputs if x.startswith(letter) and len(x) > 1]

    return inputs


def get_points(inputs):
    points = len(inputs) * 10
    return points


def assign_category(inputs):
    global values
    for c in category_dict.keys():
        print(f"{c} -> {category_dict[c]}")
    for i in inputs:
        while is_correct(i) is False:
            print(f"What is the correct value for {i}?")
            i = input().title()
        print(f"What category is {i}?")
        category = input().lower()
        if category in category_dict.keys():
            values = pd.concat(
                [
                    values,
                    pd.DataFrame(
                        {"Value": i, "Category": category_dict[category]}, index=[0]
                    ),
                ],
                ignore_index=True,
            )
        else:
            print("Invalid category. Please enter a valid category.")
            assign_category(inputs)


def is_correct(value):
    print(f"Is {value} correct? (y/n)")
    return input().lower() == "y"


def get_categories():
    list = []
    for c in category_dict.keys():
        list.append(category_dict[c])
    return ", ".join(list)


def export():
    try:
        values.to_csv(
            value_path, mode="a", header=not os.path.exists(value_path), index=False
        )
        rounds.to_csv(
            rounds_path, mode="a", header=not os.path.exists(rounds_path), index=False
        )
    except Exception:
        print("Error saving the game. Please try again.")


def end_game():
    print("Game over!")
    values.sort_values(by="Category")
    print(rounds)
    print(values)
    export()
    print("Press any key to exit or r to see the report!")
    if input() == "r":
        report()
    exit()


def run_game():
    global rounds
    letter = get_letter()
    print(f"This rounds letter: {letter}")
    print(f"Your categories are: {get_categories()}")
    print("Press any key when ready or x to get a new letter!")
    if input() == "x":
        run_game()
    else:
        inputs = collect_inputs(letter)
        print(inputs)
    print("Round over")
    assign_category(inputs)
    rounds = pd.concat(
        [
            rounds,
            pd.DataFrame(
                {
                    "Letter": letter,
                    "All Values": ", ".join(inputs),
                    "Points": get_points(inputs),
                },
                index=[0],
            ),
        ],
        ignore_index=True,
    )
    print("Press any key to start the next round or x to end the game!")
    if input() == "x":
        end_game()
    else:
        run_game()


def report():
    temp_rounds = pd.read_csv(rounds_path)
    temp_values = pd.read_csv(value_path)
    top_values = temp_values["Value"].value_counts().head(10)
    top_categories = temp_values["Category"].value_counts().head(10)
    top_letters = temp_rounds["Letter"].value_counts().head(10)

    fig, axes = plt.subplots(2, 2, constrained_layout=True)
    fig.suptitle("Game Report")

    axes[0, 0].bar(top_values.index, top_values)
    axes[0, 0].set_title("Top Values")
    axes[0, 0].set_xticklabels(top_values.index, rotation=45)

    axes[0, 1].bar(top_categories.index, top_categories)
    axes[0, 1].set_title("Top Categories")
    axes[0, 1].set_xticklabels(top_categories.index, rotation=45)

    axes[1, 0].bar(top_letters.index, top_letters)
    axes[1, 0].set_title("Top Letters")

    avg_points_per_letter = temp_rounds.groupby("Letter")["Points"].mean()
    axes[1, 1].bar(avg_points_per_letter.index, avg_points_per_letter)
    axes[1, 1].set_title("Average Points per Letter")

    for ax in axes.flat:
        ax.yaxis.get_major_locator().set_params(integer=True)

    fig.show()


while True:
    print("Press any key to start the game or r to see the report!")
    if input() == "r":
        report()
    else:
        run_game()
