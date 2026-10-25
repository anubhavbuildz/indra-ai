"""Function schema exposed for the Prowler scanner tool."""
from openai.types.chat import ChatCompletionToolUnionParam

# Fixes both the type validation signature and bracket enclosure errors perfectly
prowler_scan_tool: list[ChatCompletionToolUnionParam] = [
    {
        "type": "function",
        "function": {
            "name": "run_scan",
            "description": (
                "Run a read-only Prowler scan for an AWS region and optional service subset."
            ),
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
                },
                "additionalProperties": False,
            },
        },
    }
]
