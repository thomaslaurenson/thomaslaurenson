import argparse
import collections
import json
import os

import dotenv
import github
import matplotlib.pyplot as plt


dotenv.load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def fetch_github_top_languages(skip_repos: list) -> dict:
    auth = github.Auth.Token(ACCESS_TOKEN)
    g = github.Github(auth=auth)

    # Structure for counting language use
    # Language is counted/stored as bytes (int)
    langs = collections.defaultdict(int)
    repos = dict()

    count = 0
    # Loop through all repos for the user
    for repo in g.get_user().get_repos():
        # Skip repo is requested
        if repo.full_name in skip_repos:
            print(f"[*] Skipping: {repo.full_name}")
            continue

        print(f"[*] Processing: {repo.full_name}")

        # For the specific repo, get dict of languages used
        lang_dict = repo.get_languages()
        for lang, size in lang_dict.items():
            langs[lang] += size
            print(f"    [*] {lang}: {size}")
        
        # Also, save the repo languages
        repos[repo.full_name] = lang_dict

        # Useful for testing, only fetch a couple repos
        # count += 1
        # if count > 10:
        #      break

    # Save data
    with open("langs.json", "w") as f:
        json.dump(langs, f, indent=4)
    with open("repos.json", "w") as f:
        json.dump(repos, f, indent=4)
    
    return langs


def parse_github_top_languages(langs: list, skip_langs: list, count) -> dict:
    # Remove erroneous languages
    for language in skip_langs:
        langs.pop(language)

    # Sort languages by highest count
    langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)

    # Only get the first 'N' languages
    langs = langs[:count]

    # Sorted outputs a list of tuples, so convert back to dict
    langs = dict(langs)

    print("[*] Top languages:")
    for k, v in langs.items():
        print(f"    [*] {k}: {v}")

    return langs


def plot_github_top_languages(langs, mode):
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
    fig = plt.figure(figsize=(8,2))
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
        loc="upper center", bbox_to_anchor=(0.5, 0), fancybox=True, shadow=True, ncol=5, framealpha=0, labelcolor="black" if mode == "light" else "white"
    )
    plt.savefig(f"top_languages_{mode}.png", format='png', transparent=True)


def main():
    # Fetch data from GitHub to make chart
    # skip_repos = [] 
    # langs = None
    # if not langs:
    #     print("[*] Fetching data from GitHub...")
    #     langs = fetch_github_top_languages(skip_repos)

    # Parse the raw GitHub data
    with open("langs.json") as f:
        langs = json.load(f)
    skip_langs = [
        "Lua",
        "TeX",
        "HTML",
    ]
    count = 5
    print("[*] Parse data from GitHub...")
    langs = parse_github_top_languages(langs, skip_langs, count)

    for mode in ["light", "dark"]:
        plot_github_top_languages(langs, mode)


if __name__ == "__main__":
    main()
