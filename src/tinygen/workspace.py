from dataclasses import dataclass
from .github import GithubRepo
from typing import Optional, List
from .diff import unified_diff
from .tool import Tool
import re

@dataclass
class Buffer:
    path: str
    orig: str
    edit: Optional[str]

class Workspace:
    """
    The workspace of open buffers and edits.
    """

    def __init__(self, repo: GithubRepo):
        self.repo = repo
        self.buffers = {}

    def open(self, path: str) -> str:
        if path in self.buffers:
            return self.buffers[path]

        contents = self.repo.open(path)
        self.buffers[path] = Buffer(path, contents, contents)
        return contents
        
    def write(self, path: str, content: str):
        if path not in self.buffers:
            _ = self.open(path) # loads buffer
        buf = self.buffers[path]
        buf.edit = content

    def find(self, pat: str) -> List[str]:
        repo_matches = self.repo.find_file(pat)
        buf_matches = [b.path for b in self.buffers.values() if b.path not in repo_matches and query in b.path]
        return buf_matches + repo_matches

    def search(self, query: str) -> List[str]:
        repo_matches = self.repo.search(query)
        buf_matches = [b.path for b in self.buffers.values() if b.path not in repo_matches and query in (b.edits or "")]
        return buf_matches + repo_matches

    def diff(self) -> str:
        diffs = [unified_diff(b.path, b.orig, b.edit) for b in self.buffers.values()]
        return '\n'.join(list(filter(None, diffs)))


def tools(w: Workspace) -> List[Tool]:
    find_tool = Tool(
        "find",
        "find QUERY\nreturns a list of paths contain given QUERY. QUERY is a regular string",
        lambda args: w.find(args[0])
    )

    search_tool = Tool(
        "search",
        "search QUERY\nreturns a list of paths to files containing that match QUERY. QUERY is a regular string",
        lambda args: w.search(args[0])
    )

    open_tool = Tool(
        "open",
        "open PATH\nreturns contents of file at PATH.",
        lambda args: w.open(args[0]) or "EMPTY FILE"
    )

    write_tool = Tool(
        "write",
        "write PATH CONTENT\nwrite CONTENT to the file at PATH. This overwrites existing content if any.",
        lambda args: w.write(args[0], args[1]) or "OK"
    )
    return [find_tool, search_tool, open_tool, write_tool]
