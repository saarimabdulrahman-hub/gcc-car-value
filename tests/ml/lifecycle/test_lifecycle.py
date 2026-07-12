"""Test lifecycle orchestrator — workflow, scheduler, approval, promotion, rollback."""
import pytest
from ml.lifecycle.orchestrator import LifecycleOrchestrator
from ml.lifecycle.workflow import WorkflowEngine
from ml.lifecycle.scheduler import RetrainingScheduler
from ml.lifecycle.approval import ApprovalWorkflow
from ml.lifecycle.models import WorkflowStage, TriggerSource, WorkflowRecord
from ml.lifecycle.config import LifecycleConfig


class TestWorkflowEngine:
    def test_create_and_transition(self):
        engine = WorkflowEngine()
        wf = engine.create("valuation")
        assert wf.stage == WorkflowStage.QUEUED

        engine.transition(wf.workflow_id, WorkflowStage.TRAINING)
        wf = engine.get(wf.workflow_id)
        assert wf.stage == WorkflowStage.TRAINING

    def test_valid_transitions(self):
        engine = WorkflowEngine()
        wf = engine.create("test")
        stages = [WorkflowStage.DATASET_SELECTED, WorkflowStage.TRAINING,
                 WorkflowStage.EVALUATING, WorkflowStage.REGISTERED,
                 WorkflowStage.WAITING_APPROVAL, WorkflowStage.APPROVED,
                 WorkflowStage.DEPLOYING, WorkflowStage.ACTIVE,
                 WorkflowStage.MONITORING, WorkflowStage.COMPLETED]
        for stage in stages:
            engine.transition(wf.workflow_id, stage)
        assert engine.get(wf.workflow_id).stage == WorkflowStage.COMPLETED

    def test_failure_transition(self):
        engine = WorkflowEngine()
        wf = engine.create("test")
        engine.transition(wf.workflow_id, WorkflowStage.TRAINING)
        engine.transition(wf.workflow_id, WorkflowStage.FAILED,
                         error="out of memory")
        assert engine.get(wf.workflow_id).stage == WorkflowStage.FAILED

    def test_stages_history_tracked(self):
        engine = WorkflowEngine()
        wf = engine.create("test")
        engine.transition(wf.workflow_id, WorkflowStage.TRAINING)
        engine.transition(wf.workflow_id, WorkflowStage.EVALUATING)
        wf = engine.get(wf.workflow_id)
        assert len(wf.stages_history) >= 2

    def test_list_active(self):
        engine = WorkflowEngine()
        wf = engine.create("test")
        engine.transition(wf.workflow_id, WorkflowStage.TRAINING)
        assert len(engine.list_active()) == 1


class TestScheduler:
    def test_initial_trigger_allowed(self):
        s = RetrainingScheduler()
        ok, reason = s.should_trigger(TriggerSource.MANUAL)
        assert ok

    def test_concurrent_limit(self):
        config = LifecycleConfig(max_concurrent_workflows=1)
        s = RetrainingScheduler(config)
        s.increment_active()
        ok, _ = s.should_trigger(TriggerSource.MANUAL)
        assert not ok  # Already at max

    def test_active_count(self):
        s = RetrainingScheduler()
        s.increment_active(); s.increment_active()
        assert s.active_count == 2
        s.decrement_active()
        assert s.active_count == 1


class TestApproval:
    def test_approve_workflow(self):
        aw = ApprovalWorkflow()
        wf = WorkflowRecord(model_name="test")
        aw.request(wf)
        aw.approve(wf.workflow_id, approver="ml-engineer", comment="looks good")
        assert not aw.is_pending(wf.workflow_id)

    def test_reject_workflow(self):
        aw = ApprovalWorkflow()
        wf = WorkflowRecord(model_name="test")
        aw.request(wf)
        aw.reject(wf.workflow_id, approver="ml-engineer", reason="poor performance")
        assert not aw.is_pending(wf.workflow_id)

    def test_pending_list(self):
        aw = ApprovalWorkflow()
        aw.request(WorkflowRecord(model_name="a"))
        aw.request(WorkflowRecord(model_name="b"))
        assert len(aw.list_pending()) == 2


class TestLifecycleOrchestrator:
    def test_full_workflow(self):
        orch = LifecycleOrchestrator()
        wf = orch.start("valuation")
        assert wf is not None
        assert wf.stage == WorkflowStage.DATASET_SELECTED

        orch.training_started(wf.workflow_id)
        orch.training_completed(wf.workflow_id, experiment_id="exp-1", model_version=2)
        assert orch.get_workflow(wf.workflow_id).stage == WorkflowStage.REGISTERED

    def test_approval_flow(self):
        orch = LifecycleOrchestrator()
        wf = orch.start("valuation")
        orch.training_completed(wf.workflow_id, experiment_id="exp-1")

        orch.request_approval(wf.workflow_id)
        assert len(orch.list_pending_approval()) == 1

        orch.approve(wf.workflow_id, approver="engineer")
        orch.deploy(wf.workflow_id)
        orch.promote(wf.workflow_id)
        orch.start_monitoring(wf.workflow_id)
        orch.complete(wf.workflow_id)

        final = orch.get_workflow(wf.workflow_id)
        assert final.stage == WorkflowStage.COMPLETED

    def test_rejection_flow(self):
        orch = LifecycleOrchestrator()
        wf = orch.start("valuation")
        orch.training_completed(wf.workflow_id)
        orch.request_approval(wf.workflow_id)
        orch.reject(wf.workflow_id, approver="engineer", reason="needs work")
        assert orch.get_workflow(wf.workflow_id).stage == WorkflowStage.REJECTED

    def test_rollback_flow(self):
        orch = LifecycleOrchestrator()
        wf = orch.start("valuation")
        orch.training_completed(wf.workflow_id)
        orch.approve(wf.workflow_id)
        orch.deploy(wf.workflow_id)
        orch.rollback(wf.workflow_id, reason="canary failure")
        assert orch.get_workflow(wf.workflow_id).stage == WorkflowStage.ROLLED_BACK

    def test_failure_flow(self):
        orch = LifecycleOrchestrator()
        wf = orch.start("valuation")
        orch.training_started(wf.workflow_id)
        orch.fail(wf.workflow_id, error="OOM during training")
        assert orch.get_workflow(wf.workflow_id).stage == WorkflowStage.FAILED

    def test_stats(self):
        orch = LifecycleOrchestrator()
        orch.start("valuation")
        orch.start("valuation")
        assert orch.stats["workflows"] == 2

    def test_concurrent_limit(self):
        config = LifecycleConfig(max_concurrent_workflows=2)
        orch = LifecycleOrchestrator(config)
        wf1 = orch.start("a")
        wf2 = orch.start("b")
        wf3 = orch.start("c")  # Should be None — at limit
        assert wf1 is not None
        assert wf2 is not None
        assert wf3 is None
