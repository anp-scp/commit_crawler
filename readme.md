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
│ analyze   To analyze the commits counts of a task                                                                           │
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

```bash
❯ python app.py analyze --help
                                                                                                             
 Usage: app.py analyze [OPTIONS]                                                                             
                                                                                                             
 To analyze the commits counts of a task                                                                     
                                                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --task-name                    TEXT     Task name to analyze [default: None] [required]                │
│    --topk                         INTEGER  Get to k max committers (Likely bots) [default: 5]             │
│    --bots                         TEXT     Comma separated email of bots                                  │
│    --percent      --no-percent             Want value as percent? [default: no-percent]                   │
│    --help                                  Show this message and exit.                                    │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Running the above command will give analysis without excluding blots. Check the tok contributors to get
likely bots and use it in the --bots option.

For example:

```bash
❯ python app.py analyze --task-name aiml1 --bots "gardener@tensorflow.org"
Total commits: 78824

 Top committers (Likely bots):

COMMITTER
gardener@tensorflow.org                67030
noreply@github.com                      1745
yong.tang.github@outlook.com             291
vikoth18@in.ibm.com                      278
advaitjain@users.noreply.github.com      270
Name: count, dtype: int64

Proportion of verified commits:

+------------+---------+---------------------------+
|            | Overall | Excluding bots and GH web |
+------------+---------+---------------------------+
|  Verified  |  2085   |            340            |
| Unverified |  76739  |           9709            |
+------------+---------+---------------------------+

Proportion of specific reasons for unverified commits:

+------------------+---------+---------------------------+
|                  | Overall | Excluding bots and GH web |
+------------------+---------+---------------------------+
|     unsigned     |  76431  |           9401            |
|      valid       |  2085   |            340            |
|   unknown_key    |   24    |            24             |
|     no_user      |    6    |             6             |
| unverified_email |   278   |            278            |
+------------------+---------+---------------------------+

Yearwise distribution of valid commits excluding bots and GH web:

+-------+----------+-------+
|       | Verified | Total |
+-------+----------+-------+
| 20-21 |    86    | 5280  |
| 21-22 |   229    | 2321  |
| 22-23 |    10    | 1638  |
| 23-24 |    15    |  810  |
+-------+----------+-------+
```
## FAQ

1. Why automated bot detection not possible???

    GitHub API provides account type attribute with values `Bot` and `User`. Bit is not used correclty by the users.
    For example, pytorchmergebot is a bot but it is not marked as a bot. So, using API does not seem to be reliable way
    to detect bots

2. What about unlabeled commits?

    GitHub API marks the unlabeled commits as `Unverified`. Now, if the user has enabled the Vigilant mode than `Unverified` badge
    will be shown in GH Web. But, if the user has not enabled the Vigilant mode than there will be no badge in the web UI.

    This is not possible to detect via API and Selenium based crawler would be needed to detect the use of Vigilant mode.
    This is possible to implement but goes against the GitHub's robots.txt policy.