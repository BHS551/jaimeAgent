# handlers/git_commit.py
import logging
import subprocess
from pathlib import Path

def handle(commit_message: str, folder_path: str = None) -> str:
    """Git commit with the given message in the specified repo path or nearest parent."""
    logging.debug(f"git_commit handler received message: '{commit_message}', folder_path: '{folder_path}'")

    # Determine repository root
    if folder_path:
        repo_root = Path(folder_path).expanduser().resolve()
        if not (repo_root / '.git').is_dir():
            return f"❌ Error: no git repository found at {repo_root}"
    else:
        current = Path('.').resolve()
        repo_root = None
        for parent in [current] + list(current.parents):
            if (parent / '.git').is_dir():
                repo_root = parent
                break
        if repo_root is None:
            return "❌ Error: no git repository found in current directory or parents."

    # Execute git commit
    try:
        proc = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Success
        if proc.returncode == 0:
            out = proc.stdout.strip()
            return f"✅ Commit successful in {repo_root}: {out or commit_message}"
        # Handle no-op
        err = proc.stderr.strip() or proc.stdout.strip()
        if 'nothing to commit' in err.lower():
            return f"ℹ️ Nothing to commit in {repo_root}: working tree clean"
        # Other errors
        return f"❌ git commit failed in {repo_root}: {err}"
    except Exception as e:
        logging.error(f"git_commit exception: {e}")
        return f"❌ Error in git_commit handler: {e}"
