"""Password hashing helpers for the local demo application."""

import hashlib
import hmac
import os

ALGORITHM = "sha256"
ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        ALGORITHM, password.encode("utf-8"), salt, ITERATIONS
    )
    return f"pbkdf2_{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if scheme != f"pbkdf2_{ALGORITHM}":
            return False
        candidate = hashlib.pbkdf2_hmac(
            ALGORITHM,
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (AttributeError, TypeError, ValueError):
        return False
