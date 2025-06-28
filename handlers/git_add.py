# handlers/git_add.py
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

def handle(folder_path: str) -> str:
    """Git-add a file or directory, detecting the repo root automatically."""
    target = Path(folder_path).expanduser().resolve()
    logging.debug(f"git_add handler received path: {target}")

    # Ensure the target exists
    if not target.exists():
        return f"❌ Error: path not found: {target}"

    # Locate the git repository root by walking up from target
    repo_root = None
    current = target if target.is_dir() else target.parent
    while True:
        if (current / '.git').exists():
            repo_root = current
            break
        if current.parent == current:
            break
        current = current.parent
    if repo_root is None:
        return f"❌ Error: no git repository found for path: {target}"

    # Compute path relative to repo root
    try:
        rel_path = target.relative_to(repo_root)
    except ValueError:
        rel_path = target

    # Run git add
    try:
        subprocess.run(
            ["git", "add", str(rel_path)],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return f"✅ Staged '{rel_path}' in repo '{repo_root}'"
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() or e.stdout.strip()
        logging.error(f"git add error: {stderr}")
        return f"❌ git add failed: {stderr}"