from dataclasses import dataclass
import requests
from urllib.parse import urlparse
import base64
import re
from typing import Optional, List

@dataclass
class GithubRepoSpec:
    """
    Specifies a specific github repository
    """
    owner: str
    repo: str
    branch: str

class GithubRepo:
    """
    Handle to interact with with GH repo like FS.
    """

    def __init__(self, url_or_repo_spec: str, api_key: str):
        """
        Create a new GithubRepo for interacting with a GH-hosted repository
        REPO_SPEC can be an URL 
        """

        self.repo_spec = GithubRepo._parse_repo_spec(url_or_repo_spec)
        self.api_key = api_key
        
    def _parse_repo_spec(url_or_repo_spec) -> GithubRepoSpec:
        "Parse GithubRepoSpec from given provided specifier string"
        res = urlparse(url_or_repo_spec).path.removeprefix("/")
        [owner, repo] = res.split('/')
        return GithubRepoSpec(owner, repo, 'main') #TODO(leo): always main for now

    def open(self, path: str) -> Optional[str]:
        """
        Return contents of file at path, if any
        """
        url = f"https://api.github.com/repos/{self.repo_spec.owner}/{self.repo_spec.repo}/contents/{path}"
        r = requests.get(
            url,
            headers={
                "authorization": f"Bearer {self.api_key}",
                "accept": "application/vnd.github+json",
            })
        f = r.json()

        if isinstance(f, dict) and f.get('type') == 'file':
            return decode(f['content'])
        else:
            return None

    def find_file(self, pat: str) -> List[str]:
        """
        Returns a list of paths in this GH repo with filenames that match given pattern
        """
        pat = re.compile(pat)
        url = f"https://api.github.com/repos/{self.repo_spec.owner}/{self.repo_spec.repo}/git/trees/{self.repo_spec.branch}?recursive=1"

        # TODO(leo): Cache?
        r = requests.get(
            url,
            headers={
                "authorization": f"Bearer {self.api_key}",
                "accept": "application/vnd.github+json",
            })
        resp = r.json()
        return [f['path'] for f in resp['tree'] if pat.search(f['path']) ]

    def search(self, query: str) -> List[str]:
        """
        Returns a list of paths in this GH repo for given query
        """
        url = f"https://api.github.com/search/code?q={query}+repo:{self.repo_spec.owner}/{self.repo_spec.repo}"
        r = requests.get(url,
                         headers={
                             "authorization": f"Bearer {self.api_key}",
                             "accept": "application/vnd.github+json",
                         })
                             
        resp = r.json()
        return [f['path'] for f in resp['items']]

        
def decode(content):
    ascii_bytes = content.encode("ascii")
    return base64.b64decode(ascii_bytes).decode("ascii")
