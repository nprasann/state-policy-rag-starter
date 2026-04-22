"""Authentication helpers for the MCP server."""

import os


def get_user(token: str | None) -> str:
    """Resolve the effective user for the current request."""
    if os.getenv("AUTH_PROVIDER", "none").lower() == "none":
        return "test.user@state.gov"

    # TODO: Validate the bearer token with Entra ID and return the subject UPN.
    return token or "unknown.user@state.gov"
