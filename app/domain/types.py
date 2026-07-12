import json
from dataclasses import dataclass
from typing import TypedDict

type HTML = str


class JSONPage(TypedDict):
    pid: str
    body: HTML


@dataclass
class Page:
    pid: str
    body: HTML
    status: int | None = None

    def to_json(self) -> str:
        return json.dumps({"pid": self.pid, "body": self.body})

    @classmethod
    def from_json(cls, message: JSONPage) -> "Page":
        return cls(pid=message["pid"], body=message["body"])
