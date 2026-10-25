"""Function schema exposed for the Prowler scanner tool."""

from openai.types.chat import ChatCompletionToolUnionParam

prowler_scan_tool: list[ChatCompletionToolUnionParam] = [
    {
        "type": "function",
        "function": {
            "name": "select_scan_arguments",
            "description": "Choose arguments for a read-only Prowler AWS scan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "AWS region to scan; defaults to the configured region.",
                    },
                    "services": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional Prowler service names to limit the scan.",
                    },
                    "prowler_args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional additional Prowler CLI arguments as separate tokens. "
                            "Do not include the executable, 'aws', shell syntax, or output options."
                        ),
                    },
                },
                "additionalProperties": False,
            },
        },
    }
]
