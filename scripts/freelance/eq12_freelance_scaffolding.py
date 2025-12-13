#!/usr/bin/env python3
"""
💼 EQ12 Freelance Scaffolding System
Project setup automation, client communication templates, invoice/timesheet tooling
Complete freelance developer workflow automation
"""

import datetime
import json
import logging
import re
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/freelance_scaffolding.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ClientInfo:
    """Client information structure"""

    client_id: str
    name: str
    company: str
    email: str
    phone: str
    timezone: str
    hourly_rate: Decimal
    preferred_communication: str  # email, slack, teams, etc.
    project_types: list[str]
    notes: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()


@dataclass
class ProjectConfig:
    """Project configuration structure"""

    project_id: str
    name: str
    client_id: str
    description: str
    project_type: str  # web, api, automation, analysis, etc.
    tech_stack: list[str]
    estimated_hours: int
    hourly_rate: Decimal
    start_date: str
    end_date: str
    status: str = "planning"  # planning, active, completed, paused
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()


@dataclass
class TimeEntry:
    """Time tracking entry"""

    entry_id: str
    project_id: str
    date: str
    start_time: str
    end_time: str
    hours: Decimal
    description: str
    billable: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()


class FreelanceDatabase:
    """JSON-based database for freelance data"""

    def __init__(self, data_dir: str = "data/freelance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.clients_file = self.data_dir / "clients.json"
        self.projects_file = self.data_dir / "projects.json"
        self.timesheet_file = self.data_dir / "timesheet.json"

        self._ensure_files()

    def _ensure_files(self):
        """Ensure all data files exist"""
        for file_path in [self.clients_file, self.projects_file, self.timesheet_file]:
            if not file_path.exists():
                file_path.write_text("[]", encoding="utf-8")

    def _load_json(self, file_path: Path) -> list[dict]:
        """Load JSON data from file"""
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_json(self, file_path: Path, data: list[dict]):
        """Save JSON data to file"""
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_client(self, client: ClientInfo) -> bool:
        """Add new client"""
        clients = self._load_json(self.clients_file)
        client_dict = asdict(client)
        client_dict["hourly_rate"] = float(client.hourly_rate)
        clients.append(client_dict)
        self._save_json(self.clients_file, clients)
        return True

    def get_clients(self) -> list[dict]:
        """Get all clients"""
        return self._load_json(self.clients_file)

    def add_project(self, project: ProjectConfig) -> bool:
        """Add new project"""
        projects = self._load_json(self.projects_file)
        project_dict = asdict(project)
        project_dict["hourly_rate"] = float(project.hourly_rate)
        projects.append(project_dict)
        self._save_json(self.projects_file, projects)
        return True

    def get_projects(self) -> list[dict]:
        """Get all projects"""
        return self._load_json(self.projects_file)

    def add_time_entry(self, entry: TimeEntry) -> bool:
        """Add time tracking entry"""
        timesheet = self._load_json(self.timesheet_file)
        entry_dict = asdict(entry)
        entry_dict["hours"] = float(entry.hours)
        timesheet.append(entry_dict)
        self._save_json(self.timesheet_file, timesheet)
        return True

    def get_timesheet(self, project_id: str | None = None) -> list[dict]:
        """Get timesheet entries, optionally filtered by project"""
        entries = self._load_json(self.timesheet_file)
        if project_id:
            return [e for e in entries if e.get("project_id") == project_id]
        return entries


class ProjectTemplates:
    """Project template system"""

    def __init__(self, templates_dir: str = "templates/freelance"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._create_default_templates()

    def _create_default_templates(self):
        """Create default project templates"""

        # Web Development Template
        web_template = {
            "name": "Web Development",
            "description": "Full-stack web application development",
            "tech_stack": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB"],
            "folder_structure": [
                "src/",
                "src/components/",
                "src/pages/",
                "src/utils/",
                "public/",
                "tests/",
                "docs/",
                "config/",
            ],
            "initial_files": {
                "README.md": "# {project_name}\n\n{description}\n\n## Tech Stack\n{tech_stack}\n",
                "package.json": '{\n  "name": "{project_name_slug}",\n  "version": "1.0.0"\n}',
                ".gitignore": "node_modules/\n.env\ndist/\nbuild/\n",
                "src/index.js": "// {project_name} - Main Entry Point\nconsole.log('Hello World!');",
            },
        }

        # Python Automation Template
        automation_template = {
            "name": "Python Automation",
            "description": "Python-based automation and scripting project",
            "tech_stack": ["Python", "Pandas", "Requests", "BeautifulSoup", "Selenium"],
            "folder_structure": [
                "src/",
                "tests/",
                "data/",
                "logs/",
                "config/",
                "docs/",
            ],
            "initial_files": {
                "README.md": "# {project_name}\n\n{description}\n\n## Requirements\n- Python 3.8+\n",
                "requirements.txt": "requests\npandas\nbeautifulsoup4\nselenium\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\ndata/sensitive/\nlogs/*.log\n",
                "src/main.py": '#!/usr/bin/env python3\n"""\n{project_name} - Main Module\n"""\n\ndef main():\n    print(\'Starting {project_name}\')\n\nif __name__ == \'__main__\':\n    main()',
            },
        }

        # Data Analysis Template
        analysis_template = {
            "name": "Data Analysis",
            "description": "Data analysis and visualization project",
            "tech_stack": [
                "Python",
                "Jupyter",
                "Pandas",
                "NumPy",
                "Matplotlib",
                "Seaborn",
            ],
            "folder_structure": [
                "notebooks/",
                "data/raw/",
                "data/processed/",
                "src/",
                "reports/",
                "visualizations/",
            ],
            "initial_files": {
                "README.md": "# {project_name} - Data Analysis\n\n{description}\n",
                "requirements.txt": "jupyter\npandas\nnumpy\nmatplotlib\nseaborn\nscipy\n",
                "notebooks/01_exploratory_analysis.ipynb": '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}',
                "src/data_processor.py": "import pandas as pd\nimport numpy as np\n\nclass DataProcessor:\n    def __init__(self):\n        pass",
            },
        }

        templates = {
            "web_development": web_template,
            "python_automation": automation_template,
            "data_analysis": analysis_template,
        }

        for template_name, template_data in templates.items():
            template_file = self.templates_dir / f"{template_name}.json"
            if not template_file.exists():
                template_file.write_text(json.dumps(template_data, indent=2), encoding="utf-8")

    def get_template(self, template_name: str) -> dict | None:
        """Get project template by name"""
        template_file = self.templates_dir / f"{template_name}.json"
        if template_file.exists():
            return json.loads(template_file.read_text(encoding="utf-8"))
        return None

    def list_templates(self) -> list[str]:
        """List available templates"""
        return [f.stem for f in self.templates_dir.glob("*.json")]


class ProjectGenerator:
    """Generate new projects from templates"""

    def __init__(self, projects_dir: str = "freelance_projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.templates = ProjectTemplates()

    def create_project(self, project_config: ProjectConfig, template_name: str) -> bool:
        """Create new project from template"""
        try:
            template = self.templates.get_template(template_name)
            if not template:
                logger.error(f"Template not found: {template_name}")
                return False

            # Create project directory
            project_dir = self.projects_dir / project_config.name
            project_dir.mkdir(exist_ok=True)

            # Create folder structure
            for folder in template.get("folder_structure", []):
                (project_dir / folder).mkdir(parents=True, exist_ok=True)

            # Create initial files
            for file_path, content in template.get("initial_files", {}).items():
                formatted_content = self._format_template_content(content, project_config, template)
                (project_dir / file_path).write_text(formatted_content, encoding="utf-8")

            # Create project metadata
            metadata = {
                "project_config": asdict(project_config),
                "template_used": template_name,
                "created_at": datetime.datetime.now().isoformat(),
                "folder_structure": template.get("folder_structure", []),
                "tech_stack": template.get("tech_stack", []),
            }

            (project_dir / ".eq12_project.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )

            logger.info(f"✅ Project created: {project_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create project: {e}")
            return False

    def _format_template_content(
        self, content: str, project_config: ProjectConfig, template: dict
    ) -> str:
        """Format template content with project variables"""
        replacements = {
            "{project_name}": project_config.name,
            "{project_name_slug}": re.sub(r"[^a-z0-9]+", "-", project_config.name.lower()).strip(
                "-"
            ),
            "{description}": project_config.description,
            "{tech_stack}": "\n".join(f"- {tech}" for tech in template.get("tech_stack", [])),
        }

        formatted_content = content
        for placeholder, replacement in replacements.items():
            formatted_content = formatted_content.replace(placeholder, replacement)

        return formatted_content


class InvoiceGenerator:
    """Generate professional invoices"""

    def __init__(self, database: FreelanceDatabase):
        self.database = database

    def generate_invoice(self, project_id: str, invoice_number: str | None = None) -> dict:
        """Generate invoice for project"""
        if not invoice_number:
            invoice_number = (
                f"INV-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
            )

        # Get project and client info
        projects = self.database.get_projects()
        project = next((p for p in projects if p["project_id"] == project_id), None)

        if not project:
            raise ValueError(f"Project not found: {project_id}")

        clients = self.database.get_clients()
        client = next((c for c in clients if c["client_id"] == project["client_id"]), None)

        if not client:
            raise ValueError(f"Client not found: {project['client_id']}")

        # Get time entries
        time_entries = self.database.get_timesheet(project_id)
        billable_entries = [e for e in time_entries if e.get("billable", True)]

        # Calculate totals
        total_hours = sum(Decimal(str(e["hours"])) for e in billable_entries)
        hourly_rate = Decimal(str(project["hourly_rate"]))
        subtotal = total_hours * hourly_rate

        # Generate invoice
        invoice = {
            "invoice_number": invoice_number,
            "invoice_date": datetime.date.today().isoformat(),
            "due_date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            "client": {
                "name": client["name"],
                "company": client["company"],
                "email": client["email"],
            },
            "project": {"name": project["name"], "description": project["description"]},
            "line_items": [
                {
                    "description": f"{project['name']} - Development Hours",
                    "quantity": float(total_hours),
                    "rate": float(hourly_rate),
                    "amount": float(subtotal),
                }
            ],
            "subtotal": float(subtotal),
            "tax_rate": 0.0,
            "tax_amount": 0.0,
            "total": float(subtotal),
            "time_entries": billable_entries,
            "payment_terms": "Net 30 days",
            "notes": "Thank you for your business!",
        }

        return invoice

    def save_invoice_html(self, invoice: dict, output_path: str):
        """Save invoice as HTML file"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Invoice {invoice_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .invoice-info {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
        .client-info {{ width: 45%; }}
        .invoice-details {{ width: 45%; text-align: right; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .total-row {{ font-weight: bold; background-color: #f9f9f9; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>INVOICE</h1>
        <h2>#{invoice_number}</h2>
    </div>

    <div class="invoice-info">
        <div class="client-info">
            <h3>Bill To:</h3>
            <p><strong>{client_name}</strong><br>
               {client_company}<br>
               {client_email}</p>
        </div>
        <div class="invoice-details">
            <p><strong>Invoice Date:</strong> {invoice_date}<br>
               <strong>Due Date:</strong> {due_date}<br>
               <strong>Project:</strong> {project_name}</p>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th>Quantity</th>
                <th>Rate</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {line_items}
            <tr class="total-row">
                <td colspan="3"><strong>Total</strong></td>
                <td><strong>${total:.2f}</strong></td>
            </tr>
        </tbody>
    </table>

    <div class="footer">
        <p><strong>Payment Terms:</strong> {payment_terms}</p>
        <p>{notes}</p>
    </div>
</body>
</html>
        """

        # Format line items
        line_items_html = ""
        for _item in invoice["line_items"]:
            line_items_html += """
            <tr>
                <td>{item["description"]}</td>
                <td>{item["quantity"]:.1f} hrs</td>
                <td>${item["rate"]:.2f}</td>
                <td>${item["amount"]:.2f}</td>
            </tr>
            """

        # Format HTML
        html_content = html_template.format(
            invoice_number=invoice["invoice_number"],
            client_name=invoice["client"]["name"],
            client_company=invoice["client"]["company"],
            client_email=invoice["client"]["email"],
            invoice_date=invoice["invoice_date"],
            due_date=invoice["due_date"],
            project_name=invoice["project"]["name"],
            line_items=line_items_html,
            total=invoice["total"],
            payment_terms=invoice["payment_terms"],
            notes=invoice["notes"],
        )

        Path(output_path).write_text(html_content, encoding="utf-8")
        logger.info(f"✅ Invoice saved: {output_path}")


class FreelanceScaffold:
    """Main freelance scaffolding system"""

    def __init__(self):
        self.database = FreelanceDatabase()
        self.project_generator = ProjectGenerator()
        self.invoice_generator = InvoiceGenerator(self.database)

    def setup_new_client(self, name: str, company: str, email: str, hourly_rate: float) -> str:
        """Setup new client"""
        client_id = str(uuid.uuid4())

        client = ClientInfo(
            client_id=client_id,
            name=name,
            company=company,
            email=email,
            phone="",
            timezone="UTC",
            hourly_rate=Decimal(str(hourly_rate)),
            preferred_communication="email",
            project_types=[],
        )

        self.database.add_client(client)
        logger.info(f"✅ Client created: {name} ({client_id})")
        return client_id

    def create_new_project(
        self,
        name: str,
        client_id: str,
        description: str,
        template_name: str,
        estimated_hours: int,
        hourly_rate: float,
    ) -> str:
        """Create new project"""
        project_id = str(uuid.uuid4())

        project_config = ProjectConfig(
            project_id=project_id,
            name=name,
            client_id=client_id,
            description=description,
            project_type=template_name,
            tech_stack=[],
            estimated_hours=estimated_hours,
            hourly_rate=Decimal(str(hourly_rate)),
            start_date=datetime.date.today().isoformat(),
            end_date=(
                datetime.date.today() + datetime.timedelta(days=estimated_hours // 8)
            ).isoformat(),
        )

        # Add to database
        self.database.add_project(project_config)

        # Generate project files
        self.project_generator.create_project(project_config, template_name)

        logger.info(f"✅ Project created: {name} ({project_id})")
        return project_id

    def log_time(self, project_id: str, hours: float, description: str) -> str:
        """Log time for project"""
        entry_id = str(uuid.uuid4())

        entry = TimeEntry(
            entry_id=entry_id,
            project_id=project_id,
            date=datetime.date.today().isoformat(),
            start_time="09:00",
            end_time=f"{9 + int(hours):02d}:{int((hours % 1) * 60):02d}",
            hours=Decimal(str(hours)),
            description=description,
        )

        self.database.add_time_entry(entry)
        logger.info(f"✅ Time logged: {hours}h for {description}")
        return entry_id

    def generate_project_invoice(self, project_id: str, output_dir: str = "invoices") -> str:
        """Generate invoice for project"""
        Path(output_dir).mkdir(exist_ok=True)

        invoice = self.invoice_generator.generate_invoice(project_id)

        output_file = Path(output_dir) / f"{invoice['invoice_number']}.html"
        self.invoice_generator.save_invoice_html(invoice, str(output_file))

        return str(output_file)

    def run_interactive_setup(self):
        """Interactive setup mode"""
        print("\n💼 EQ12 FREELANCE SCAFFOLDING SYSTEM")
        print("====================================")

        while True:
            print("\n📋 MAIN MENU:")
            print("1. Setup New Client")
            print("2. Create New Project")
            print("3. Log Time")
            print("4. Generate Invoice")
            print("5. View Projects")
            print("6. View Timesheet")
            print("7. Exit")

            choice = input("\nSelect option (1-7): ").strip()

            try:
                if choice == "1":
                    self._setup_client_interactive()
                elif choice == "2":
                    self._create_project_interactive()
                elif choice == "3":
                    self._log_time_interactive()
                elif choice == "4":
                    self._generate_invoice_interactive()
                elif choice == "5":
                    self._view_projects()
                elif choice == "6":
                    self._view_timesheet()
                elif choice == "7":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-7.")

            except Exception as e:
                print(f"❌ Error: {e}")

    def _setup_client_interactive(self):
        """Interactive client setup"""
        print("\n👤 SETUP NEW CLIENT")
        print("-------------------")

        name = input("Client name: ").strip()
        company = input("Company: ").strip()
        email = input("Email: ").strip()
        hourly_rate = float(input("Hourly rate ($): ").strip())

        client_id = self.setup_new_client(name, company, email, hourly_rate)
        print(f"✅ Client created with ID: {client_id}")

    def _create_project_interactive(self):
        """Interactive project creation"""
        print("\n🚀 CREATE NEW PROJECT")
        print("---------------------")

        # Show available clients
        clients = self.database.get_clients()
        if not clients:
            print("❌ No clients found. Please setup a client first.")
            return

        print("\nAvailable clients:")
        for i, client in enumerate(clients, 1):
            print(f"{i}. {client['name']} ({client['company']})")

        client_idx = int(input("\nSelect client (number): ")) - 1
        client_id = clients[client_idx]["client_id"]

        # Show available templates
        templates = self.project_generator.templates.list_templates()
        print("\nAvailable templates:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template}")

        template_idx = int(input("\nSelect template (number): ")) - 1
        template_name = templates[template_idx]

        # Get project details
        name = input("Project name: ").strip()
        description = input("Project description: ").strip()
        estimated_hours = int(input("Estimated hours: ").strip())
        hourly_rate = float(input("Hourly rate ($): ").strip())

        project_id = self.create_new_project(
            name, client_id, description, template_name, estimated_hours, hourly_rate
        )
        print(f"✅ Project created with ID: {project_id}")

    def _log_time_interactive(self):
        """Interactive time logging"""
        print("\n⏰ LOG TIME")
        print("-----------")

        # Show available projects
        projects = self.database.get_projects()
        if not projects:
            print("❌ No projects found. Please create a project first.")
            return

        print("\nActive projects:")
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project['name']}")

        project_idx = int(input("\nSelect project (number): ")) - 1
        project_id = projects[project_idx]["project_id"]

        hours = float(input("Hours worked: ").strip())
        description = input("Work description: ").strip()

        entry_id = self.log_time(project_id, hours, description)
        print(f"✅ Time logged with ID: {entry_id}")

    def _generate_invoice_interactive(self):
        """Interactive invoice generation"""
        print("\n💰 GENERATE INVOICE")
        print("-------------------")

        # Show projects with time entries
        projects = self.database.get_projects()
        timesheet = self.database.get_timesheet()

        projects_with_time = []
        for project in projects:
            project_entries = [e for e in timesheet if e["project_id"] == project["project_id"]]
            if project_entries:
                total_hours = sum(e["hours"] for e in project_entries)
                projects_with_time.append((project, total_hours))

        if not projects_with_time:
            print("❌ No projects with logged time found.")
            return

        print("\nProjects with logged time:")
        for i, (project, hours) in enumerate(projects_with_time, 1):
            print(f"{i}. {project['name']} ({hours:.1f} hours)")

        project_idx = int(input("\nSelect project (number): ")) - 1
        project_id = projects_with_time[project_idx][0]["project_id"]

        invoice_file = self.generate_project_invoice(project_id)
        print(f"✅ Invoice generated: {invoice_file}")

    def _view_projects(self):
        """View all projects"""
        projects = self.database.get_projects()
        clients = self.database.get_clients()

        print("\n📊 ALL PROJECTS")
        print("---------------")

        for project in projects:
            client = next((c for c in clients if c["client_id"] == project["client_id"]), None)
            client_name = client["name"] if client else "Unknown"

            print(f"🚀 {project['name']}")
            print(f"   Client: {client_name}")
            print(f"   Status: {project['status']}")
            print(f"   Rate: ${project['hourly_rate']:.2f}/hr")
            print(f"   Estimated: {project['estimated_hours']} hours")
            print()

    def _view_timesheet(self):
        """View timesheet summary"""
        timesheet = self.database.get_timesheet()
        projects = self.database.get_projects()

        print("\n⏰ TIMESHEET SUMMARY")
        print("--------------------")

        # Group by project
        project_hours = {}
        for entry in timesheet:
            project_id = entry["project_id"]
            if project_id not in project_hours:
                project_hours[project_id] = 0
            project_hours[project_id] += entry["hours"]

        for project_id, total_hours in project_hours.items():
            project = next((p for p in projects if p["project_id"] == project_id), None)
            project_name = project["name"] if project else "Unknown Project"

            print(f"📊 {project_name}: {total_hours:.1f} hours")


def main():
    """Main entry point"""
    scaffold = FreelanceScaffold()

    # Demo mode
    print("💼 EQ12 Freelance Scaffolding Demo")

    # Create demo client
    client_id = scaffold.setup_new_client("John Doe", "Tech Corp", "john@techcorp.com", 85.0)

    # Create demo project
    project_id = scaffold.create_new_project(
        "E-commerce Platform",
        client_id,
        "Build modern e-commerce platform with React and Node.js",
        "web_development",
        120,
        85.0,
    )

    # Log some time
    scaffold.log_time(project_id, 8.5, "Initial setup and database design")
    scaffold.log_time(project_id, 6.0, "Frontend component development")
    scaffold.log_time(project_id, 4.5, "API endpoint implementation")

    # Generate invoice
    invoice_file = scaffold.generate_project_invoice(project_id)
    print(f"📄 Demo invoice generated: {invoice_file}")

    # Start interactive mode
    scaffold.run_interactive_setup()


if __name__ == "__main__":
    main()
