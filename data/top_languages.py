import argparse
import collections
import json
import os

import dotenv
import github
import matplotlib.pyplot as plt


dotenv.load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

VERBOSE = False


def fetch_github_top_languages() -> dict:
    print("[*] Fetching data from GitHub...")
    auth = github.Auth.Token(ACCESS_TOKEN)
    g = github.Github(auth=auth)

    # Structure for counting repos metadata
    repos = dict()

    count = 0
    # Loop through all repos for the user
    for repo in g.get_user().get_repos():
        print(f"[*] Fetching: {repo.full_name}")

        # For the specific repo, get dict of languages used
        lang_dict = repo.get_languages()

        # Also, save the repo languages
        repos[repo.full_name] = lang_dict

        count += 1
        # Useful for testing, only fetch a couple repos
        # if count > 10:
        #      break

    # Save data
    with open("repos.json", "w") as f:
        json.dump(repos, f, indent=4)

    return langs


def parse_github_top_languages(
    repos: list, skip_repos: list, skip_langs: list, count
) -> dict:
    print("[*] Parse data from GitHub...")

    langs = collections.defaultdict(int)

    for repo_name, langs_dict in repos.items():
        # Skip repo if requested
        if repo_name in skip_repos:
            print(f"[*] Skipping repo: {repo_name}")
            continue

        print(f"[*] Processing repo: {repo_name}")

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
        "-l",
        "--load",
        action="store_true",
        help="Load repo metadata from file",
        default=True,
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
    load = args.load
    VERBOSE = args.verbose
    print(skip_languages)

    # Get repo metadata
    # Load from file (repos.json) or re-dump
    repos = None
    if load:
        with open("repos.json") as f:
            repos = json.load(f)
    else:
        repos = fetch_github_top_languages()

    # Process repos metadata to get top languages
    langs = parse_github_top_languages(repos, skip_repos, skip_languages, count)

    # Create a light + dark mode chart
    for mode in ["light", "dark"]:
        plot_github_top_languages(langs, mode)
