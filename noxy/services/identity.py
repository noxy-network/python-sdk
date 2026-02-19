"""Identity service for fetching devices."""

import uuid

from noxy.grpc import noxy_pb2
from noxy.transport import auth_metadata
from noxy.types import NoxyIdentityDevice


class IdentityService:
    """Fetches identity devices from the relay."""

    def get_devices(
        self,
        stub,
        auth_token: str,
        identity_id: str,
    ) -> list[NoxyIdentityDevice]:
        """Return all devices registered for the given identity address."""
        req = noxy_pb2.GetIdentityDevicesRequest(
            request_id=str(uuid.uuid4()),
            identity_id=identity_id,
        )
        metadata = auth_metadata(auth_token)
        resp = stub.GetIdentityDevices(req, metadata=metadata)

        return [
            NoxyIdentityDevice(
                device_id=d.device_id,
                public_key=bytes(d.public_key),
                pq_public_key=bytes(d.pq_public_key),
            )
            for d in resp.devices
        ]
