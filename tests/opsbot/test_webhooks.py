"""Test webhook signature verification and event handling."""

import hashlib
import hmac
import json
import time
from unittest.mock import patch

from fastapi.testclient import TestClient

from eq12_opsbot.server import create_app


class TestWebhookVerification:
    """Test webhook HMAC signature verification."""

    def test_valid_signature_accepted(self, sample_webhook_payload):
        """Test that valid HMAC signature is accepted."""
        app = create_app()
        client = TestClient(app)

        # Create valid signature
        secret = "test-webhook-secret"
        timestamp = int(time.time())
        payload_bytes = json.dumps(sample_webhook_payload).encode()

        signature_payload = f"{timestamp}.{payload_bytes.decode()}"
        signature = hmac.new(
            secret.encode(), signature_payload.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "OpenAI-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json",
        }

        with patch.dict("os.environ", {"OPENAI_WEBHOOK_SECRET": secret}):
            response = client.post("/webhooks/openai", json=sample_webhook_payload, headers=headers)

        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_invalid_signature_rejected(self, sample_webhook_payload):
        """Test that invalid HMAC signature is rejected."""
        app = create_app()
        client = TestClient(app)

        timestamp = int(time.time())
        invalid_signature = "invalid_signature_12345"

        headers = {
            "OpenAI-Signature": f"t={timestamp},v1={invalid_signature}",
            "Content-Type": "application/json",
        }

        with patch.dict("os.environ", {"OPENAI_WEBHOOK_SECRET": "test-secret"}):
            response = client.post("/webhooks/openai", json=sample_webhook_payload, headers=headers)

        assert response.status_code == 403
        assert "Invalid signature" in response.json()["detail"]

    def test_old_timestamp_rejected(self, sample_webhook_payload):
        """Test that timestamps older than 5 minutes are rejected."""
        app = create_app()
        client = TestClient(app)

        # Create timestamp from 10 minutes ago
        old_timestamp = int(time.time()) - (10 * 60)
        secret = "test-webhook-secret"
        payload_bytes = json.dumps(sample_webhook_payload).encode()

        signature_payload = f"{old_timestamp}.{payload_bytes.decode()}"
        signature = hmac.new(
            secret.encode(), signature_payload.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "OpenAI-Signature": f"t={old_timestamp},v1={signature}",
            "Content-Type": "application/json",
        }

        with patch.dict("os.environ", {"OPENAI_WEBHOOK_SECRET": secret}):
            response = client.post("/webhooks/openai", json=sample_webhook_payload, headers=headers)

        assert response.status_code == 400
        assert "too old" in response.json()["detail"]


class TestWebhookIdempotency:
    """Test webhook idempotency and duplicate prevention."""

    def test_duplicate_webhook_rejected(self, sample_webhook_payload):
        """Test that duplicate webhook events are rejected."""
        app = create_app()
        client = TestClient(app)

        secret = "test-webhook-secret"
        timestamp = int(time.time())
        payload_bytes = json.dumps(sample_webhook_payload).encode()

        signature_payload = f"{timestamp}.{payload_bytes.decode()}"
        signature = hmac.new(
            secret.encode(), signature_payload.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "OpenAI-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json",
        }

        with patch.dict("os.environ", {"OPENAI_WEBHOOK_SECRET": secret}):
            # First request should succeed
            response1 = client.post(
                "/webhooks/openai", json=sample_webhook_payload, headers=headers
            )
            assert response1.status_code == 200

            # Second request with same event ID should be rejected
            response2 = client.post(
                "/webhooks/openai", json=sample_webhook_payload, headers=headers
            )
            assert response2.status_code == 409
            assert "duplicate" in response2.json()["detail"].lower()


class TestEventRouting:
    """Test webhook event routing to appropriate handlers."""

    def test_job_completed_routing(self, sample_webhook_payload):
        """Test that job.completed events are routed properly."""
        app = create_app()
        client = TestClient(app)

        secret = "test-webhook-secret"
        timestamp = int(time.time())
        payload_bytes = json.dumps(sample_webhook_payload).encode()

        signature_payload = f"{timestamp}.{payload_bytes.decode()}"
        signature = hmac.new(
            secret.encode(), signature_payload.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "OpenAI-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json",
        }

        with patch.dict("os.environ", {"OPENAI_WEBHOOK_SECRET": secret}):
            with patch("eq12_opsbot.handlers_openai.handle_job_completed") as mock_handler:
                response = client.post(
                    "/webhooks/openai", json=sample_webhook_payload, headers=headers
                )

                assert response.status_code == 200
                mock_handler.assert_called_once()

    def test_rate_limit_warning_routing(self, sample_rate_limit_payload):
        """Test that rate_limit.warning events are routed properly."""
        app = create_app()
        client = TestClient(app)

        secret = "test-webhook-secret"
        timestamp = int(time.time())
        payload_bytes = json.dumps(sample_rate_limit_payload).encode()

        signature_payload = f"{timestamp}.{payload_bytes.decode()}"
        signature = hmac.new(
            secret.encode(), signature_payload.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "OpenAI-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json",
        }

        with patch.dict("os.environ", {"OPENAI_WEBHOOK_SECRET": secret}):
            with patch("eq12_opsbot.handlers_openai.handle_rate_limit_warning") as mock_handler:
                response = client.post(
                    "/webhooks/openai", json=sample_rate_limit_payload, headers=headers
                )

                assert response.status_code == 200
                mock_handler.assert_called_once()


class TestHealthEndpoint:
    """Test health check endpoint functionality."""

    def test_health_endpoint_basic(self):
        """Test basic health endpoint response."""
        app = create_app()
        client = TestClient(app)

        response = client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime_seconds" in data
        assert "config_summary" in data

    def test_health_endpoint_includes_components(self):
        """Test health endpoint includes component status."""
        app = create_app()
        client = TestClient(app)

        with patch.dict("os.environ", {"EQ12_BUDGET_DAILY": "5", "EQ12_BUDGET_MONTHLY": "120"}):
            response = client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert "budget_status" in data
            assert "rate_limit_status" in data
