from dotenv import load_dotenv
import os
load_dotenv()

# CONFIG VARIABLES
# ================

DATA_DIR = "./temp"
COMMIT_LIST_FILE = "commits_list.txt"
REST_API_HEADER = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
    "X-GitHub-Api-Version": "2022-11-28"
}

# CONSTANTS
# =========

COMMIT_REST_API_URI = "https://api.github.com/repos/{0}/{1}/commits"
GRAPHQL_API_URL = "https://api.github.com/graphql"