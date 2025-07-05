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
        "name": "read_file",
        "description": "Read the contents of a file or list a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or directory path"}
            },
            "required": ["path"],
        },
        "context": "read_file",
    },
    {
        "name": "modify_file",
        "description": "Overwrite or create a file with the given content",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path to write (supports ~ for home)",
                },
                "content": {"type": "string", "description": "New file content"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "append_json",
        "description": "Append a JSON object to the end of session_memory.json",
        "parameters": {
            "type": "object",
            "properties": {
                "entry": {
                    "type": "object",
                    "description": "JSON-serializable object to append",
                }
            },
            "required": ["entry"],
        },
    },
    {
        "name": "create_git_branch",
        "description": "Create a new git branch and check it out",
        "parameters": {
            "type": "object",
            "properties": {
                "branch_name": {
                    "type": "string",
                    "description": "Name of the new branch",
                }
            },
            "required": ["branch_name"],
        },
    },
    {
        "name": "git_add",
        "description": "Stage files or folders in the nearest Git repository",
        "parameters": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file or directory paths to add",
                }
            },
            "required": ["paths"],
        },
    },
    {
        "name": "git_commit",
        "description": "Commit staged changes with a message",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"}
            },
            "required": ["message"],
        },
    },
    {
        "name": "git_diff",
        "description": "Show diff between local and remote for the current branch",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Repository root folder",
                }
            },
            "required": ["folder_path"],
        },
    },
]

# 1) Plan & Confirm
FUNCTIONS.extend(
    [
        {
            "name": "outline_plan",
            "description": "Generate a high-level plan of steps before modifying code",
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Summarized project context or relevant code snippets",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "The user’s natural-language task description",
                    },
                },
                "required": ["context", "task_description"],
            },
        },
        {
            "name": "confirm_plan",
            "description": "Ask user to confirm or refine an outlined plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The textual plan steps returned by outline_plan",
                    }
                },
                "required": ["plan"],
            },
        },
    ]
)

# 2) Semantic search retrieval
FUNCTIONS.append(
    {
        "name": "semantic_search",
        "description": "Retrieve top-k relevant code snippets from the indexed repo",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {
                    "type": "integer",
                    "description": "Number of snippets to retrieve",
                },
            },
            "required": ["query"],
        },
    }
)

# 3) Post-change validation
FUNCTIONS.extend(
    [
        {
            "name": "run_tests",
            "description": "Run the project’s test suite and return pass/fail and any errors",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "Path to the project root for running tests",
                    }
                },
                "required": ["folder_path"],
            },
        },
        {
            "name": "run_linter",
            "description": "Run linter (e.g. flake8, eslint) and return any findings",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "Path to the project root for linting",
                    }
                },
                "required": ["folder_path"],
            },
        },
    ]
)

# 4) Memory store for intermediate facts
FUNCTIONS.extend(
    [
        {
            "name": "save_memory",
            "description": "Persist an intermediate fact or key/value pair for later retrieval",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Identifier for the memory entry",
                    },
                    "value": {
                        "type": "object",
                        "description": "Arbitrary JSON-serializable value",
                    },
                },
                "required": ["key", "value"],
            },
        },
        {
            "name": "load_memory",
            "description": "Retrieve a previously saved value from memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Identifier for the memory entry",
                    }
                },
                "required": ["key"],
            },
        },
    ]
)
