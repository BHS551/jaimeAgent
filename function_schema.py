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
        "description": "Read and return the full contents of a text file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read (supports ~ for home)"
                }
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
        }
]