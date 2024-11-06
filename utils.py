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

def get_commits(uri: str, params: dict =None) -> httpx.Response:
    """Utility to fetch commitss by performing REST get call based on given Endpoint
    and query params

    Parameters
    ----------
    uri : str
        REST API Endpoint
    params : dict, optional
        Query Params, by default None

    Returns
    -------
    httpx.Response
        HTTP Response from REST Endpoint

    Raises
    ------
    typer.Exit
        Exits if unexpected status code
    """
    with httpx.Client() as client:
        response = client.get(
            uri,
            headers=config.REST_API_HEADER,
            params=params
        )
    if response.status_code == httpx.codes.OK:
        return response
    else:
        console.print(f"Response status: {response.status_code}")
        console.print(response.json())
        raise typer.Exit(1)

