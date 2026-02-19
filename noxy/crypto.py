"""AES-256-GCM encryption with HKDF key derivation."""

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def encrypt(shared_secret: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    """Encrypt plaintext with AES-256-GCM using a key derived from the shared secret via HKDF-SHA256.

    Returns (ciphertext_with_auth_tag, nonce). The auth tag (16 bytes) is appended to ciphertext.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"",
    )
    key = hkdf.derive(shared_secret)

    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return ciphertext, nonce
