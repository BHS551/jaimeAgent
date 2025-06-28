# handlers/git_push.py
import logging
import subprocess
from pathlib import Path

def handle(folder_path: str) -> str:
    """Perform 'git push' for the current branch in the specified repository path."""
    logging.debug(f"git_push handler received folder_path: {folder_path}")

    # Resolve and verify repository path
    repo_root = Path(folder_path).expanduser().resolve()
    if not (repo_root / '.git').is_dir():
        return f"❌ Error: no git repository found at {repo_root}"

    # Run git push in current branch
    cmd = ["git", "push"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if proc.returncode == 0:
            output = proc.stdout.strip() or ""
            return f"✅ Push successful in {repo_root}: {output}"
        err = proc.stderr.strip() or proc.stdout.strip()
        return f"❌ git push failed in {repo_root}: {err}"
    except Exception as e:
        logging.error(f"git_push exception: {e}")
        return f"❌ Error in git_push handler: {e}"