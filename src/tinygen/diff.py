import difflib
from typing import Optional

def unified_diff(path: str, old_content: Optional[str], new_content: Optional[str]) -> Optional[str]:
    """
    Returns a unified diff for a file at PATH that changed from old_content to new_content.
    If there was no changes, returns None
    """
    # treat None content as deletions
    old_path = "a/" + path if old_content else "/dev/null"
    new_path = "b/" + path if new_content else "/dev/null"
    old_content = old_content or ""
    new_content = new_content or ""

    if old_content == new_content:
        return None

    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=old_path,
        tofile=new_path,
    )
    diff_text = "".join(diff) + "\n"
    return diff_text
