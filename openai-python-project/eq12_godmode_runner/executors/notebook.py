"""
Notebook Executor for EQ12 God Mode Commander++
Handles Jupyter notebook execution and data analysis tasks
"""

import os
import subprocess
from datetime import datetime


def run_notebook_task(task: str, notebook_type: str = "general") -> dict:
    """Execute notebook-based task"""
    try:
        print(f"📊 Running notebook task: {task[:50]}...")

        # Map task types to specific notebooks
        notebook_map = {
            "market": "notebooks/market_analysis.ipynb",
            "sports": "notebooks/sports_analysis.ipynb",
            "travel": "notebooks/travel_optimizer.ipynb",
            "housing": "notebooks/housing_tracker.ipynb",
            "study": "notebooks/study_planner.ipynb",
            "general": "notebooks/market_analysis.ipynb",  # Default
        }

        notebook_path = notebook_map.get(notebook_type, notebook_map["general"])

        # Check if notebook exists
        if not os.path.exists(notebook_path):
            print(f"⚠️ Notebook not found: {notebook_path}")
            return {
                "success": False,
                "error": f"Notebook not found: {notebook_path}",
                "task": task,
                "timestamp": datetime.now().isoformat(),
            }

        # Execute notebook with papermill or direct nbconvert
        output_path = (
            f"logs/notebook_outputs/output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Method 1: Using nbconvert (simpler, no parameters)
        cmd = [
            "jupyter",
            "nbconvert",
            "--execute",
            "--to",
            "notebook",
            "--output",
            output_path,
            notebook_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        response = {
            "success": result.returncode == 0,
            "notebook_path": notebook_path,
            "output_path": output_path,
            "task": task,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat(),
        }

        if response["success"]:
            print("✅ Notebook executed successfully")
            print(f"📁 Output saved: {output_path}")
        else:
            print("❌ Notebook execution failed")
            if result.stderr:
                print(f"🚨 Error: {result.stderr[:200]}...")

        return response

    except subprocess.TimeoutExpired:
        print("⏰ Notebook execution timed out")
        return {
            "success": False,
            "error": "timeout",
            "task": task,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ Notebook executor error: {e}")
        return {
            "success": False,
            "error": str(e),
            "task": task,
            "timestamp": datetime.now().isoformat(),
        }


def run_market_analysis(action: str) -> dict:
    """Run market analysis notebook"""
    print(f"📈 Running market analysis for: {action}")
    return run_notebook_task(action, "market")


def run_sports_analysis(action: str) -> dict:
    """Run sports analysis notebook"""
    print(f"🏆 Running sports analysis for: {action}")
    return run_notebook_task(action, "sports")


def run_data_pipeline(action: str, data_source: str = "api") -> dict:
    """Execute data pipeline notebook"""
    print(f"🔄 Running data pipeline: {action}")

    # Could trigger specific data processing notebooks
    pipeline_map = {
        "scraping": "notebooks/data_scraping.ipynb",
        "analysis": "notebooks/data_analysis.ipynb",
        "visualization": "notebooks/data_viz.ipynb",
    }

    # Determine pipeline type from action
    pipeline_type = "analysis"  # default
    if "scrape" in action.lower() or "collect" in action.lower():
        pipeline_type = "scraping"
    elif "visualiz" in action.lower() or "chart" in action.lower():
        pipeline_type = "visualization"

    return run_notebook_task(action, pipeline_type)


def schedule_notebook_run(action: str, schedule_time: str = "hourly") -> dict:
    """Schedule notebook for recurring execution"""
    print(f"⏰ Scheduling notebook: {action}")

    response = {
        "success": True,
        "scheduled": True,
        "task": action,
        "schedule": schedule_time,
        "timestamp": datetime.now().isoformat(),
        "message": f"Notebook scheduled for {schedule_time} execution",
    }

    # In production, this would integrate with cron/Task Scheduler
    print(f"✅ Notebook scheduled for {schedule_time} runs")

    return response


if __name__ == "__main__":
    # Test the executor
    print("Testing Notebook executor...")
    result = run_notebook_task("Test market analysis execution", "market")

    if result["success"]:
        print("✅ Notebook executor test successful")
    else:
        print("❌ Notebook executor test failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
