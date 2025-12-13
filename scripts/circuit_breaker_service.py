"""
EQ12 Circuit Breaker Service
Standalone service for managing API rate limits and failures
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path


class CircuitBreakerService:
    """Standalone circuit breaker service"""

    def __init__(self):
        self.state_file = Path("logs/circuit_breaker/state.json")
        self.setup_logging()
        self.ensure_state_file()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs/circuit_breaker")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    log_dir / f"circuit_breaker_{datetime.now().strftime('%Y%m%d')}.log"
                ),
                logging.StreamHandler(),
            ],
        )

    def ensure_state_file(self):
        """Ensure circuit breaker state file exists"""
        if not self.state_file.exists():
            self.reset_to_healthy()

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        try:
            return json.loads(self.state_file.read_text())
        except Exception as e:
            logging.error(f"Failed to read state file: {e}")
            return self.get_default_state()

    def get_default_state(self) -> dict:
        """Get default healthy state"""
        return {
            "status": "healthy",
            "offline": False,
            "until": None,
            "failure_count": 0,
            "last_failure": None,
            "last_success": None,
            "total_failures": 0,
            "total_requests": 0,
            "uptime_start": datetime.now().isoformat(),
        }

    def save_state(self, state: dict):
        """Save state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logging.error(f"Failed to save state: {e}")

    def is_healthy(self) -> bool:
        """Check if circuit breaker is in healthy state"""
        state = self.get_state()

        if not state.get("offline"):
            return True

        until_str = state.get("until")
        if until_str:
            try:
                until_time = datetime.fromisoformat(until_str.replace("Z", ""))
                if datetime.now() > until_time:
                    # Auto-reset after timeout
                    self.reset_to_healthy()
                    logging.info("Circuit breaker auto-reset to healthy")
                    return True
            except Exception as e:
                logging.error(f"Error parsing until time: {e}")

        return False

    def record_failure(self, service_name: str = "unknown"):
        """Record a service failure"""
        state = self.get_state()
        state["failure_count"] += 1
        state["total_failures"] += 1
        state["total_requests"] += 1
        state["last_failure"] = datetime.now().isoformat()

        # Trip circuit breaker after 5 failures in 5 minutes
        if state["failure_count"] >= 5:
            until_time = datetime.now() + timedelta(minutes=5)
            state.update(
                {
                    "offline": True,
                    "until": until_time.isoformat() + "Z",
                    "status": "tripped",
                }
            )
            logging.warning(
                f"Circuit breaker TRIPPED for {service_name} until {until_time}")

        self.save_state(state)
        logging.info(
            f"Recorded failure for {service_name} (count: {
                state['failure_count']})")

    def record_success(self, service_name: str = "unknown"):
        """Record a successful service call"""
        state = self.get_state()
        state["total_requests"] += 1
        state["last_success"] = datetime.now().isoformat()

        # Gradually reduce failure count on success
        if state["failure_count"] > 0:
            state["failure_count"] = max(0, state["failure_count"] - 1)

        # Reset to healthy if no recent failures
        if state["failure_count"] == 0 and state.get("offline"):
            state.update({"offline": False, "until": None, "status": "healthy"})
            logging.info(
                f"Circuit breaker RESET to healthy after success from {service_name}")

        self.save_state(state)

    def reset_to_healthy(self):
        """Manually reset circuit breaker to healthy state"""
        state = self.get_default_state()
        self.save_state(state)
        logging.info("Circuit breaker manually reset to healthy")

    def get_status_report(self) -> dict:
        """Get detailed status report"""
        state = self.get_state()

        # Calculate uptime
        uptime_start = state.get("uptime_start")
        if uptime_start:
            try:
                start_time = datetime.fromisoformat(uptime_start)
                uptime_seconds = (datetime.now() - start_time).total_seconds()
            except Exception:
                uptime_seconds = 0
        else:
            uptime_seconds = 0

        # Calculate success rate
        total_requests = state.get("total_requests", 0)
        total_failures = state.get("total_failures", 0)
        success_rate = 0
        if total_requests > 0:
            success_rate = ((total_requests - total_failures) / total_requests) * 100

        return {
            "status": state.get("status", "unknown"),
            "is_healthy": self.is_healthy(),
            "offline": state.get("offline", False),
            "failure_count": state.get("failure_count", 0),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "success_rate_percent": round(success_rate, 2),
            "uptime_seconds": int(uptime_seconds),
            "uptime_formatted": str(timedelta(seconds=int(uptime_seconds))),
            "last_failure": state.get("last_failure"),
            "last_success": state.get("last_success"),
            "offline_until": state.get("until"),
        }


def main():
    """Main CLI interface"""
    service = CircuitBreakerService()

    if len(sys.argv) < 2:
        print("Circuit Breaker Service")
        print("Usage:")
        print("  python circuit_breaker_service.py status    # Get status")
        print("  python circuit_breaker_service.py reset     # Reset to healthy")
        print("  python circuit_breaker_service.py fail <service>   # Record failure")
        print("  python circuit_breaker_service.py success <service> # Record success")
        return None

    command = sys.argv[1].lower()

    if command == "status":
        report = service.get_status_report()
        print(json.dumps(report, indent=2))

    elif command == "reset":
        service.reset_to_healthy()
        print("Circuit breaker reset to healthy state")

    elif command == "fail":
        service_name = sys.argv[2] if len(sys.argv) > 2 else "manual"
        service.record_failure(service_name)
        print(f"Recorded failure for {service_name}")

    elif command == "success":
        service_name = sys.argv[2] if len(sys.argv) > 2 else "manual"
        service.record_success(service_name)
        print(f"Recorded success for {service_name}")

    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    main()
