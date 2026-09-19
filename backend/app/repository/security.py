import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from app.core.errors import ForgeAIError

SECRET_FILE_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
SECRET_PATTERNS = (
    re.compile(r"(?im)(api[_-]?key|secret|token|password)\s*[:=]\s*(['\"]?)[^\s'\"]+\2"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END [^-]+-----"),
    re.compile(r"(?i)\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{20,}\b"),
)


@dataclass(frozen=True)
class RedactionResult:
    content: str
    secret_count: int


def normalize_relative_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip()
    if not normalized or "\x00" in normalized:
        raise ForgeAIError("unsafe_path", "File paths must be non-empty and must not contain null bytes.")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise ForgeAIError("unsafe_path", "Absolute paths and path traversal are not allowed.")
    if path.name in SECRET_FILE_NAMES or path.name.startswith(".env"):
        raise ForgeAIError("sensitive_file", "Environment and private-key files cannot be uploaded.")
    return path.as_posix()


def redact_secrets(content: str) -> RedactionResult:
    redacted = content
    count = 0
    for pattern in SECRET_PATTERNS:
        redacted, replacements = pattern.subn(lambda match: f"{match.group(1) if match.lastindex else 'REDACTED'}=\"[REDACTED]\"", redacted)
        count += replacements
    return RedactionResult(redacted, count)
