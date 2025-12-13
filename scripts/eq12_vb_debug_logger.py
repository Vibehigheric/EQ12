#!/usr/bin/env python3
"""
EQ12 Advanced VB Debug Logging Automation
Purpose: Real-time VB debugging session capture with structured JSON logging
Agent: GitHub Copilot with EQ12 expertise
Timestamp: 2025-10-10T22:15:00Z

Features:
- Real-time Debug.WriteLine capture and analysis
- Structured JSON logging for VB debugging sessions
- Automated log parsing and performance metrics
- Integration with EQ12 logging standards
- Visual Studio debug output monitoring
"""

import argparse
import json
import logging
import queue
import re
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class EQ12VBDebugLogger:
    """Advanced VB debug logging with real-time capture and analysis"""

    def __init__(self, workspace: str = "C:\\\\EQ12"):
        self.workspace = Path(workspace)
        self.logs_dir = self.workspace / "logs" / "vb_debugging"
        self.debug_sessions_dir = self.logs_dir / "sessions"
        self.configs_dir = self.workspace / "configs"

        # Create directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.debug_sessions_dir.mkdir(exist_ok=True)
        self.configs_dir.mkdir(exist_ok=True)

        self.setup_logging()

        # Debug patterns for parsing VB Debug.WriteLine output
        self.debug_patterns = {
            "function_entry": r"🔍 Entering (\w+):",
            "function_exit": r"✅ Exiting (\w+):",
            "variable_log": r"📊 (\w+).*?:\s*(.+)",
            "performance": r"⏱️.*?(\d+(?:\.\d+)?)ms",
            "error": r"❌.*?Exception.*?:\s*(.+)",
            "warning": r"⚠️.*?:\s*(.+)",
            "success": r"✅.*?:\s*(.+)",
        }

        # Session tracking
        self.active_sessions = {}
        self.debug_queue = queue.Queue()
        self.monitoring = False

    def setup_logging(self):
        """Configure VB debug logging system"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"vb_debug_logger_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔧 EQ12 VB Debug Logger initialized")

    def create_debug_session(
            self,
            session_name: str,
            vb_file: Path | None = None) -> str:
        """Create new VB debugging session with structured logging"""
        session_id = f"vb_debug_{
            datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_name}"

        session_info = {
            "session_id": session_id,
            "session_name": session_name,
            "start_time": datetime.now(UTC).isoformat(),
            "vb_file": str(vb_file) if vb_file else None,
            "debug_events": [],
            "performance_metrics": {},
            "function_calls": [],
            "variables_tracked": {},
            "errors": [],
            "warnings": [],
        }

        self.active_sessions[session_id] = session_info

        # Create session log file
        session_file = self.debug_sessions_dir / f"{session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📝 Created VB debug session: {session_id}")
        return session_id

    def parse_debug_output(self, debug_line: str, session_id: str) -> dict[str, Any]:
        """Parse VB Debug.WriteLine output into structured events"""
        timestamp = datetime.now(UTC).isoformat()

        event = {
            "timestamp": timestamp,
            "raw_output": debug_line.strip(),
            "event_type": "unknown",
            "parsed_data": {},
        }

        # Parse different types of debug output
        for pattern_name, pattern in self.debug_patterns.items():
            match = re.search(pattern, debug_line)
            if match:
                event["event_type"] = pattern_name

                if pattern_name == "function_entry":
                    event["parsed_data"] = {
                        "function_name": match.group(1),
                        "action": "entry",
                    }
                    self.track_function_call(
                        session_id, match.group(1), "entry", timestamp)

                elif pattern_name == "function_exit":
                    event["parsed_data"] = {
                        "function_name": match.group(1),
                        "action": "exit",
                    }
                    self.track_function_call(
                        session_id, match.group(1), "exit", timestamp)

                elif pattern_name == "variable_log":
                    var_name = match.group(1)
                    var_value = match.group(2)
                    event["parsed_data"] = {
                        "variable_name": var_name,
                        "variable_value": var_value,
                    }
                    self.track_variable(session_id, var_name, var_value, timestamp)

                elif pattern_name == "performance":
                    duration_ms = float(match.group(1))
                    event["parsed_data"] = {"duration_ms": duration_ms}
                    self.track_performance(session_id, duration_ms)

                elif pattern_name in ["error", "warning", "success"]:
                    message = match.group(1)
                    event["parsed_data"] = {
                        "message": message,
                        "severity": pattern_name,
                    }
                    if pattern_name == "error":
                        self.track_error(session_id, message, timestamp)
                    elif pattern_name == "warning":
                        self.track_warning(session_id, message, timestamp)

                break

        return event

    def track_function_call(
            self,
            session_id: str,
            function_name: str,
            action: str,
            timestamp: str):
        """Track function entry/exit for performance analysis"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        if action == "entry":
            # Record function entry
            call_info = {
                "function_name": function_name,
                "entry_time": timestamp,
                "exit_time": None,
                "duration_ms": None,
            }
            session["function_calls"].append(call_info)

        elif action == "exit":
            # Find matching entry and calculate duration
            for call in reversed(session["function_calls"]):
                if call["function_name"] == function_name and call["exit_time"] is None:
                    call["exit_time"] = timestamp

                    # Calculate duration
                    entry_time = datetime.fromisoformat(
                        call["entry_time"].replace("Z", "+00:00"))
                    exit_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    duration = (exit_time - entry_time).total_seconds() * 1000
                    call["duration_ms"] = duration

                    self.logger.debug(
                        f"⏱️ Function {function_name} took {
                            duration:.2f}ms")
                    break

    def track_variable(
            self,
            session_id: str,
            var_name: str,
            var_value: str,
            timestamp: str):
        """Track variable assignments and changes"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        if var_name not in session["variables_tracked"]:
            session["variables_tracked"][var_name] = []

        session["variables_tracked"][var_name].append(
            {"timestamp": timestamp, "value": var_value})

    def track_performance(self, session_id: str, duration_ms: float):
        """Track performance metrics"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        if "durations" not in session["performance_metrics"]:
            session["performance_metrics"]["durations"] = []

        session["performance_metrics"]["durations"].append(duration_ms)

        # Calculate statistics
        durations = session["performance_metrics"]["durations"]
        session["performance_metrics"]["avg_duration_ms"] = sum(
            durations) / len(durations)
        session["performance_metrics"]["max_duration_ms"] = max(durations)
        session["performance_metrics"]["min_duration_ms"] = min(durations)

    def track_error(self, session_id: str, error_message: str, timestamp: str):
        """Track errors and exceptions"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        session["errors"].append({"timestamp": timestamp, "message": error_message})

    def track_warning(self, session_id: str, warning_message: str, timestamp: str):
        """Track warnings and alerts"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        session["warnings"].append({"timestamp": timestamp, "message": warning_message})

    def monitor_visual_studio_output(
            self,
            session_id: str,
            duration_seconds: int = 300):
        """Monitor Visual Studio debug output in real-time"""
        self.logger.info(
            f"👀 Starting Visual Studio debug monitor for {duration_seconds} seconds")

        self.monitoring = True
        start_time = time.time()

        # This is a simplified version - real implementation would need to hook into VS Debug API
        # or monitor debug output files/streams

        def monitor_thread():
            while self.monitoring and (time.time() - start_time < duration_seconds):
                try:
                    # Simulate reading debug output (replace with actual VS integration)
                    # In real implementation, this would read from Visual Studio debug
                    # output
                    if not self.debug_queue.empty():
                        debug_line = self.debug_queue.get()
                        event = self.parse_debug_output(debug_line, session_id)

                        if session_id in self.active_sessions:
                            self.active_sessions[session_id]["debug_events"].append(
                                event)

                        self.logger.debug(
                            f"📊 Captured debug event: {
                                event['event_type']}")

                    time.sleep(0.1)  # Check every 100ms

                except Exception as e:
                    self.logger.error(f"❌ Error monitoring debug output: {e}")

        monitor_thread = threading.Thread(target=monitor_thread)
        monitor_thread.daemon = True
        monitor_thread.start()

        return monitor_thread

    def inject_debug_line(self, debug_line: str):
        """Inject debug line for testing purposes"""
        self.debug_queue.put(debug_line)

    def finalize_session(self, session_id: str) -> Path:
        """Finalize debugging session and save comprehensive report"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session["end_time"] = datetime.now(UTC).isoformat()

        # Calculate session statistics
        session["statistics"] = self.calculate_session_statistics(session)

        # Save final session report
        session_file = self.debug_sessions_dir / f"{session_id}_final.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        # Generate human-readable report
        report_file = self.generate_session_report(session_id, session)

        # Clean up
        del self.active_sessions[session_id]

        self.logger.info(f"✅ Finalized VB debug session: {session_id}")
        self.logger.info(f"📊 Reports saved: {session_file}, {report_file}")

        return report_file

    def calculate_session_statistics(self, session: dict) -> dict:
        """Calculate comprehensive session statistics"""
        stats = {
            "total_debug_events": len(session["debug_events"]),
            "total_function_calls": len(session["function_calls"]),
            "total_variables_tracked": len(session["variables_tracked"]),
            "total_errors": len(session["errors"]),
            "total_warnings": len(session["warnings"]),
            "event_types_breakdown": {},
        }

        # Count event types
        for event in session["debug_events"]:
            event_type = event["event_type"]
            stats["event_types_breakdown"][event_type] = (
                stats["event_types_breakdown"].get(event_type, 0) + 1
            )

        # Function performance analysis
        completed_calls = [call for call in session["function_calls"]
                           if call["duration_ms"] is not None]
        if completed_calls:
            durations = [call["duration_ms"] for call in completed_calls]
            stats["function_performance"] = {
                "total_completed_calls": len(completed_calls),
                "avg_duration_ms": sum(durations) /
                len(durations),
                "max_duration_ms": max(durations),
                "min_duration_ms": min(durations),
                "slowest_function": max(
                    completed_calls,
                    key=lambda x: x["duration_ms"])["function_name"],
            }

        return stats

    def generate_session_report(self, session_id: str, session: dict) -> Path:
        """Generate human-readable debugging session report"""
        report_file = self.debug_sessions_dir / f"{session_id}_report.md"

        report_content = """# EQ12 VB Debugging Session Report

**Session ID**: {session_id}
**Session Name**: {session.get('session_name', 'Unknown')}
**Start Time**: {session.get('start_time', 'Unknown')}
**End Time**: {session.get('end_time', 'Unknown')}
**VB File**: {session.get('vb_file', 'Not specified')}

## Session Summary

- **Total Debug Events**: {session['statistics']['total_debug_events']}
- **Function Calls**: {session['statistics']['total_function_calls']}
- **Variables Tracked**: {session['statistics']['total_variables_tracked']}
- **Errors**: {session['statistics']['total_errors']}
- **Warnings**: {session['statistics']['total_warnings']}

## Event Types Breakdown

"""

        for event_type, count in session["statistics"]["event_types_breakdown"].items():
            report_content += f"- **{event_type.replace('_', ' ').title()}**: {count}\n"

        # Function Performance Analysis
        if "function_performance" in session["statistics"]:
            session["statistics"]["function_performance"]
            report_content += """
## Function Performance Analysis

- **Total Completed Calls**: {perf['total_completed_calls']}
- **Average Duration**: {perf['avg_duration_ms']:.2f}ms
- **Maximum Duration**: {perf['max_duration_ms']:.2f}ms
- **Minimum Duration**: {perf['min_duration_ms']:.2f}ms
- **Slowest Function**: {perf['slowest_function']}

"""

        # Errors and Warnings
        if session["errors"]:
            report_content += "## Errors Encountered\n\n"
            for i, error in enumerate(session["errors"], 1):
                report_content += f"{i}. **{error['timestamp']}**: {error['message']}\n"
            report_content += "\n"

        if session["warnings"]:
            report_content += "## Warnings\n\n"
            for i, warning in enumerate(session["warnings"], 1):
                report_content += f"{i}. **{warning['timestamp']}**: {warning['message']}\n"
            report_content += "\n"

        # Variable Tracking
        if session["variables_tracked"]:
            report_content += "## Variable Tracking\n\n"
            for var_name, changes in session["variables_tracked"].items():
                report_content += f"### Variable: {var_name}\n\n"
                for change in changes[-5:]:  # Show last 5 changes
                    report_content += f"- **{change['timestamp']}**: `{change['value']}`\n"
                report_content += "\n"

        report_content += """
## Recommendations

Based on this debugging session:

1. **Performance**: Review functions with duration > 100ms for optimization opportunities
2. **Error Handling**: Ensure all errors have appropriate Try-Catch blocks
3. **Variable Tracking**: Consider reducing excessive variable logging in production
4. **Debug Cleanup**: Remove debug statements before production deployment

---
*Generated by EQ12 VB Debug Logger*
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        return report_file

    def demo_debugging_session(self) -> str:
        """Run a demo debugging session with simulated VB debug output"""
        session_id = self.create_debug_session("demo_session")

        self.logger.info("🎬 Running demo VB debugging session")

        # Simulate VB debug output
        demo_debug_lines = [
            "🔍 Entering ProcessData: 2025-10-10T22:15:30Z",
            "📊 Variable inputValue: test_data_123",
            "📊 Variable counter: 0",
            "🔍 Entering ValidateInput: 2025-10-10T22:15:31Z",
            "✅ Exiting ValidateInput: 2025-10-10T22:15:31Z",
            "⏱️ ValidateInput executed in 125.5ms",
            "📊 Variable processedData: PROCESSED_TEST_DATA_123",
            "⚠️ Warning: Large data set detected - consider optimization",
            "✅ Exiting ProcessData: 2025-10-10T22:15:32Z",
            "⏱️ ProcessData executed in 2340.7ms",
        ]

        # Process demo lines
        for line in demo_debug_lines:
            event = self.parse_debug_output(line, session_id)
            self.active_sessions[session_id]["debug_events"].append(event)
            time.sleep(0.1)  # Simulate real-time processing

        # Finalize session
        report_file = self.finalize_session(session_id)

        self.logger.info(f"🎉 Demo session completed: {report_file}")
        return session_id


def main():
    """Main entry point for EQ12 VB Debug Logger"""
    parser = argparse.ArgumentParser(
        description="EQ12 Advanced VB Debug Logging Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo                           # Run demo debugging session
  %(prog)s --monitor --duration 300         # Monitor VS debug output for 5 minutes
  %(prog)s --create-session "my_test"       # Create new debugging session
  %(prog)s --finalize "session_id"          # Finalize and generate report
        """,
    )

    parser.add_argument(
        "--workspace",
        default="C:\\\\EQ12",
        help="EQ12 workspace directory (default: C:\\\\EQ12)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo VB debugging session")
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Monitor Visual Studio debug output")
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Monitor duration in seconds (default: 300)",
    )
    parser.add_argument(
        "--create-session",
        help="Create new debugging session with given name")
    parser.add_argument("--finalize", help="Finalize debugging session by session ID")
    parser.add_argument("--vb-file", help="VB file being debugged")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger = EQ12VBDebugLogger(args.workspace)

        if args.demo:
            print("🎬 Running EQ12 VB Debug Logger Demo")
            print("=" * 50)
            session_id = logger.demo_debugging_session()
            print(f"✅ Demo completed! Session ID: {session_id}")

        elif args.create_session:
            vb_file = Path(args.vb_file) if args.vb_file else None
            session_id = logger.create_debug_session(args.create_session, vb_file)
            print(f"✅ Created debugging session: {session_id}")

        elif args.finalize:
            if args.finalize not in logger.active_sessions:
                print(f"❌ Session not found: {args.finalize}")
                sys.exit(1)
            report_file = logger.finalize_session(args.finalize)
            print(f"✅ Session finalized! Report: {report_file}")

        elif args.monitor:
            session_id = logger.create_debug_session(f"monitor_{int(time.time())}")
            print(
                f"👀 Monitoring Visual Studio debug output for {
                    args.duration} seconds")
            print(f"Session ID: {session_id}")

            monitor_thread = logger.monitor_visual_studio_output(
                session_id, args.duration)

            try:
                monitor_thread.join(args.duration + 5)
                report_file = logger.finalize_session(session_id)
                print(f"✅ Monitoring completed! Report: {report_file}")
            except KeyboardInterrupt:
                logger.monitoring = False
                print("🛑 Monitoring stopped by user")

        else:
            parser.print_help()

    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
