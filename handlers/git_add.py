import os
import subprocess


def handle(folder_path: str) -> str:
    """
    Stage every change inside the given folder (recursively).

    Parameters
    ----------
    folder_path : str
        Relative or absolute path to a directory in the repository.
    """
    if not folder_path:
        return "❌ folder_path is required"

    abs_path = os.path.abspath(os.path.expanduser(folder_path))
    if not os.path.isdir(abs_path):
        return f"❌ Not a directory: {abs_path}"

    # Stage everything under the folder
    subprocess.check_call(["git", "add", abs_path])
    return f"✅ staged all changes in {folder_path!r}"
