"""Kyber768 post-quantum key encapsulation for decision payload encryption."""

from typing import Tuple

import kybercffi


class KyberProvider:
    """Kyber768 provider for encapsulating shared secrets with device public keys."""

    def __init__(self) -> None:
        self._kyber = kybercffi.Kyber768()

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulate a shared secret using the device's post-quantum public key.

        Returns (kyber_ciphertext, shared_secret). Ciphertext is 1088 bytes, shared secret is 32 bytes.
        """
        return self._kyber.encapsulate(public_key)
