"""Authenticated HTTP client for the GitHub REST and GraphQL APIs.

Provides:

1. Authenticated REST GET requests.
2. GraphQL query execution with error handling.
3. Automatic cursor-based pagination for user and organisation queries.

Usage::

    from src.github_client import GitHubClient

    client = GitHubClient()
    result = client.query(MY_QUERY, {"username": "octocat"})
"""
import logging
from collections.abc import Callable

import requests

from src.config import API_URL, GH_TOKEN

REST_API_URL = 'https://api.github.com'

logger = logging.getLogger(__name__)


class GitHubClient:
    """Authenticated client for the GitHub REST and GraphQL APIs."""

    def __init__(self) -> None:
        self.headers = {
            'Authorization': f'Bearer {GH_TOKEN}',
            'Content-Type': 'application/json',
        }

    def get_rest(self, path: str, params: dict | None = None) -> dict | list:
        """Perform an authenticated GET request against the REST API.

        :param path: API path relative to ``https://api.github.com``, e.g. ``/users/octocat/events``.
        :param params: Optional query parameters to include in the request.
        :return: Parsed JSON response as a dict or list.
        """
        url = f"{REST_API_URL}{path}"
        logger.debug("GET %s params=%s", path, params)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def query(self, query_string: str, variables: dict | None = None) -> dict:
        """Execute a GraphQL query and return the parsed response.

        :param query_string: GraphQL query string.
        :param variables: Optional mapping of GraphQL variable names to values.
        :raises RuntimeError: When the response contains GraphQL errors or is malformed.
        :return: Full parsed response dict including the ``data`` key.
        """
        payload = {'query': query_string}
        if variables:
            payload['variables'] = variables
        logger.debug("GraphQL query variables=%s", list(variables.keys()) if variables else None)
        response = requests.post(
            API_URL,
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "errors" in data:
            raise RuntimeError(f"GitHub GraphQL returned errors: {data['errors']}")
        if not isinstance(data, dict) or "data" not in data:
            raise RuntimeError(f"Unexpected GitHub response (no 'data'): {data}")
        return data

    def paginated_query(self, query_string: str, username: str, process_fn: Callable[[dict], None]) -> None:
        """Execute a paginated GraphQL query over a user's repositories.

        Iterates through all pages, calling *process_fn* with each page's
        raw response until ``hasNextPage`` is false.

        :param query_string: GraphQL query string with ``$cursor`` variable support.
        :param username: GitHub username passed as the ``$username`` variable.
        :param process_fn: Callable invoked with each page's raw response dict.
        """
        cursor = None
        has_next_page = True
        page_count = 0
        logger.debug("starting paginated query for user %s", username)

        while has_next_page:
            variables = {'username': username, 'cursor': cursor}
            result = self.query(query_string, variables)

            process_fn(result)
            page_count += 1

            page_info = self._extract_page_info(result)
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')

        logger.debug("paginated query complete for user %s: %d page(s)", username, page_count)

    def paginated_org_query(self, query_string: str, org: str, process_fn: Callable[[dict], None]) -> None:
        """Execute a paginated GraphQL query over an organisation's repositories.

        Iterates through all pages, calling *process_fn* with each page's
        raw response until ``hasNextPage`` is false.

        :param query_string: GraphQL query string with ``$cursor`` variable support.
        :param org: GitHub organisation login passed as the ``$org`` variable.
        :param process_fn: Callable invoked with each page's raw response dict.
        """
        cursor = None
        has_next_page = True
        page_count = 0
        logger.debug("starting paginated org query for org %s", org)

        while has_next_page:
            variables = {'org': org, 'cursor': cursor}
            result = self.query(query_string, variables)

            process_fn(result)
            page_count += 1

            page_info = self._extract_org_page_info(result)
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')

        logger.debug("paginated org query complete for org %s: %d page(s)", org, page_count)

    def _extract_page_info(self, result: dict) -> dict:
        try:
            return result['data']['user']['repositories']['pageInfo']
        except (KeyError, TypeError):
            return {}

    def _extract_org_page_info(self, result: dict) -> dict:
        try:
            return result['data']['organization']['repositories']['pageInfo']
        except (KeyError, TypeError):
            return {}
