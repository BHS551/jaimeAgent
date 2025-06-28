# handlers/git_pull.py
import logging
import subprocess
from pathlib import Path

def handle(folder_path: str, rebase: bool = False) -> str:
    """Perform 'git pull' (or 'git pull --rebase') in the specified repository path."""
    logging.debug(f"git_pull handler received folder_path: {folder_path}, rebase: {rebase}")

    repo_root = Path(folder_path).expanduser().resolve()
    if not (repo_root / '.git').is_dir():
        return f"❌ Error: no git repository found at {repo_root}"

    cmd = ["git", "pull"]
    if rebase:
        cmd.append("--rebase")

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
            return f"✅ Pull successful in {repo_root}{(' with rebase' if rebase else '')}: {output}"
        err = proc.stderr.strip() or proc.stdout.strip()
        return f"❌ git pull failed in {repo_root}: {err}"
    except Exception as e:
        logging.error(f"git_pull exception: {e}")
        return f"❌ Error in git_pull handler: {e}"