import logging
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from math import pow

from src.config import LANGUAGES_ORGS, LOCAL_TZ, STARS_ORGS
from src.github_client import GitHubClient
from src.graphql_queries import (
    ALL_TIME_CONTRIBUTIONS_QUERY,
    FOLLOWERS_COUNT_QUERY,
    ORG_LANGUAGES_QUERY,
    ORG_STARS_QUERY,
    SEARCH_ISSUE_COUNT_QUERY,
    SEARCH_REVIEW_COUNT_QUERY,
    STREAK_CALENDAR_QUERY,
    TOTAL_STARS_QUERY,
    USER_LANGUAGES_QUERY,
    USER_PROFILE_QUERY,
    YEAR_CONTRIBUTIONS_QUERY,
    YEAR_CONTRIBUTIONS_SUMMARY_QUERY,
)

logger = logging.getLogger(__name__)


class GitHubStats:

    def __init__(self, username):
        self.username = username
        self.client = GitHubClient()

    def get_total_stars(self):
        total_stars = 0

        def process_stars(result):
            nonlocal total_stars
            repos = result['data']['user']['repositories']['nodes']
            total_stars += sum(repo['stargazerCount'] for repo in repos)

        self.client.paginated_query(TOTAL_STARS_QUERY, self.username, process_stars)

        def process_org_stars(result):
            nonlocal total_stars
            repos = result['data']['organization']['repositories']['nodes']
            total_stars += sum(repo['stargazerCount'] for repo in repos)

        for org in STARS_ORGS:
            self.client.paginated_org_query(ORG_STARS_QUERY, org, process_org_stars)

        logger.info("total stars: %d (user + %d orgs)", total_stars, len(STARS_ORGS))
        return total_stars

    def get_commits_last_year(self):
        now = datetime.now(timezone.utc)
        one_year_ago = now - timedelta(days=365)

        variables = {
            'username': self.username,
            'from': one_year_ago.isoformat(),
            'to': now.isoformat(),
        }

        result = self.client.query(YEAR_CONTRIBUTIONS_QUERY, variables)
        contributions = result['data']['user']['contributionsCollection']
        return contributions['contributionCalendar']['totalContributions']

    def get_commits_all_time(self):
        result = self.client.query(ALL_TIME_CONTRIBUTIONS_QUERY, {'username': self.username})
        years = result['data']['user']['contributionsCollection']['contributionYears']

        total_commits = 0
        for year in years:
            start = datetime(year, 1, 1, tzinfo=timezone.utc)
            end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

            variables = {
                'username': self.username,
                'from': start.isoformat(),
                'to': end.isoformat()
            }

            result = self.client.query(YEAR_CONTRIBUTIONS_QUERY, variables)
            contributions = result['data']['user']['contributionsCollection']
            total_commits += contributions['contributionCalendar']['totalContributions']

        logger.info("commits all time: %d across %d years", total_commits, len(years))
        return total_commits

    def get_total_issues_created(self):
        # Search is the most consistent way to count authored issues across orgs,
        # provided the token can "see" those repositories.
        q = f"author:{self.username} is:issue"
        result = self.client.query(SEARCH_ISSUE_COUNT_QUERY, {"query": q})
        return result["data"]["search"]["issueCount"]

    def get_display_name(self):
        result = self.client.query(USER_PROFILE_QUERY, {'username': self.username})
        user = result.get("data", {}).get("user") or {}
        return user.get("name") or user.get("login") or self.username

    def get_total_pull_requests_created(self):
        q = f"author:{self.username} is:pr"
        result = self.client.query(SEARCH_ISSUE_COUNT_QUERY, {"query": q})
        return result["data"]["search"]["issueCount"]

    def get_followers_count(self):
        result = self.client.query(FOLLOWERS_COUNT_QUERY, {'username': self.username})
        return result['data']['user']['followers']['totalCount']

    def get_total_reviews_created(self):
        # Count authored PR reviews via search.
        q = f"reviewed-by:{self.username} is:pr"
        result = self.client.query(SEARCH_REVIEW_COUNT_QUERY, {"query": q})
        return result["data"]["search"]["issueCount"]

    def get_repos_contributed_last_year(self):
        now = datetime.now(timezone.utc)
        one_year_ago = now - timedelta(days=365)

        variables = {
            'username': self.username,
            'from': one_year_ago.isoformat(),
            'to': now.isoformat(),
        }

        result = self.client.query(YEAR_CONTRIBUTIONS_SUMMARY_QUERY, variables)
        contributions = result['data']['user']['contributionsCollection']
        return contributions['totalRepositoriesWithContributedCommits']

    def get_top_languages(self, top_n=6, exclude=None):
        if exclude is None:
            exclude = {"TeX", "HTML"}
        language_bytes = defaultdict(int)

        def process_languages(result):
            repos = result['data']['user']['repositories']['nodes']
            for repo in repos:
                for edge in repo['languages']['edges']:
                    name = edge['node']['name']
                    if name in exclude:
                        continue
                    language_bytes[name] += edge['size']

        self.client.paginated_query(USER_LANGUAGES_QUERY, self.username, process_languages)

        def process_org_languages(result):
            repos = result['data']['organization']['repositories']['nodes']
            for repo in repos:
                for edge in repo['languages']['edges']:
                    name = edge['node']['name']
                    if name in exclude:
                        continue
                    language_bytes[name] += edge['size']

        for org in LANGUAGES_ORGS:
            self.client.paginated_org_query(ORG_LANGUAGES_QUERY, org, process_org_languages)

        total_bytes = sum(language_bytes.values())
        if total_bytes == 0:
            return []

        sorted_languages = sorted(
            language_bytes.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_languages = []
        for lang, bytes_count in sorted_languages[:top_n]:
            percentage = (bytes_count / total_bytes) * 100
            top_languages.append({
                'language': lang,
                'percentage': round(percentage, 2),
                'bytes': bytes_count,
            })

        logger.info(
            "top languages: %s",
            ", ".join(f"{lang['language']} {lang['percentage']}%" for lang in top_languages),
        )
        return top_languages

    def get_first_contribution_date(self) -> tuple[str, str]:
        years_resp = self.client.query(ALL_TIME_CONTRIBUTIONS_QUERY, {'username': self.username})
        years = sorted(years_resp['data']['user']['contributionsCollection']['contributionYears'])
        if not years:
            return ("–", "–")

        for year in years:
            start_dt = datetime(year, 1, 1, tzinfo=timezone.utc)
            end_dt = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            days = self._fetch_calendar_days(start_dt, end_dt)
            first = next((d for d, count in sorted(days) if count > 0), None)
            if first:
                logger.info("first contribution: %s", first.isoformat())
                return (str(first.year), first.strftime("%b %-d, %Y"))

        return ("–", "–")

    def get_total_contributions(self):
        return self.get_commits_all_time()

    def _fetch_calendar_days(self, start_dt: datetime, end_dt: datetime):
        variables = {
            'username': self.username,
            'from': start_dt.isoformat(),
            'to': end_dt.isoformat(),
        }
        result = self.client.query(STREAK_CALENDAR_QUERY, variables)
        weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        days_list = []
        for w in weeks:
            for d in w["contributionDays"]:
                days_list.append((date.fromisoformat(d["date"]), d["contributionCount"]))
        return days_list

    def get_streak_stats(self) -> dict:
        # Determine all contribution years
        years_resp = self.client.query(ALL_TIME_CONTRIBUTIONS_QUERY, {'username': self.username})
        years = years_resp['data']['user']['contributionsCollection']['contributionYears']
        if not years:
            return {
                "total_contributions": 0,
                "current_streak": 0,
                "current_range": "-",
                "longest_streak": 0,
                "longest_range": "-",
            }

        days_list = []
        for year in years:
            start_dt = datetime(year, 1, 1, tzinfo=timezone.utc)
            if year == max(years):
                end_dt = datetime.now(LOCAL_TZ)
            else:
                end_dt = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            days_list.extend(self._fetch_calendar_days(start_dt, end_dt))

        if not days_list:
            return {
                "total_contributions": 0,
                "current_streak": 0,
                "current_range": "-",
                "longest_streak": 0,
                "longest_range": "-",
                "total_range": "-",
            }

        days_list.sort(key=lambda x: x[0])

        # Weekends (Sat=5, Sun=6) are excluded: they neither count toward nor break streaks.
        days_list = [(d, c) for d, c in days_list if d.weekday() < 5]

        if not days_list:
            return {
                "total_contributions": 0,
                "current_streak": 0,
                "current_range": "-",
                "longest_streak": 0,
                "longest_range": "-",
                "total_range": "-",
            }

        total_contribs = sum(c for _, c in days_list)
        first_day = days_list[0][0]
        last_day = days_list[-1][0]

        # Longest streak scan (forward over weekday-only entries).
        # After the weekend filter every consecutive pair in the list is a consecutive
        # weekday, so a simple prev_has flag is sufficient — no day-gap check needed.
        longest_len = 0
        longest_start = None
        longest_end = None
        run_len = 0
        run_start = None
        prev_has = False
        for d, count in days_list:
            has = count > 0
            if has:
                if prev_has:
                    run_len += 1
                else:
                    run_len = 1
                    run_start = d
                if run_len > longest_len:
                    longest_len = run_len
                    longest_start = run_start
                    longest_end = d
            else:
                run_len = 0
                run_start = None
            prev_has = has

        # Current streak (most-recent weekday backwards).
        # Grace period: if "today UTC" has 0 contributions and is still a weekday in NZT,
        # the user may not have committed yet today — skip ahead to the previous weekday.
        today_nzt = datetime.now(LOCAL_TZ).date()
        today_utc = datetime.now(timezone.utc).date()

        current_len = 0
        current_start = None
        current_end = None
        last_idx = len(days_list) - 1
        last_day_entry, last_count = days_list[last_idx]

        if (last_count == 0
                and today_nzt.weekday() < 5
                and last_day_entry == today_utc):
            last_idx -= 1

        if last_idx >= 0:
            last_day_entry, last_count = days_list[last_idx]
            if last_count > 0:
                current_end = last_day_entry
                current_len = 1
                current_start = last_day_entry
                for idx in range(last_idx - 1, -1, -1):
                    d, count = days_list[idx]
                    if count > 0:
                        current_len += 1
                        current_start = d
                    else:
                        break

        def fmt_range(start_d, end_d):
            if not start_d or not end_d:
                return "-"
            if start_d.year == end_d.year:
                return f"{start_d.strftime('%b %-d')} - {end_d.strftime('%b %-d, %Y')}"
            return f"{start_d.strftime('%b %-d, %Y')} - {end_d.strftime('%b %-d, %Y')}"

        return {
            "total_contributions": total_contribs,
            "total_range": fmt_range(first_day, last_day),
            "current_streak": current_len,
            "current_range": fmt_range(current_start, current_end),
            "longest_streak": longest_len,
            "longest_range": fmt_range(longest_start, longest_end),
            "current_start_date": current_start.isoformat() if current_start else None,
            "current_end_date": current_end.isoformat() if current_end else None,
            "longest_start_date": longest_start.isoformat() if longest_start else None,
            "longest_end_date": longest_end.isoformat() if longest_end else None,
        }


def calculate_rank(
    *,
    all_commits: bool,
    commits: int,
    prs: int,
    issues: int,
    reviews: int,
    stars: int,
    followers: int,
):
    # Rank calculation based on GitHub Readme Stats:
    # github.com/anuraghazra/github-readme-stats/blob/master/src/calculateRank.js
    def exponential_cdf(x: float) -> float:
        return 1 - pow(2, -x)

    def log_normal_cdf(x: float) -> float:
        return x / (1 + x)

    COMMITS_MEDIAN = 1000 if all_commits else 250
    COMMITS_WEIGHT = 2
    PRS_MEDIAN = 50
    PRS_WEIGHT = 3
    ISSUES_MEDIAN = 25
    ISSUES_WEIGHT = 1
    REVIEWS_MEDIAN = 2
    REVIEWS_WEIGHT = 1
    STARS_MEDIAN = 50
    STARS_WEIGHT = 4
    FOLLOWERS_MEDIAN = 10
    FOLLOWERS_WEIGHT = 1

    TOTAL_WEIGHT = (
        COMMITS_WEIGHT
        + PRS_WEIGHT
        + ISSUES_WEIGHT
        + REVIEWS_WEIGHT
        + STARS_WEIGHT
        + FOLLOWERS_WEIGHT
    )

    rank = 1 - (
        COMMITS_WEIGHT * exponential_cdf(commits / COMMITS_MEDIAN)
        + PRS_WEIGHT * exponential_cdf(prs / PRS_MEDIAN)
        + ISSUES_WEIGHT * exponential_cdf(issues / ISSUES_MEDIAN)
        + REVIEWS_WEIGHT * exponential_cdf(reviews / REVIEWS_MEDIAN)
        + STARS_WEIGHT * log_normal_cdf(stars / STARS_MEDIAN)
        + FOLLOWERS_WEIGHT * log_normal_cdf(followers / FOLLOWERS_MEDIAN)
    ) / TOTAL_WEIGHT

    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]

    percentile = rank * 100
    level = None
    for t, lvl in zip(thresholds, levels):
        if percentile <= t:
            level = lvl
            break
    if level is None:
        level = levels[-1]

    return level, percentile
