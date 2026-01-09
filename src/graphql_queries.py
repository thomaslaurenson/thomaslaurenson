TOTAL_STARS_QUERY = """
query($username: String!, $cursor: String) {
  user(login: $username) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
      nodes {
        stargazerCount
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

USER_CONTRIBUTIONS_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

USER_LANGUAGES_QUERY = """
query($username: String!, $cursor: String) {
  user(login: $username) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

FOLLOWERS_COUNT_QUERY = """
query($username: String!) {
  user(login: $username) {
    followers {
      totalCount
    }
  }
}
"""

ALL_TIME_CONTRIBUTIONS_QUERY = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionYears
    }
  }
}
"""

YEAR_CONTRIBUTIONS_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""

YEAR_CONTRIBUTIONS_SUMMARY_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      totalRepositoriesWithContributedCommits
    }
  }
}
"""

SEARCH_ISSUE_COUNT_QUERY = """
query($query: String!) {
  search(type: ISSUE, query: $query) {
    issueCount
  }
}
"""

USER_PROFILE_QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
  }
}
"""

STREAK_CALENDAR_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

SEARCH_REVIEW_COUNT_QUERY = """
query($query: String!) {
  search(type: ISSUE, query: $query) {
    issueCount
  }
}
"""
