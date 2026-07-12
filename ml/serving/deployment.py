"""Deployment Manager — deploy, activate, deactivate, rollback, archive."""

import uuid, time
from ml.serving.models import DeploymentRecord, DeploymentStatus


class DeploymentManager:
    def __init__(self):
        self._deployments: dict[str, list[DeploymentRecord]] = {}  # model_name → records

    def deploy(self, model_name: str, version: int) -> str:
        dep_id = str(uuid.uuid4())[:12]
        record = DeploymentRecord(
            deployment_id=dep_id, model_name=model_name,
            version=version, status=DeploymentStatus.DEPLOYED,
            traffic_pct=0.0,
        )
        self._deployments.setdefault(model_name, []).append(record)
        return dep_id

    def activate(self, model_name: str, deployment_id: str) -> None:
        records = self._deployments.get(model_name, [])
        for r in records:
            if r.deployment_id == deployment_id:
                r.status = DeploymentStatus.ACTIVE
                r.activated_at = time.time()
                r.traffic_pct = 100.0
                # Deactivate others
                for other in records:
                    if other.deployment_id != deployment_id and other.status == DeploymentStatus.ACTIVE:
                        other.status = DeploymentStatus.ARCHIVED

    def rollback(self, model_name: str, reason: str) -> str:
        records = self._deployments.get(model_name, [])
        active = [r for r in records if r.status == DeploymentStatus.ACTIVE]
        if active:
            active[0].status = DeploymentStatus.ROLLED_BACK
            active[0].rolled_back_at = time.time()
            active[0].rollback_reason = reason

        # Activate previous version
        previous = [r for r in records if r.status in (DeploymentStatus.DEPLOYED, DeploymentStatus.ARCHIVED)]
        if previous:
            prev = previous[-1]
            prev.status = DeploymentStatus.ACTIVE
            prev.activated_at = time.time()
            prev.traffic_pct = 100.0
            return prev.deployment_id
        return ""

    def get_history(self, model_name: str) -> list[DeploymentRecord]:
        return self._deployments.get(model_name, [])
