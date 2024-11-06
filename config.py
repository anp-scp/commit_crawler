from dotenv import load_dotenv
import os
load_dotenv()

# CONFIG VARIABLES
# ================

DATA_DIR = "./temp"
RESULT_FILE = "results.csv"
META_FILE = "meta.txt"
REPO_NAME = "name.txt"
REST_API_HEADER = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
    "X-GitHub-Api-Version": "2022-11-28"
}
PER_PAGE = '5'

# CONSTANTS
# =========

COMMIT_REST_API_URI = "https://api.github.com/repos/{0}/{1}/commits"
GRAPHQL_API_URL = "https://api.github.com/graphql"
RESULT_HEADER = ["SHA", "DATE", "STATUS", "REASON"]