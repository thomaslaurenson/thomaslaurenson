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


def parse_github_stats(repos: list, skip_repos: list) -> dict:
    print("[*] Parse data from GitHub...")

    stats = collections.defaultdict(int)
    repo_count = 0

    for repo_name, repo_dict in repos.items():
        # Skip repo if requested
        if repo_name in skip_repos:
            print(f"[*] Skipping repo: {repo_name}")
            continue

        print(f"[*] Processing repo: {repo_name}")
        repo_count += 1

        for entry in repo_dict:
            if entry == "top_languages":
                continue
            else:
                stats[entry] += repo_dict[entry]

    stats["repo_count"] = repo_count
    return stats


def calculate_rank(stats: dict) -> dict:
    print("[*] Calculate GitHub ranking...")

    def exponential_cdf(x):
        return 1 - 2**-x

    def log_normal_cdf(x):
        return x / (1 + x)

    all_commits = True
    commits = stats["commit_count"]
    prs = stats["pr_count"]
    issues = stats["issue_count"]
    # TODO reviews
    reviews = 0
    stars = stats["stargazers_count"]
    # TODO followers
    followers = 39

    weights = {
        "commits": 2,
        "prs": 3,
        "issues": 1,
        "reviews": 1,
        "stars": 4,
        "followers": 1,
    }

    medians = {
        "commits": 1000 if all_commits else 250,
        "prs": 50,
        "issues": 25,
        "reviews": 2,
        "stars": 50,
        "followers": 10,
    }

    # Calculate total weight
    total_weight = 0
    for weight_value in weights.values():
        total_weight += weight_value

    rank = (
        1
        - (
            weights["commits"] * exponential_cdf(commits / medians["commits"])
            + weights["prs"] * exponential_cdf(prs / medians["prs"])
            + weights["issues"] * exponential_cdf(issues / medians["issues"])
            + weights["reviews"] * exponential_cdf(reviews / medians["reviews"])
            + weights["stars"] * log_normal_cdf(stars / medians["stars"])
            + weights["followers"] * log_normal_cdf(followers / medians["followers"])
        )
        / total_weight
    )

    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]

    rank = rank * 100
    level_index = [i for i in thresholds if i <= rank]
    level_index = len(level_index) - 1
    level = levels[level_index]

    print(f"[*] Rank: {rank}")
    print(f"[*] Level: {level}")

    return level, rank


def visualize_github_stats(stats, level, rank, mode):
    print("[*] Visualizing data from GitHub...")
    print(stats)
    print(level)
    print(rank)
    print(mode)

    pie_rank = int(rank)

    fig, ax = plt.subplots(figsize=(8, 2))

    # Create donut chart
    plt.pie(
        [pie_rank, 100 - pie_rank],
        wedgeprops={"width": 0.3},
        startangle=90,
        colors=["#FF000000", "#5DADE2"],
    )

    # Add level (e.g., A, B) to middle
    ax.text(
        0.0,
        0.0,
        level,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=40,
        fontweight="bold",
        color="#5DADE2",
    )
    # plt.show()
    # return

    table_data = [
        ["emjoi", "Repositories", stats["repo_count"]],
        ["emjoi", "Stargazers", stats["stargazers_count"]],
    ]

    # column_labels = [entry[1] for entry in table_data]
    # cell_text = [[entry[2]] for entry in table_data]
    # print(column_labels)
    # print(cell_text)

    # fig, ax = plt.subplots()
    # ax.axis('off')
    # ax.set_axis_off()
    tab = plt.table(cellText=table_data, loc="left")

    # Remove table cell border
    for key, cell in tab.get_celld().items():
        print(key[0])
        print(key[1])
        print(cell)
        print(type(cell))
        cell.set_linewidth(0)
        # Emoji column, right align
        if key[1] == 0:
            cell.set_text_props(ha="right")
        # Stat name column, left align
        if key[1] in [1, 2]:
            cell.set_text_props(ha="left")

    # Set title
    ax.set_title("Thomas Laurenson's GitHub Stats", weight="bold", size=12, color="k", loc="right")

    # cells = tab.properties()["celld"]
    # for i in range(0, 5):
    #     cells[i, 3].set_text_props(ha="center")

    fig.tight_layout()

    plt.show()
    # the_table = plt.table(cellText=cell_text,
    #                   rowLabels=rows,
    #                   rowColours=colors,
    #                   colLabels=columns,
    #                   loc='bottom')

    table = ax.table(cellText=table_data, loc="center")
    # Crunch some data


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
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
        default=False,
        required=False,
    )
    args = parser.parse_args()

    skip_repos = args.skip_repos
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
    stats = parse_github_stats(repos, skip_repos)
    level, rank = calculate_rank(stats)

    # Create a light + dark mode visualization
    # for mode in ["light", "dark"]:
    #     visualize_github_stats(stats, level, rank, mode)

    mode = "dark"
    visualize_github_stats(stats, level, rank, mode)


# <path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm9 3a1 1 0 11-2 0 1 1 0 012 0zm-.25-6.25a.75.75 0 00-1.5 0v3.5a.75.75 0 001.5 0v-3.5z"/>