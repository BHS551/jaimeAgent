# JSON schema definitions for functions exposed to the LLM
FUNCTIONS = [
    {
        "name": "write_file",
        "description": "Append content to an existing file or create it, creating parent directories if needed",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path to modify/create (supports ~ for home)",
                },
                "content": {"type": "string", "description": "Content to append"},
            },
            "required": ["path", "content"],
        },
        "context": "write_file",
    },
    {
        "name": "modify_file",
        "description": "Append content to an existing file or create it, creating parent directories if needed",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path to modify/create (supports ~ for home)",
                },
                "content": {"type": "string", "description": "Content to append"},
            },
            "required": ["path", "content"],
        },
        "context": "write_file",
    },
    {
        "name": "read_file",
        "description": "If the path is a file, read its content. If it is a directory, return a JSON list of files in it",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "smart_modify_file",
        "description": "Read a file, apply high-level instructions via the LLM, and overwrite it",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File to update (supports ~ for home)",
                },
                "instructions": {
                    "type": "string",
                    "description": "Natural-language description of how to change the file",
                },
            },
            "required": ["path", "instructions"],
        },
    },
    {
        "name": "git_add",
        "description": "Stage all changes in the specified folder for commit",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Path of the folder to stage changes",
                }
            },
            "required": ["folder_path"],
        },
    },
    {
        "name": "git_commit",
        "description": "Commit staged changes to the local git repository",
        "parameters": {
            "type": "object",
            "properties": {
                "commit_message": {
                    "type": "string",
                    "description": "Commit message for the changes",
                },
                "folder_path": {
                    "type": "string",
                    "description": "The folder path to commit changes from",
                },
            },
            "required": ["commit_message", "folder_path"],
        },
    },
    {
        "name": "git_push",
        "description": "Handles the git push event.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "The folder path to push changes from",
                },
            },
            "required": ["folder_path"],
        },
    },
    {
        "name": "git_diff",
        "description": "Show git diff between local changes and the remote HEAD for the current branch",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Path of the Git repository to diff",
                }
            },
            "required": ["folder_path"],
        },
    },
]
# New function schema for the git pull functionality
FUNCTIONS.append(
    {
        "name": "git_pull",
        "description": "Handles the git pull operation to fetch updates from a remote repository",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "The folder path to pull changes in",
                },
                "rebase": {
                    "type": "boolean",
                    "description": "A boolean indicating whether to rebase the changes or not",
                },
            },
            "required": ["folder_path", "rebase"],
        },
    }
)
# New function schema for the git checkout functionality
FUNCTIONS.append(
    {
        "name": "create_git_branch",
        "description": "The create_git_branch function will operate within a specified folder path (absolute path) to create a new branch in Git. This function will first check the current branch and then create the new branch based on the user's input.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "The folder path to pull changes in",
                },
                "branch_name": {
                    "type": "string",
                    "description": "The name of the new branch to create",
                },
            },
            "required": ["folder_path", "branch_name"],
        },
    }
)
