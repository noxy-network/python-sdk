"""Quota service for fetching usage."""

import uuid

from noxy.grpc import noxy_pb2
from noxy.transport import auth_metadata
from noxy.types import NoxyGetQuotaResponse, NoxyQuotaStatus


class QuotaService:
    """Fetches quota usage from the relay."""

    def get(self, stub, auth_token: str) -> NoxyGetQuotaResponse:
        """Return quota usage for the application."""
        req = noxy_pb2.GetQuotaRequest(request_id=str(uuid.uuid4()))
        metadata = auth_metadata(auth_token)
        resp = stub.GetQuota(req, metadata=metadata)

        return NoxyGetQuotaResponse(
            request_id=resp.request_id,
            app_name=resp.app_name,
            quota_total=resp.quota_total,
            quota_remaining=resp.quota_remaining,
            status=NoxyQuotaStatus(resp.status),
        )
