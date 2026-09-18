"""A small, deterministic contract for an internal platform service.

The service converts a developer's workload request into an auditable platform
plan. It intentionally returns a plan rather than making cloud API calls: the
approval and provisioning adapters are environment-specific boundaries.
"""

from dataclasses import dataclass
from typing import Literal


Environment = Literal["development", "staging", "production"]


@dataclass(frozen=True)
class WorkloadRequest:
    service: str
    environment: Environment
    image: str
    replicas: int
    public_ingress: bool = False
    database_access: bool = False


@dataclass(frozen=True)
class PlatformPlan:
    namespace: str
    deployment_replicas: int
    ingress: Literal["internal", "public"]
    database_policy: Literal["none", "least-privilege"]
    required_checks: tuple[str, ...]


def build_plan(request: WorkloadRequest) -> PlatformPlan:
    """Build a safe default plan and encode production-only release gates."""
    if not request.service.replace("-", "").isalnum():
        raise ValueError("service must contain letters, numbers, and hyphens")
    if not request.image or "@sha256:" not in request.image:
        raise ValueError("image must be pinned by digest")
    if request.replicas < 1:
        raise ValueError("at least one replica is required")

    checks = ["unit-tests", "container-scan", "policy-check"]
    replicas = request.replicas
    if request.environment == "production":
        checks.extend(["change-approved", "slo-capacity-check", "rollback-ready"])
        replicas = max(2, replicas)

    return PlatformPlan(
        namespace=f"{request.environment}-{request.service}",
        deployment_replicas=replicas,
        ingress="public" if request.public_ingress else "internal",
        database_policy="least-privilege" if request.database_access else "none",
        required_checks=tuple(checks),
    )
