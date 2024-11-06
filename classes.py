
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import Any

@dataclass_json
@dataclass
class Committer:
    name: str
    email: str
    date: str

@dataclass_json
@dataclass
class Author:
    name: str
    email: str
    date: str

@dataclass_json
@dataclass
class Verification:
    verified: bool
    reason: str

@dataclass_json
@dataclass
class Commit_Details:
    url: str
    committer: Committer
    author: Author
    verification: Verification

@dataclass_json
@dataclass
class Commit:
    sha: str
    commit_details: Commit_Details = field(metadata=config(field_name="commit"))
