import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
USERNAME = os.getenv('USERNAME')
API_URL = 'https://api.github.com/graphql'

if not TOKEN:
    raise ValueError('TOKEN not found in environment variables')

if not USERNAME:
    raise ValueError('USERNAME not found in environment variables')