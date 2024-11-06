#%%
import os
import httpx
import typer
import config
import subprocess
from rich.console import Console
console = Console()



def get_owner_and_repo_from_url(repo_url: str) -> tuple:
    """Extract owner and repo name from repo URL

    Parameters
    ----------
    repo_url : str
        Repo URL

    Returns
    -------
    typle
        Tuple containing owner and repo name
    """
    repo_url = repo_url.split("/")
    owner = repo_url[3]
    repo_name = repo_url[4].replace(".git", "")
    return owner, repo_name



