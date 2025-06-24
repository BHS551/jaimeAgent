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
        "description": "Read a text file or list all files in a directory",
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
                "folder_path": {"type": "string", "description": "The name of the branch to push"}
            },
            "required": ["branch_name", "remote"]
        }
    }
]