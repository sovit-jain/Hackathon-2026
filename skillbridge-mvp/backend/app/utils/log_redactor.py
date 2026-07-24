"""Utility module for redacting sensitive information from logs."""

import re
from typing import Any, Pattern


class LogRedactor:
    """Redacts sensitive information (JWT tokens, API keys, passwords) from log messages."""

    # Patterns to detect and redact sensitive data
    JWT_PATTERN: Pattern = re.compile(
        r"(eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})",
        re.IGNORECASE,
    )
    API_KEY_PATTERN: Pattern = re.compile(r"(api[_-]?key)[=:\s]+([^\s,]+)", re.IGNORECASE)
    BEARER_PATTERN: Pattern = re.compile(r"(bearer\s+)([^\s]+)", re.IGNORECASE)
    PASSWORD_PATTERN: Pattern = re.compile(
        r"(password)[=:\s]+([^\s,}]+)", re.IGNORECASE
    )
    SECRET_PATTERN: Pattern = re.compile(r"(secret)[=:\s]+([^\s,}]+)", re.IGNORECASE)
    TOKEN_PATTERN: Pattern = re.compile(
        r"(token)[=:\s]+([^\s,}]+)", re.IGNORECASE
    )
    AUTHORIZATION_PATTERN: Pattern = re.compile(
        r"(authorization)[=:\s]+([^\s,}]+)", re.IGNORECASE
    )

    @staticmethod
    def redact(text: str) -> str:
        """Redact sensitive information from text."""
        if not isinstance(text, str):
            return str(text)

        # Redact JWT tokens
        text = LogRedactor.JWT_PATTERN.sub(r"[JWT_REDACTED]", text)

        # Redact API keys
        text = LogRedactor.API_KEY_PATTERN.sub(r"\1=[API_KEY_REDACTED]", text)

        # Redact bearer tokens
        text = LogRedactor.BEARER_PATTERN.sub(r"\1[TOKEN_REDACTED]", text)

        # Redact passwords
        text = LogRedactor.PASSWORD_PATTERN.sub(r"\1=[PASSWORD_REDACTED]", text)

        # Redact secrets
        text = LogRedactor.SECRET_PATTERN.sub(r"\1=[SECRET_REDACTED]", text)

        # Redact generic tokens
        text = LogRedactor.TOKEN_PATTERN.sub(r"\1=[TOKEN_REDACTED]", text)

        # Redact authorization headers
        text = LogRedactor.AUTHORIZATION_PATTERN.sub(r"\1=[AUTH_REDACTED]", text)

        return text

    @staticmethod
    def redact_value(value: Any) -> Any:
        """Redact a single value if it's a string."""
        if isinstance(value, str):
            return LogRedactor.redact(value)
        return value
