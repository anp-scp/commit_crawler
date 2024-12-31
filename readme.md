## Install Requirements

```bash
pip install -r requirements.txt

```

## Setup

Create a .env file with the following content:

```
AUTH_TOKEN=<your github auth token>
```

## List available commands:

```bash
python app.py --help

╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ list      List existing tasks                                                                                               │
│ measure   To fetch and process the commits from given repository (main branch). Task name is to differentitae between jobs  │
│ remove    To delete a task                                                                                                  │
│ rlimit    To get reamining rate limit                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Crawl commits for a repo:


### Format:
```bash
python app.py measure <task_name> <repo_url>
```

For example:

```bash
python app.py measure aiml3 https://github.com/tensorflow/tensorflow 
```

The data will be stored at <task_name>/<results.csv>


## List existing tasks:

```bash
❯ python app.py list
                         Task                         
┏━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Sl No.: ┃ Task Name ┃ Repo Name                    ┃
┡━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│       0 │ aiml1     │ pytorch/pytorch              │
│       1 │ aiml2     │ jax-ml/jax                   │
│       2 │ aiml3     │ tensorflow/tensorflow        │
│       3 │ db1       │ MariaDB/server               │
│       4 │ db2       │ mongodb/mongo                │
│       5 │ db3       │ neo4j/neo4j                  │
│       6 │ sec1      │ casbin/casbin                │
│       7 │ sec2      │ rapid7/metasploit-framework  │
│       8 │ sec3      │ zaproxy/zaproxy              │
│       9 │ sigstore1 │ sigstore/cosign              │
│      10 │ sigstore2 │ sigstore/gitsign             │
│      11 │ webdev1   │ encode/django-rest-framework │
│      12 │ webdev2   │ django/django                │
│      13 │ webdev3   │ facebook/react               │
└─────────┴───────────┴──────────────────────────────┘
```

### Analysis

Use `analysis.ipynb` as an example for analysis.

