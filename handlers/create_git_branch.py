# New Git Branch Creation Functionality

def create_git_branch(folder_path, new_branch_name):
    """
    Create a new Git branch in the specified folder.
    """
    import os
    import subprocess

    # Change directory to the specified folder path
    os.chdir(folder_path)

    # Check the current branch
    current_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    print(f'Current branch: {current_branch}')

    # Create a new branch
    subprocess.call(['git', 'checkout', '-b', new_branch_name])
    print(f'New branch created: {new_branch_name}')

    # Verify creation
    new_branch_check = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    if new_branch_check == new_branch_name:
        print(f'Successfully created and switched to branch: {new_branch_name}')
    else:
        print(f'Failed to create branch: {new_branch_name}')# New Git Branch Creation Functionality

def create_git_branch(folder_path, new_branch_name):
    import os
    import subprocess
    
    # Step 2: Change Directory
    os.chdir(folder_path)
    
    # Step 3: Check Current Branch
    current_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    print(f'Current branch: {current_branch}')
    
    # Step 4: Create New Branch
    subprocess.check_call(['git', 'checkout', '-b', new_branch_name])
    
    # Step 5: Confirm Creation
    new_branch_created = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    if new_branch_created == new_branch_name:
        print(f'Branch {new_branch_name} created successfully.')
    else:
        print('Failed to create branch.')