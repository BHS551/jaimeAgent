# JSON schema definitions for functions exposed to the LLM
FUNCTIONS = [
    {
        "name": "write_file",
        "description": "Append content to an existing file or create it, creating parent directories if needed",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to modify/create (supports ~ for home)"},
                "content": {"type": "string", "description": "Content to append"}
            },
            "required": ["path", "content"]
        },
        "context": "write_file"
    },
    {
        "name": "modify_file",
        "description": "Append content to an existing file or create it, creating parent directories if needed",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to modify/create (supports ~ for home)"},
                "content": {"type": "string", "description": "Content to append"}
            },
            "required": ["path", "content"]
        },
        "context": "write_file"
    },
    {
        "name": "read_file",
        "description": "If the path is a file, read its content. If it is a directory, return a JSON list of files in it",
        "parameters": {
            "type": "object",
            "properties": {
            "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "smart_modify_file",
        "description": "Read a file, apply high-level instructions via the LLM, and overwrite it",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File to update (supports ~ for home)"
                },
                "instructions": {
                    "type": "string",
                    "description": "Natural-language description of how to change the file"
                }
            },
            "required": ["path", "instructions"]
        }
    },
    {
        "name": "git_add",
        "description": "Stage all changes in the specified folder for commit",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Path of the folder to stage changes"}
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "git_commit",
        "description": "Commit staged changes to the local git repository",
        "parameters": {
            "type": "object",
            "properties": {
                "commit_message": {"type": "string", "description": "Commit message for the changes"},
            },
            "required": ["commit_message"]
        }
    },
    {
        "name": "git_push",
        "description": "Handles the git push event.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "The folder path to push changes from"},
            },
            "required": ["branch_name", "remote"]
        }
    }
]# New function schema for the git pull functionality
FUNCTIONS.append({
    "name": "perform_git_pull",
    "description": "Handles the git pull operation to fetch updates from a remote repository",
    "parameters": {
        "repository_url": {"type": "string", "description": "The URL of the remote Git repository to pull updates from."},
        "local_dir": {"type": "string", "description": "The path to the local directory where the repository is cloned."},
        "auth_credentials": {"type": "object", "description": "Any credentials required for accessing the remote repository, if applicable."}
    },
    "outputs": {
        "update_log": {"type": "string", "description": "Log of the changes retrieved from the remote repository, indicating which files were updated, added, or removed."},
        "success_message": {"type": "string", "description": "Message indicating whether the pull operation succeeded or failed."}
    },
    "expected_behavior": [
        "Executes the git pull command in the specified local directory.",
        "Handles errors gracefully and provides clear feedback to the user.",
        "Updates the user with a summary of changes upon successful pull."
    ]
})