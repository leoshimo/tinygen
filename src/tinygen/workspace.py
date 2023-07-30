from dataclasses import dataclass
from .github import GithubRepo
from typing import Optional, List
from .diff import unified_diff
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
        pat = re.compile(pat)
        buf_matches = [b.path for b in self.buffers.values() if b.path not in repo_matches and pat.search(b.path or "")]
        return buf_matches + repo_matches

    def search(self, query: str) -> List[str]:
        repo_matches = self.repo.search(query)
        buf_matches = [b.path for b in self.buffers.values() if b.path not in repo_matches and (b.edits or "").includes(query)]
        return buf_matches + repo_matches

    def diff(self) -> str:
        diffs = [unified_diff(b.path, b.orig, b.edit) for b in self.buffers.values()]
        return '\n'.join(list(filter(None, diffs)))
