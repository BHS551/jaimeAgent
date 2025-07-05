import subprocess

def handle(folder_path: str):
    try:
        result = subprocess.run(['flake8', folder_path], cwd=folder_path, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f'❌ Error running linter: {e}'}