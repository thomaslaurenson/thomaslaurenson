import logging
from collections.abc import Callable

import requests

from src.config import API_URL, GH_TOKEN

REST_API_URL = 'https://api.github.com'

logger = logging.getLogger(__name__)


class GitHubClient:

    def __init__(self) -> None:
        self.headers = {
            'Authorization': f'Bearer {GH_TOKEN}',
            'Content-Type': 'application/json',
        }

    def get_rest(self, path: str, params: dict | None = None) -> dict | list:
        url = f"{REST_API_URL}{path}"
        logger.debug("GET %s params=%s", path, params)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def query(self, query_string: str, variables: dict | None = None) -> dict:
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
        cursor = None
        has_next_page = True

        while has_next_page:
            variables = {'username': username, 'cursor': cursor}
            result = self.query(query_string, variables)

            process_fn(result)

            page_info = self._extract_page_info(result)
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')

    def paginated_org_query(self, query_string: str, org: str, process_fn: Callable[[dict], None]) -> None:
        cursor = None
        has_next_page = True

        while has_next_page:
            variables = {'org': org, 'cursor': cursor}
            result = self.query(query_string, variables)

            process_fn(result)

            page_info = self._extract_org_page_info(result)
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')

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
