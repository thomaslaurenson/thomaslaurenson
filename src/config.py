import logging
import os

GH_TOKEN = os.getenv('GH_TOKEN')
GH_USERNAME = os.getenv('GH_USERNAME')
API_URL = 'https://api.github.com/graphql'

if not GH_TOKEN:
    raise ValueError('GH_TOKEN not found in environment variables')
if not GH_USERNAME:
    raise ValueError('GH_USERNAME not found in environment variables')

# LOG_LEVEL controls verbosity: "NONE" (silent), "INFO" (summary), "DEBUG" (includes API calls).
# Can also be overridden via the LOG_LEVEL environment variable.
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "NONE").upper()

_level_map = {"NONE": logging.WARNING, "INFO": logging.INFO, "DEBUG": logging.DEBUG}
logging.basicConfig(
    level=_level_map.get(LOG_LEVEL, logging.WARNING),
    format="%(name)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# Per-org configuration — controls which orgs contribute to star and language stats.
ORG_CONFIG = [
    {"name": "thegraydot", "stars": True, "languages": True},
    {"name": "UoA-eResearch", "stars": False, "languages": False},
    {"name": "UoA-SRE", "stars": False, "languages": False},
]

STARS_ORGS = [o["name"] for o in ORG_CONFIG if o["stars"]]
LANGUAGES_ORGS = [o["name"] for o in ORG_CONFIG if o["languages"]]
