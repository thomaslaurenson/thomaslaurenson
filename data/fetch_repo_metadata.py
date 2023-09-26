import json
import os

import dotenv
import github


dotenv.load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def fetch_github_metadata() -> dict:
    print("[*] Fetching data from GitHub...")
    auth = github.Auth.Token(ACCESS_TOKEN)
    g = github.Github(auth=auth)

    # Structure for counting repos metadata
    repos = dict()

    # user = g.get_user()
    # user_name = user.login
    # user = g.get_user(user_name)
    # followers = user.followers
    # print(vars(user))
    # exit(1)

    # Loop through all repos for the user
    for repo in g.get_user().get_repos():
        print(f"[*] Fetching: {repo.full_name}")

        # For the specific repo, get useful metadata
        lang_dict = repo.get_languages()
        private = repo.private
        stargazers_count = repo.stargazers_count
        open_issue_count = repo.get_issues(state="open").totalCount
        closed_issue_count = repo.get_issues(state="closed").totalCount
        issue_count = open_issue_count + closed_issue_count
        open_pr_count = repo.get_pulls(state="open").totalCount
        closed_pr_count = repo.get_pulls(state="closed").totalCount
        pr_count = open_pr_count + closed_pr_count
        commit_count = repo.get_commits().totalCount

        # Save repo metadata
        repos[repo.full_name] = dict()
        repos[repo.full_name]["top_languages"] = lang_dict
        repos[repo.full_name]["private"] = private
        repos[repo.full_name]["stargazers_count"] = stargazers_count
        repos[repo.full_name]["issue_count"] = issue_count
        repos[repo.full_name]["pr_count"] = pr_count
        repos[repo.full_name]["commit_count"] = commit_count

    # Save data
    with open("repos.json", "w") as f:
        json.dump(repos, f, indent=4)


if __name__ == "__main__":
    fetch_github_metadata()
