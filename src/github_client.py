import requests
from src.config import TOKEN, API_URL


class GitHubClient:

    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json',
        }

    def query(self, query_string, variables=None):
        payload = {'query': query_string}
        if variables:
            payload['variables'] = variables

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

    def paginated_query(self, query_string, username, process_fn):
        cursor = None
        has_next_page = True

        while has_next_page:
            variables = {'username': username, 'cursor': cursor}
            result = self.query(query_string, variables)

            process_fn(result)

            page_info = self._extract_page_info(result)
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')

    def _extract_page_info(self, result):
        try:
            return result['data']['user']['repositories']['pageInfo']
        except (KeyError, TypeError):
            return {}
