#%%
import os
import re
import csv
import utils
import typer
import config
from classes import Commit
from rich.console import Console
app = typer.Typer()
console = Console()

@app.command
def measure(task_name: str, repo_url: str):
    # File paths for the task
    task_path = os.path.join(config.DATA_DIR, task_name)
    meta_path = os.path.join(task_path, config.META_FILE)
    result_path = os.path.join(task_path, config.RESULT_FILE)

    task = "normal" # task type
    owner, repo = utils.get_owner_and_repo_from_url(repo_url)

    # Setup task dir or resume if exists
    if os.path.exists(meta_path):
        task = "resume"
    else:
        os.makedirs(task_path)

    # %%
    # Endpoint to fetch commits
    uri = config.COMMIT_REST_API_URI.format(owner, repo)

    ## get commit to start with
    if task == "normal":
        # Start with latest commit
        params = {"per_page": "1"}
        response = utils.get_commits(uri=uri, params=params)
        start = response.json()[0]["sha"]
        end = ""
    else:
        # Start with the last commit pocessed in the last process
        with open(meta_path, "r") as f:
            start, end = f.readline().split(",")
            start = end
    #%%
    ## Start getting commits in batch
    params = {"sha": start, "per_page": config.PER_PAGE}

    # Pattern to get link for next page from the `Link` header
    next_pattern = "(?<=<)([\\S]*)(?=>; rel=\"Next\")" 
    pageRemaining = True

    # CSV file to store the data
    result = open(result_path, 'a', newline='')
    csv_writer = csv.writer(result)
    csv_writer.writerow(config.RESULT_HEADER) if task == 'normal' else ''

    total_scanned = 0
    with console.status("[bold green]Scanning repo...") as status:
        while pageRemaining:
            response = utils.get_commits(uri=uri, params=params)
            links = response.headers.get("link", None)
            commits = response.json()
            del response

            # Process commits per page
            data = []
            for i in range(len(commits)):
                commit = Commit.from_dict(commits[i])
                if commit.sha == end:
                    # Skip the last processed commit if resuming
                    continue
                commit = utils.check_verification_status(commit)
                end = commit.sha
                data.append([commit.sha, commit.details.committer.date, commit.details.verification.verified, commit.details.verification.reason])

            # Write data to csv
            csv_writer.writerows(data)

            # Log the last commit processed 
            with open(meta_path, "w") as f:
                f.write(f"{start},{end}")
            
            # Get the link to next page
            if links is None:
                break
            is_next = re.search(next_pattern, links, re.IGNORECASE)
            if is_next is None:
                pageRemaining = False
            else:
                uri = is_next.group()
            total_scanned += len(data)
            if total_scanned % 500 == 0:
                console.print(f"Scanned {total_scanned} commits")

    result.close()
# %%
