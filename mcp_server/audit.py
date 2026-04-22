"""Audit logging helpers for the MCP server."""

import json
from datetime import UTC, datetime
from typing import Any


def log(user: str, action: str, params: dict[str, Any]) -> None:
    """Emit a structured audit event for the current request."""
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "user": user,
        "action": action,
        "params": params,
    }
    print(json.dumps(event))
    # TODO: Write audit events to Postgres for durable retention.
