import argparse
import collections
import json
import os
import pathlib

import dotenv
import github
import matplotlib.pyplot as plt


dotenv.load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

VERBOSE = False


def parse_github_top_languages(
    repos: list, skip_repos: list, skip_langs: list, count
) -> dict:
    print("[*] Parse data from GitHub...")

    langs = collections.defaultdict(int)

    for repo_name, repo_dict in repos.items():
        # Skip repo if requested
        if repo_name in skip_repos:
            print(f"[*] Skipping repo: {repo_name}")
            continue

        print(f"[*] Processing repo: {repo_name}")

        langs_dict = repo_dict["top_languages"]

        for language, size in langs_dict.items():
            # Skip language if requested
            if language.lower() in skip_langs:
                if VERBOSE:
                    print(f"    [*] {language}: {size} SKIPPING!")
                continue

            langs[language] += size
            if VERBOSE:
                print(f"    [*] {language}: {size}")

    # Sort languages by highest count
    langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)

    # Only get the first 'N' languages
    langs = langs[:count]

    # Sorted outputs a list of tuples, so convert back to dict
    langs = dict(langs)

    if VERBOSE:
        print("[*] Top languages:")
        for k, v in langs.items():
            print(f"    [*] {k}: {v}")

    return langs


def plot_github_top_languages(langs, mode):
    print("[*] Plotting data from GitHub...")

    # Crunch some data
    langs_total = sum(langs.values())

    langs_percentages = dict()
    for language, size in langs.items():
        percentage = round(size / langs_total * 100)
        langs_percentages[language] = percentage

    # https://www.heavy.ai/blog/12-color-palettes-for-telling-better-stories-with-your-data
    colors = [
        "#fd7f6f",
        "#7eb0d5",
        "#b2e061",
        "#bd7ebe",
        "#ffb55a",
        "#ffee65",
        "#beb9db",
        "#fdcce5",
        "#8bd3c7",
    ]

    # Set size of figure
    fig = plt.figure(figsize=(8, 2))
    ax = plt.subplot(111)

    # Plot the data
    index = 0
    left_size = 0
    for language, size in langs.items():
        label = f"{language} ({langs_percentages[language]}%)"
        color = colors[index]
        plt.barh(
            0,
            size,
            left=left_size,
            color=color,
            height=0.8,
            label=label,
        )
        # Increment index (for color) and left padding
        index += 1
        left_size += size

    # Hide the axis
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Hide the border
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add percentage to bars
    for bar in ax.patches:
        x = bar.get_x() + bar.get_width() / 2
        y = 0
        percentage = f"{round(bar.get_width() / langs_total * 100)}%"
        ax.text(
            x,
            y,
            percentage,
            ha="center",
            color="black" if mode == "light" else "white",
            weight="bold",
            size=8,
        )

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.35, box.width, box.height * 0.65])

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 0),
        fancybox=True,
        ncol=5,
        framealpha=0,
        labelcolor="black" if mode == "light" else "white",
    )

    # Add a title
    plt.title(
        "Top Programming Languages",
        {"color": "black" if mode == "light" else "white", "fontweight": "bold"},
    )

    plt.savefig(f"top_languages_{mode}.png", format="png", transparent=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--skip_repos",
        nargs="+",
        help="Repository names to exclude (e.g., owner/name)",
        default=list(),
        required=False,
    )
    parser.add_argument(
        "-p",
        "--skip_languages",
        nargs="+",
        help="Programming languages to exclude",
        default=list(),
        required=False,
    )
    parser.add_argument(
        "-c",
        "--count",
        help="Count of languages to include on graph",
        default=5,
        required=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
        default=False,
        required=False,
    )
    args = parser.parse_args()

    skip_repos = args.skip_repos
    skip_languages = args.skip_languages
    count = int(args.count)
    if count > 9:
        print("[*] Count is too large. Choose between 2-9.")
        exit(1)

    VERBOSE = args.verbose

    # Check repos.json file exists
    repos_file = pathlib.Path("repos.json")
    if not repos_file.is_file():
        print("[*] The repos.json file does not exist.")
        print("[*] Add access token to .env and run python3 fetch_repo_metadata.py")
        exit(1)

    # Get repo metadata from repos.json file
    repos = None
    with open("repos.json") as f:
        repos = json.load(f)

    # Process repos metadata to get top languages
    langs = parse_github_top_languages(repos, skip_repos, skip_languages, count)

    # Create a light + dark mode chart
    for mode in ["light", "dark"]:
        plot_github_top_languages(langs, mode)
