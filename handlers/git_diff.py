# handlers/git_diff.py
import logging
import subprocess
from pathlib import Path

def handle(folder_path: str) -> str:
    """
    Show git diff between local changes and remote HEAD for the current branch.
    Decodes all output as UTF-8 (errors replaced) to avoid Windows codec errors,
    and safely handles missing stderr/stdout.
    """
    logging.debug(f"git_diff handler received folder_path: {folder_path}")
    repo_root = Path(folder_path).expanduser().resolve()
    if not (repo_root / '.git').is_dir():
        return f"❌ Error: no git repository found at {repo_root}"

    try:
        # Fetch remote (no merge), decoding as UTF-8 and replacing errors
        subprocess.run(
            ["git", "fetch"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            check=True
        )

        # Find current branch
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        branch = (branch_proc.stdout or "").strip()

        # Produce diff against origin/<branch>
        diff_proc = subprocess.run(
            ["git", "diff", "--no-color", f"origin/{branch}"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace"
        )
        diff_text = (diff_proc.stdout or "").strip()

        if diff_text:
            return f"✅ Diff for branch '{branch}':\n{diff_text}"
        else:
            return f"ℹ️ No differences between local '{branch}' and 'origin/{branch}'"

    except subprocess.CalledProcessError as e:
        # Safely extract stderr/stdout, strip None
        err = ((e.stderr or "") + (e.stdout or "")).strip()
        logging.error(f"git_diff error: {err}")
        return f"❌ git diff failed: {err}"

    except Exception as e:
        logging.error(f"git_diff exception: {e}")
        return f"❌ Error in git_diff handler: {e}"
