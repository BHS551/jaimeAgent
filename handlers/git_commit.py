def handle(commit_message: str):
    import subprocess
    try:
        # Execute the git commit command with the provided commit message
        result = subprocess.run(['git', 'commit', '-m', commit_message],
                                 check=True,
                                 capture_output=True,
                                 text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f'Error during git commit: {e.stderr}'