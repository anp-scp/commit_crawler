#%%
import os
import re
import csv
import utils
import typer
import config
import pandas as pd
from classes import Commit
from rich.table import Table
from tabulate import tabulate
from rich.console import Console
from typing_extensions import Annotated
app = typer.Typer()
console = Console()


@app.command()
def remove(task_name: str):
    """To delete a task"""
    utils.clean(task_name)

@app.command()
def analyze(
    task_name: Annotated[str, typer.Option(help="Task name to analyze")],
    topk: Annotated[int, typer.Option(help="Get to k max committers (Likely bots)") ] = 5,  
    bots: Annotated[str, typer.Option(help="Comma separated email of bots")] = "", 
    percent: Annotated[bool, typer.Option(help="Want value as percent?")] = False
):
    """To analyze the commits counts of a task"""
    # Parse bots
    if bots == "":
        console.print("WARNING: No bots provided. Will not exclude bots", style="bold red")
        bots = []
    else:
        bots = [bot.strip() for bot in bots.split(",")]

    # Read the data
    path = os.path.join(config.DATA_DIR, task_name, config.RESULT_FILE)
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        console.print("Task not found", style="bold red")
        return
    df['COMMIT_DATE'] = pd.to_datetime(df['COMMIT_DATE'], format='%Y-%m-%dT%H:%M:%SZ')
    excludingBotsAndWebs = df[(df['COMMITTER'] != 'noreply@github.com') & (~df['COMMITTER'].isin(bots))]

    ## Some related info
    console.print(f"Total commits: {len(df)}\n")
    console.print("[u] Top committers (Likely bots):[/u]\n")
    print(df['COMMITTER'].value_counts().head(topk), end="\n\n")

    ## Proportions of verified commits
    console.print("[u]Proportion of verified commits:[/u]\n")
    data = {
        "Overall": [df['STATUS'].value_counts().to_dict().get(True,0), df['STATUS'].value_counts().to_dict().get(False,0)],
        "Excluding bots and GH web": [excludingBotsAndWebs['STATUS'].value_counts().to_dict().get(True,0), excludingBotsAndWebs['STATUS'].value_counts().to_dict().get(False,0)]
    }
    data = pd.DataFrame(data, index=["Verified", "Unverified"])
    if percent:
        data = data.div(data.sum(axis=0), axis=1) * 100
    print(tabulate(data, headers=data.columns, tablefmt="pretty"))

    ## Proportions of specific reasons
    console.print("\n[u]Proportion of specific reasons for unverified commits:[/u]\n")

    data = pd.DataFrame(index=df['REASON'].unique().tolist())
    data["Overall"] = 0
    data["Excluding bots and GH web"] = 0
    temp = df['REASON'].value_counts()
    temp.name = "Overall"
    data.update(temp)

    temp = excludingBotsAndWebs['REASON'].value_counts()
    temp.name = "Excluding bots and GH web"
    data.update(temp)
    if percent:
        data = data.div(data.sum(axis=0), axis=1) * 100
    print(tabulate(data, headers=data.columns, tablefmt="pretty"))

    ## Yearwise distribution of valid commits excluding bots and GH web
    console.print("\n[u]Yearwise distribution of valid commits excluding bots and GH web:[/u]\n")
    
    data = pd.DataFrame(index=["20-21","21-22","22-23","23-24"], data={
        "Verified": [
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] < '2021-04-28')]['REASON'].value_counts().to_dict().get("valid", 0),
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] >= '2021-04-28') & (excludingBotsAndWebs['COMMIT_DATE'] < '2022-04-28')]['REASON'].value_counts().to_dict().get("valid", 0),
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] >= '2022-04-28') & (excludingBotsAndWebs['COMMIT_DATE'] < '2023-04-28')]['REASON'].value_counts().to_dict().get("valid", 0),
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] >= '2023-04-28')]['REASON'].value_counts().to_dict().get("valid", 0)
        ],
        "Total": [
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] < '2021-04-28')].shape[0],
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] >= '2021-04-28') & (excludingBotsAndWebs['COMMIT_DATE'] < '2022-04-28')].shape[0],
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] >= '2022-04-28') & (excludingBotsAndWebs['COMMIT_DATE'] < '2023-04-28')].shape[0],
            excludingBotsAndWebs[(excludingBotsAndWebs['COMMIT_DATE'] >= '2023-04-28')].shape[0]
        ]
    })
    print(tabulate(data, headers=data.columns, tablefmt="pretty"))

@app.command()
def measure(task_name: str, repo_url: str):
    """To fetch and process the commits from given repository (main branch).
    Task name is to differentitae between jobs
    """
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
        with open(os.path.join(task_path, config.REPO_NAME), 'w') as f:
            f.write(f"{owner}_{repo}")

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
    params = {"sha": start, "per_page": config.PER_PAGE, "since": config.COMMIT_SINCE}

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
                data.append([
                    commit.sha, commit.details.committer.date, commit.details.author.email,
                    commit.details.committer.email, commit.details.verification.verified,
                    commit.details.verification.reason
                ])

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
            if total_scanned % 200 == 0:
                print(f"Scanned {total_scanned} commits")

    result.close()

@app.command()
def list():
    """List existing tasks
    """
    if not os.path.exists(config.DATA_DIR):
        console.print("No tasks exist")
        return
    
    table = Table(title="Task")
    table.add_column("Sl No.:", justify="right")
    table.add_column("Task Name")
    table.add_column("Repo Name")
    task_list = sorted(os.listdir(config.DATA_DIR))
    for i, task in enumerate(task_list):
        with open(os.path.join(config.DATA_DIR, task, config.REPO_NAME), 'r') as f:
            repo_name = f.read()
        table.add_row(str(i), task, repo_name.replace("_", "/"))
    console.print(table)

@app.command(name="rlimit")
def remaining_limit(repo_url: str):
    """To get reamining rate limit"""
    owner, repo = utils.get_owner_and_repo_from_url(repo_url)
    uri = config.COMMIT_REST_API_URI.format(owner, repo)
    params = {"per_page": 1,}
    response = utils.get_commits(uri=uri, params=params)
    console.print(f"Rate limit remaining: {response.headers['X-RateLimit-Remaining']}")
# %%

if __name__ == "__main__":
    app()