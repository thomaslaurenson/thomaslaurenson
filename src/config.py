import os
from dotenv import load_dotenv

load_dotenv()

GH_TOKEN = os.getenv('GH_TOKEN')
GH_USERNAME = os.getenv('GH_USERNAME')
API_URL = 'https://api.github.com/graphql'

if not GH_TOKEN:
    raise ValueError('GH_TOKEN not found in environment variables')
if not GH_USERNAME:
    raise ValueError('GH_USERNAME not found in environment variables')