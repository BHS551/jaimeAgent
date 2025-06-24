import subprocess

def handle(folder_path):
    try:
        subprocess.run(['git', 'push'], cwd=folder_path, check=True)
        print('Push successful')
    except subprocess.CalledProcessError:
        print('Error during push')
