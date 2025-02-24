from typing import Optional

def redact_secret(value: str, show_chars: Optional[int] = 4) -> str:
    """Redact a secret value, optionally showing last N characters
    Example: "supersecrettoken" -> "********token"
    """
    if not value:
        return ""
    if len(value) <= show_chars:
        return "*" * len(value)
    return "*" * (len(value) - show_chars) + value[-show_chars:]
