#!/usr/bin/env python3
"""
Civil Service Job Tracker (Buffalo Stack Component)
Monitors civil service job postings for union positions (Code 14215)
"""

import argparse
import datetime
import logging
import os
import sqlite3
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

DB_PATH = BASE_DIR / "civil_service_jobs.db"

# Set up logging
log_file = LOGS_DIR / f"civil_service_{datetime.date.today()}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)


class CivilServiceTracker:
    def __init__(self) -> bool:
        self.db_path = DB_PATH
        self.init_database()

    def init_database(self) -> bool:
        """Initialize SQLite database for job tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE,
                    title TEXT,
                    department TEXT,
                    location TEXT,
                    salary_range TEXT,
                    posting_date TEXT,
                    closing_date TEXT,
                    description TEXT,
                    requirements TEXT,
                    union_code TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified BOOLEAN DEFAULT FALSE
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tracking_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    jobs_found INTEGER,
                    new_jobs INTEGER,
                    errors INTEGER,
                    notes TEXT
                )
            """
            )
            logging.info("Database initialized")

    def generate_mock_jobs(self, source_name) -> bool:
        """Generate mock job data for demonstration"""
        import random

        job_titles = [
            "Police Officer",
            "Firefighter",
            "EMT Paramedic",
            "911 Dispatcher",
            "Correctional Officer",
            "Court Clerk",
            "Public Works Technician",
            "Building Inspector",
        ]

        departments = [
            "Police Department",
            "Fire Department",
            "Emergency Services",
            "Public Safety",
            "Public Works",
            "Municipal Court",
        ]

        locations = [
            "Downtown",
            "North District",
            "South District",
            "East Side",
            "West End",
        ]

        mock_jobs = []
        num_jobs = random.randint(1, 5)

        for _i in range(num_jobs):
            job_id = f"{source_name.lower().replace(' ', '_')}_{random.randint(1000, 9999)}"
            title = random.choice(job_titles)
            department = random.choice(departments)
            location = random.choice(locations)

            job = {
                "job_id": job_id,
                "title": title,
                "department": department,
                "location": location,
                "salary_range": f"${random.randint(45000, 85000):,} - ${random.randint(85000, 120000):,}",
                "posting_date": datetime.date.today().isoformat(),
                "closing_date": (
                    datetime.date.today() + datetime.timedelta(days=random.randint(14, 45))
                ).isoformat(),
                "description": f"Full-time {title} position in {department}. Union eligible under code 14215.",
                "requirements": "High school diploma, valid driver's license, background check required.",
                "union_code": "14215",
            }
            mock_jobs.append(job)

        return mock_jobs

    def fetch_civil_service_jobs(self) -> bool:
        """Fetch civil service jobs from various sources"""
        jobs_found = []

        # Mock civil service API calls - replace with real endpoints
        sources = [
            {
                "name": "City Jobs Portal",
                "url": "https://api.example-city.gov/jobs",
                "params": {"category": "civil_service", "union_eligible": "true"},
            },
            {
                "name": "County HR System",
                "url": "https://hr.example-county.gov/api/jobs",
                "params": {"type": "union", "code": "14215"},
            },
        ]

        for source in sources:
            try:
                # In a real implementation, these would be actual API calls
                # For demo purposes, we'll simulate job data
                mock_jobs = self.generate_mock_jobs(source["name"])
                jobs_found.extend(mock_jobs)
                logging.info(f"Fetched {len(mock_jobs)} jobs from {source['name']}")

            except Exception as e:
                logging.error(f"Failed to fetch from {source['name']}: {e}")

        return jobs_found

    def save_jobs(self, jobs) -> bool:
        """Save jobs to database, avoiding duplicates"""
        new_jobs = 0

        with sqlite3.connect(self.db_path) as conn:
            for job in jobs:
                try:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO jobs
                        (job_id, title, department, location, salary_range,
                         posting_date, closing_date, description, requirements, union_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            job["job_id"],
                            job["title"],
                            job["department"],
                            job["location"],
                            job["salary_range"],
                            job["posting_date"],
                            job["closing_date"],
                            job["description"],
                            job["requirements"],
                            job["union_code"],
                        ),
                    )

                    if conn.total_changes > 0:
                        new_jobs += 1
                        logging.info(f"New job saved: {job['title']} - {job['department']}")

                except Exception as e:
                    logging.error(f"Failed to save job {job.get('job_id', 'unknown')}: {e}")

        return new_jobs

    def get_recent_jobs(self, days=7) -> bool:
        """Get jobs discovered in the last N days"""
        cutoff_date = datetime.date.today() - datetime.timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM jobs
                WHERE discovered_at > date(?)
                ORDER BY discovered_at DESC
            """,
                (cutoff_date,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def send_notifications(self, new_jobs) -> bool:
        """Send notifications for new jobs"""
        if not new_jobs:
            return

        # Telegram notification
        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if telegram_token and telegram_chat_id:
            message = f"🚨 {len(new_jobs)} New Civil Service Jobs Found!\n\n"

            for job in new_jobs[:3]:  # Limit to first 3 jobs to avoid long messages
                message += f"• {job['title']} - {job['department']}\n"
                message += f"  Salary: {job['salary_range']}\n"
                message += f"  Closes: {job['closing_date']}\n\n"

            if len(new_jobs) > 3:
                message += f"...and {len(new_jobs) - 3} more jobs\n"

            try:
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                data = {"chat_id": telegram_chat_id, "text": message}
                response = requests.post(url, data=data, timeout=10)

                if response.status_code == 200:
                    logging.info("Telegram notification sent successfully")
                else:
                    logging.warning(f"Telegram notification failed: {response.status_code}")

            except Exception as e:
                logging.error(f"Failed to send Telegram notification: {e}")

        # Email notification (placeholder)
        # Could integrate with SendGrid, SMTP, etc.
        logging.info(f"Notifications processed for {len(new_jobs)} new jobs")

    def log_run(self, jobs_found, new_jobs, errors=0, notes="") -> bool:
        """Log this tracking run"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tracking_log (jobs_found, new_jobs, errors, notes)
                VALUES (?, ?, ?, ?)
            """,
                (jobs_found, new_jobs, errors, notes),
            )

    def run(self) -> bool:
        """Main tracking run"""
        logging.info("=== Civil Service Tracker Run Started ===")

        try:
            # Fetch jobs from all sources
            all_jobs = self.fetch_civil_service_jobs()
            logging.info(f"Total jobs fetched: {len(all_jobs)}")

            # Save new jobs to database
            new_jobs_count = self.save_jobs(all_jobs)

            # Get the actual new job records for notifications
            if new_jobs_count > 0:
                new_jobs = self.get_recent_jobs(days=1)
                self.send_notifications(new_jobs)

            # Log this run
            self.log_run(len(all_jobs), new_jobs_count, 0, "Successful run")

            logging.info(f"=== Run Complete: {new_jobs_count} new jobs found ===")
            return True

        except Exception as e:
            logging.exception(f"Tracker run failed: {e}")
            self.log_run(0, 0, 1, f"Failed: {e}")
            return False


def main() -> bool:
    parser = argparse.ArgumentParser(description="Civil Service Job Tracker")
    parser.add_argument("--init-only", action="store_true", help="Initialize database only")
    parser.add_argument("--show-recent", type=int, default=0, help="Show recent jobs (days)")
    parser.add_argument("--stats", action="store_true", help="Show tracking statistics")

    args = parser.parse_args()

    tracker = CivilServiceTracker()

    if args.init_only:
        print("✅ Database initialized successfully")
        return

    if args.show_recent > 0:
        jobs = tracker.get_recent_jobs(args.show_recent)
        print(f"\n📋 Jobs from last {args.show_recent} days:")
        for job in jobs:
            print(f"• {job['title']} - {job['department']} ({job['salary_range']})")
        return

    if args.stats:
        with sqlite3.connect(tracker.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM jobs")
            total_jobs = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM tracking_log")
            total_runs = cursor.fetchone()[0]

            print("\n📊 Tracking Statistics:")
            print(f"Total jobs tracked: {total_jobs}")
            print(f"Total runs: {total_runs}")
        return

    # Normal run
    success = tracker.run()
    exit_code = 0 if success else 1
    exit(exit_code)


if __name__ == "__main__":
    main()
