"""Governed AWS cloud utilities for ECC.

Wraps read-only AWS inspection calls behind an audit boundary so every
lookup is tied to a GovernanceContext correlation id, matching the
telemetry contract established by core.orchestrator_factory.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # boto3 is an optional runtime dependency
    boto3 = None
    BotoCoreError = ClientError = Exception


# Resource types this bridge knows how to audit-inspect, mapped to the
# boto3 client + describe/list call used to fulfil a read-only lookup.
_SUPPORTED_RESOURCE_TYPES: Dict[str, Dict[str, str]] = {
    "ec2_instances": {"service": "ec2", "call": "describe_instances"},
    "s3_buckets": {"service": "s3", "call": "list_buckets"},
    "iam_roles": {"service": "iam", "call": "list_roles"},
    "rds_instances": {"service": "rds", "call": "describe_db_instances"},
    "lambda_functions": {"service": "lambda", "call": "list_functions"},
}


class AWSGovernanceBridge:
    """Read-only AWS inspection bridge that audits every call against a
    required correlation id, so cloud lookups stay traceable back to the
    GovernanceContext that initiated them.
    """

    def __init__(self, correlation_id: str, session: Optional[Any] = None) -> None:
        if not correlation_id:
            raise ValueError("AWSGovernanceBridge requires a non-empty correlation_id")
        self.correlation_id: str = correlation_id
        self._session = session or (boto3.Session() if boto3 is not None else None)

    def _audit_log(self, message: str) -> None:
        print(f"[ECC AWS GOVERNANCE] [Correlation ID: {self.correlation_id}] {message}")

    def inspect_infrastructure(self, resource_type: str) -> Dict[str, Any]:
        """Perform a read-only lookup for `resource_type`, logging an
        audit line before the call and returning a normalized result
        (or an error payload) so failures never break the caller.
        """
        self._audit_log(f"Auditing lookups for resource type: {resource_type}")

        mapping = _SUPPORTED_RESOURCE_TYPES.get(resource_type)
        if mapping is None:
            self._audit_log(
                f"FAILED - unsupported resource type: {resource_type!r}. "
                f"Known types: {sorted(_SUPPORTED_RESOURCE_TYPES)}"
            )
            return {
                "status": "error",
                "correlation_id": self.correlation_id,
                "resource_type": resource_type,
                "error": f"Unsupported resource_type: {resource_type!r}",
            }

        if self._session is None:
            self._audit_log("FAILED - boto3 is not installed in this environment")
            return {
                "status": "error",
                "correlation_id": self.correlation_id,
                "resource_type": resource_type,
                "error": "boto3 is required to perform live AWS lookups",
            }

        try:
            client = self._session.client(mapping["service"])
            operation = getattr(client, mapping["call"])
            response = operation()
            self._audit_log(f"SUCCESS - lookup completed for resource type: {resource_type}")
            return {
                "status": "success",
                "correlation_id": self.correlation_id,
                "resource_type": resource_type,
                "data": response,
            }
        except (ClientError, BotoCoreError) as exc:
            self._audit_log(f"FAILED - AWS API error for {resource_type}: {exc}")
            return {
                "status": "error",
                "correlation_id": self.correlation_id,
                "resource_type": resource_type,
                "error": str(exc),
            }
        except Exception as exc:  # unexpected failure, still must be traceable
            self._audit_log(f"FAILED - unexpected error for {resource_type}: {exc}")
            return {
                "status": "error",
                "correlation_id": self.correlation_id,
                "resource_type": resource_type,
                "error": str(exc),
            }
