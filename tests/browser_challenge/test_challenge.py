"""Test challenge detection, classification, policies, and recovery."""
import pytest
from browser.challenge.models import Challenge, ChallengeType, RecoveryAction, RecoveryResult
from browser.challenge.detector import ChallengeDetector
from browser.challenge.classifier import ChallengeClassifier, classify_severity
from browser.challenge.policies import PolicyEngine
from browser.challenge.recovery import RecoveryManager
from browser.challenge.manager import ChallengeManager


class TestDetector:
    def test_detects_captcha_in_html(self):
        detector = ChallengeDetector()
        html = "<html><body><div class='g-recaptcha'></div></body></html>"
        challenge = detector.detect(html=html)
        assert challenge is not None
        assert challenge.challenge_type == ChallengeType.CAPTCHA
        assert challenge.confidence > 0.9

    def test_detects_cloudflare_js_challenge(self):
        detector = ChallengeDetector()
        html = "<html><body>cf-browser-verify Checking your browser...</body></html>"
        challenge = detector.detect(html=html)
        assert challenge is not None
        assert challenge.challenge_type == ChallengeType.JAVASCRIPT_CHALLENGE

    def test_detects_access_denied_by_title(self):
        detector = ChallengeDetector()
        challenge = detector.detect(title="403 Access Denied")
        assert challenge is not None
        assert challenge.challenge_type == ChallengeType.ACCESS_DENIED

    def test_detects_rate_limit_by_status(self):
        detector = ChallengeDetector()
        challenge = detector.detect(http_status=429)
        assert challenge is not None
        assert challenge.challenge_type == ChallengeType.RATE_LIMITED

    def test_normal_page_returns_none(self):
        detector = ChallengeDetector()
        challenge = detector.detect(
            html="<html><body><h1>Toyota Land Cruiser 2018</h1></body></html>",
            title="Toyota Land Cruiser for sale",
        )
        assert challenge is None


class TestClassifier:
    def test_classify_severity(self):
        assert classify_severity(Challenge("", ChallengeType.CAPTCHA)) == "high"
        assert classify_severity(Challenge("", ChallengeType.RATE_LIMITED)) == "medium"

    def test_classifier_passthrough(self):
        classifier = ChallengeClassifier()
        c = Challenge(challenge_type=ChallengeType.CAPTCHA, confidence=0.5)
        result = classifier.classify(c)
        assert result.challenge_type == ChallengeType.CAPTCHA


class TestPolicyEngine:
    def test_default_captcha_policy(self):
        engine = PolicyEngine()
        actions = engine.get_policy(ChallengeType.CAPTCHA)
        assert RecoveryAction.WAIT in actions
        assert RecoveryAction.ABORT in actions

    def test_custom_policy(self):
        engine = PolicyEngine()
        engine.set_policy(ChallengeType.CAPTCHA, [RecoveryAction.RETRY, RecoveryAction.ABORT])
        actions = engine.get_policy(ChallengeType.CAPTCHA)
        assert len(actions) == 2
        assert actions[0] == RecoveryAction.RETRY

    def test_marketplace_override(self):
        engine = PolicyEngine()
        engine.set_policy(ChallengeType.CAPTCHA,
                         [RecoveryAction.ABORT],
                         marketplace="dubizzle")
        default = engine.get_policy(ChallengeType.CAPTCHA)
        override = engine.get_policy(ChallengeType.CAPTCHA, marketplace="dubizzle")
        assert len(default) > 1
        assert override == [RecoveryAction.ABORT]


class TestRecovery:
    @pytest.mark.asyncio
    async def test_wait_action_succeeds(self):
        recovery = RecoveryManager()
        c = Challenge(challenge_type=ChallengeType.UNKNOWN)
        result = await recovery.recover(c)
        assert isinstance(result, RecoveryResult)

    @pytest.mark.asyncio
    async def test_recovery_with_callback(self):
        recovery = RecoveryManager()
        actions_seen = []
        async def on_action(action, attempt):
            actions_seen.append(action.value)

        c = Challenge(challenge_type=ChallengeType.CAPTCHA)
        result = await recovery.recover(c, on_action=on_action)
        assert len(actions_seen) > 0


class TestChallengeManager:
    def test_detect_and_record(self):
        import asyncio
        mgr = ChallengeManager()

        async def run():
            c = await mgr.detect_and_record(
                html="<div class='g-recaptcha'></div>",
                session_id="s1",
            )
            assert c is not None
            assert c.challenge_type == ChallengeType.CAPTCHA

            history = await mgr.get_history("s1")
            assert len(history) == 1

        asyncio.run(run())

    def test_no_challenge_page(self):
        mgr = ChallengeManager()
        c = mgr.detect(
            html="<html><body>Toyota Camry for sale</body></html>",
            title="Toyota Camry",
        )
        assert c is None
