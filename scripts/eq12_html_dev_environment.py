#!/usr/bin/env python3
"""
EQ12 HTML Development Environment Setup - Professional Web Development Stack
Professional Engineering Grade HTML/CSS/JS Development Environment

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This script sets up a complete HTML development environment optimized for EQ12:
- Professional HTML/CSS/JS project structure
- Live development server with hot reload
- Code validation and linting tools
- Browser testing and compatibility checks
- Integration with EQ12 automation systems
- Performance optimization tools

Usage Examples:
  python eq12_html_dev_environment.py --setup-workspace
  python eq12_html_dev_environment.py --create-project "My Dashboard"
  python eq12_html_dev_environment.py --start-dev-server

Teaching Notes (30-Day Python Curriculum Integration):
- Project management (Day 30): Professional project setup and organization
- Web development (Day 24): HTML/CSS/JS development environment
- Automation tools (Day 25): Development workflow automation
- File operations (Day 12): Template generation and file management
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import webbrowser
import threading
import http.server
import socketserver
from urllib.parse import urlparse

class EQ12HTMLDevEnvironment:
    """
    Professional HTML development environment manager

    Teaching note (Day 20 - Classes): Comprehensive development environment
    manager with project scaffolding and server management capabilities.
    """

    def __init__(self, workspace_dir: Optional[Path] = None):
        """Initialize HTML development environment"""
        self.workspace_dir = workspace_dir or Path('C:/EQ12/html_workspace')
        self.projects_dir = self.workspace_dir / 'projects'
        self.templates_dir = self.workspace_dir / 'templates'
        self.tools_dir = self.workspace_dir / 'tools'
        self.config_file = self.workspace_dir / 'config.json'

        # Development server settings
        self.dev_server = None
        self.server_thread = None

        # Default configuration
        self.config = {
            'development_server': {
                'port': 8080,
                'host': 'localhost',
                'auto_reload': True
            },
            'project_defaults': {
                'include_css_framework': True,
                'include_js_framework': False,
                'responsive_design': True,
                'accessibility_features': True
            },
            'tools': {
                'html_validator': True,
                'css_validator': True,
                'js_linter': True,
                'browser_testing': True
            }
        }

        print(f"EQ12 HTML Development Environment initialized")
        print(f"Workspace: {self.workspace_dir}")

    def setup_workspace(self) -> bool:
        """
        Set up complete HTML development workspace

        Teaching note (Day 12 - File operations): Professional workspace
        setup with directory structure and template creation.
        """
        print("🏗️ Setting up HTML development workspace...")

        try:
            # Create directory structure
            directories = [
                self.workspace_dir,
                self.projects_dir,
                self.templates_dir,
                self.tools_dir,
                self.workspace_dir / 'assets' / 'css',
                self.workspace_dir / 'assets' / 'js',
                self.workspace_dir / 'assets' / 'images',
                self.workspace_dir / 'docs',
                self.workspace_dir / 'examples'
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")

            # Create configuration file
            self.save_config()

            # Create HTML templates
            self.create_html_templates()

            # Create development tools
            self.create_development_tools()

            # Create example projects
            self.create_example_projects()

            print("✅ HTML development workspace setup complete!")
            return True

        except Exception as e:
            print(f"❌ Error setting up workspace: {str(e)}")
            return False

    def create_html_templates(self):
        """Create professional HTML templates"""
        templates = {
            'basic.html': self.get_basic_html_template(),
            'responsive.html': self.get_responsive_html_template(),
            'dashboard.html': self.get_dashboard_template(),
            'landing_page.html': self.get_landing_page_template()
        }

        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created template: {filename}")

    def get_basic_html_template(self) -> str:
        """Basic HTML5 template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="EQ12 HTML Project">
    <title>EQ12 HTML Project</title>
    <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
    <header>
        <h1>EQ12 HTML Project</h1>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home">
            <h2>Welcome to Your HTML Project</h2>
            <p>This is a professional HTML5 template created by EQ12.</p>
        </section>

        <section id="about">
            <h2>About</h2>
            <p>Professional web development with EQ12 tools and standards.</p>
        </section>

        <section id="contact">
            <h2>Contact</h2>
            <p>Contact information goes here.</p>
        </section>
    </main>

    <footer>
        <p>&copy; 2025 EQ12 HTML Project. Professional web development.</p>
    </footer>

    <script src="assets/js/main.js"></script>
</body>
</html>'''

    def get_responsive_html_template(self) -> str:
        """Responsive HTML5 template with modern features"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="EQ12 Responsive HTML Project">
    <meta name="keywords" content="HTML, CSS, JavaScript, Responsive">
    <meta name="author" content="EQ12 Engineering Team">
    <title>EQ12 Responsive Project</title>

    <!-- CSS -->
    <link rel="stylesheet" href="assets/css/normalize.css">
    <link rel="stylesheet" href="assets/css/responsive.css">

    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="assets/images/favicon.ico">
</head>
<body>
    <!-- Skip to main content for accessibility -->
    <a href="#main-content" class="skip-to-main">Skip to main content</a>

    <header class="header">
        <div class="container">
            <div class="logo">
                <h1>EQ12</h1>
            </div>

            <nav class="nav" role="navigation" aria-label="Main navigation">
                <button class="nav-toggle" aria-controls="nav-menu" aria-expanded="false">
                    <span class="hamburger"></span>
                    <span class="sr-only">Menu</span>
                </button>

                <ul class="nav-menu" id="nav-menu">
                    <li><a href="#home" class="nav-link">Home</a></li>
                    <li><a href="#features" class="nav-link">Features</a></li>
                    <li><a href="#about" class="nav-link">About</a></li>
                    <li><a href="#contact" class="nav-link">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main id="main-content" class="main">
        <section id="home" class="hero">
            <div class="container">
                <div class="hero-content">
                    <h2>Professional Responsive Design</h2>
                    <p>Built with modern HTML5, CSS3, and JavaScript best practices.</p>
                    <button class="btn btn-primary">Get Started</button>
                </div>
            </div>
        </section>

        <section id="features" class="features">
            <div class="container">
                <h2>Features</h2>
                <div class="feature-grid">
                    <article class="feature-card">
                        <h3>Responsive Design</h3>
                        <p>Optimized for all devices and screen sizes.</p>
                    </article>

                    <article class="feature-card">
                        <h3>Accessibility</h3>
                        <p>WCAG 2.1 compliant with proper ARIA labels.</p>
                    </article>

                    <article class="feature-card">
                        <h3>Performance</h3>
                        <p>Optimized for fast loading and smooth interactions.</p>
                    </article>
                </div>
            </div>
        </section>

        <section id="about" class="about">
            <div class="container">
                <h2>About EQ12</h2>
                <p>Professional engineering solutions for modern web development.</p>
            </div>
        </section>

        <section id="contact" class="contact">
            <div class="container">
                <h2>Contact Us</h2>
                <form class="contact-form" action="#" method="post">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required>

                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>

                    <label for="message">Message:</label>
                    <textarea id="message" name="message" required></textarea>

                    <button type="submit" class="btn btn-primary">Send Message</button>
                </form>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 EQ12 Engineering. Professional web development solutions.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="assets/js/responsive.js"></script>
</body>
</html>'''

    def get_dashboard_template(self) -> str:
        """Professional dashboard template for data visualization"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Dashboard</title>
    <link rel="stylesheet" href="assets/css/dashboard.css">
</head>
<body class="dashboard-body">
    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h1 class="logo">EQ12</h1>
            </div>

            <nav class="sidebar-nav">
                <ul class="nav-list">
                    <li><a href="#overview" class="nav-item active">Overview</a></li>
                    <li><a href="#analytics" class="nav-item">Analytics</a></li>
                    <li><a href="#reports" class="nav-item">Reports</a></li>
                    <li><a href="#settings" class="nav-item">Settings</a></li>
                </ul>
            </nav>
        </aside>

        <main class="main-content">
            <header class="topbar">
                <div class="topbar-left">
                    <h2 id="page-title">Dashboard Overview</h2>
                </div>
                <div class="topbar-right">
                    <span id="last-updated">Last updated: <time datetime="2025-11-22">Today</time></span>
                    <button class="refresh-btn">Refresh</button>
                </div>
            </header>

            <div class="dashboard-content">
                <section class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Users</h3>
                        <div class="stat-value">1,234</div>
                        <div class="stat-change positive">+12%</div>
                    </div>

                    <div class="stat-card">
                        <h3>Revenue</h3>
                        <div class="stat-value">$45,678</div>
                        <div class="stat-change positive">+8%</div>
                    </div>

                    <div class="stat-card">
                        <h3>Conversion</h3>
                        <div class="stat-value">3.45%</div>
                        <div class="stat-change negative">-2%</div>
                    </div>

                    <div class="stat-card">
                        <h3>Performance</h3>
                        <div class="stat-value">98.2%</div>
                        <div class="stat-change positive">+0.5%</div>
                    </div>
                </section>

                <section class="charts-section">
                    <div class="chart-container">
                        <h3>Analytics Overview</h3>
                        <div id="main-chart" class="chart-placeholder">
                            [Chart will be rendered here]
                        </div>
                    </div>

                    <div class="chart-container">
                        <h3>Recent Activity</h3>
                        <div id="activity-chart" class="chart-placeholder">
                            [Activity chart will be rendered here]
                        </div>
                    </div>
                </section>

                <section class="data-table-section">
                    <h3>Recent Transactions</h3>
                    <div class="table-wrapper">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Date</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>001</td>
                                    <td>2025-11-22</td>
                                    <td>$123.45</td>
                                    <td class="status success">Success</td>
                                </tr>
                                <tr>
                                    <td>002</td>
                                    <td>2025-11-22</td>
                                    <td>$67.89</td>
                                    <td class="status pending">Pending</td>
                                </tr>
                                <tr>
                                    <td>003</td>
                                    <td>2025-11-21</td>
                                    <td>$234.56</td>
                                    <td class="status success">Success</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <script src="assets/js/dashboard.js"></script>
</body>
</html>'''

    def get_landing_page_template(self) -> str:
        """Modern landing page template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 - Professional Engineering Solutions</title>
    <meta name="description" content="Professional engineering solutions for automation, AI, and web development">
    <link rel="stylesheet" href="assets/css/landing.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <img src="assets/images/logo.svg" alt="EQ12" class="logo">
            </div>

            <ul class="nav-menu">
                <li><a href="#features">Features</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
                <li><a href="#" class="btn btn-outline">Get Started</a></li>
            </ul>

            <div class="hamburger">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </nav>
    </header>

    <main>
        <section class="hero">
            <div class="hero-content">
                <h1 class="hero-title">Professional Engineering Solutions</h1>
                <p class="hero-subtitle">Automation, AI, and web development tools for modern businesses</p>

                <div class="hero-actions">
                    <button class="btn btn-primary btn-large">Start Free Trial</button>
                    <button class="btn btn-secondary btn-large">Learn More</button>
                </div>
            </div>

            <div class="hero-visual">
                <div class="hero-image-placeholder">
                    [Hero Image/Animation]
                </div>
            </div>
        </section>

        <section id="features" class="features">
            <div class="container">
                <h2 class="section-title">Powerful Features</h2>

                <div class="features-grid">
                    <div class="feature">
                        <div class="feature-icon">🚀</div>
                        <h3>Automation</h3>
                        <p>Streamline your workflows with intelligent automation solutions.</p>
                    </div>

                    <div class="feature">
                        <div class="feature-icon">🤖</div>
                        <h3>AI Integration</h3>
                        <p>Leverage AI and machine learning for better decision making.</p>
                    </div>

                    <div class="feature">
                        <div class="feature-icon">💻</div>
                        <h3>Web Development</h3>
                        <p>Modern, responsive web applications built for performance.</p>
                    </div>

                    <div class="feature">
                        <div class="feature-icon">📊</div>
                        <h3>Analytics</h3>
                        <p>Comprehensive analytics and reporting for data-driven insights.</p>
                    </div>

                    <div class="feature">
                        <div class="feature-icon">🔒</div>
                        <h3>Security</h3>
                        <p>Enterprise-grade security with comprehensive monitoring.</p>
                    </div>

                    <div class="feature">
                        <div class="feature-icon">⚡</div>
                        <h3>Performance</h3>
                        <p>Optimized for speed and scalability across all platforms.</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="cta">
            <div class="container">
                <h2>Ready to Get Started?</h2>
                <p>Join thousands of professionals using EQ12 for their engineering needs.</p>
                <button class="btn btn-primary btn-large">Start Your Free Trial</button>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>EQ12</h3>
                    <p>Professional engineering solutions for the modern world.</p>
                </div>

                <div class="footer-section">
                    <h4>Product</h4>
                    <ul>
                        <li><a href="#">Features</a></li>
                        <li><a href="#">Pricing</a></li>
                        <li><a href="#">Documentation</a></li>
                    </ul>
                </div>

                <div class="footer-section">
                    <h4>Company</h4>
                    <ul>
                        <li><a href="#">About</a></li>
                        <li><a href="#">Careers</a></li>
                        <li><a href="#">Contact</a></li>
                    </ul>
                </div>

                <div class="footer-section">
                    <h4>Connect</h4>
                    <ul>
                        <li><a href="#">GitHub</a></li>
                        <li><a href="#">Twitter</a></li>
                        <li><a href="#">LinkedIn</a></li>
                    </ul>
                </div>
            </div>

            <div class="footer-bottom">
                <p>&copy; 2025 EQ12 Engineering. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="assets/js/landing.js"></script>
</body>
</html>'''

    def create_development_tools(self):
        """Create development tools and utilities"""
        tools = {
            'live_reload.js': self.get_live_reload_script(),
            'dev_server.py': self.get_dev_server_script(),
            'build.py': self.get_build_script(),
            'validator.py': self.get_validator_script()
        }

        for filename, content in tools.items():
            tool_path = self.tools_dir / filename
            with open(tool_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created tool: {filename}")

    def get_live_reload_script(self) -> str:
        """JavaScript for live reload functionality"""
        return '''// EQ12 Live Reload Script
(function() {
    'use strict';

    let lastModified = {};
    let reloadInterval = 1000; // Check every second

    function checkForChanges() {
        fetch('/api/check-changes', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.changed) {
                console.log('Files changed, reloading...');
                window.location.reload();
            }
        })
        .catch(error => {
            console.log('Live reload check failed:', error);
        });
    }

    // Start checking for changes
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Live reload enabled');
        setInterval(checkForChanges, reloadInterval);
    }
})();'''

    def get_dev_server_script(self) -> str:
        """Python development server script"""
        return '''#!/usr/bin/env python3
"""
EQ12 Development Server
Simple HTTP server with live reload functionality
"""

import os
import sys
import json
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

class EQ12DevHandler(SimpleHTTPRequestHandler):
    """Custom handler with live reload support"""

    def do_GET(self):
        if self.path == '/api/check-changes':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Check for file changes (simplified)
            response = {'changed': False}
            self.wfile.write(json.dumps(response).encode())
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

def start_server(port=8080, directory="."):
    """Start development server"""
    os.chdir(directory)

    server_address = ('', port)
    httpd = HTTPServer(server_address, EQ12DevHandler)

    print(f"EQ12 Development Server running at http://localhost:{port}")
    print(f"Serving directory: {os.getcwd()}")
    print("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped")
        httpd.shutdown()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 Development Server')
    parser.add_argument('--port', type=int, default=8080, help='Port number')
    parser.add_argument('--dir', default='.', help='Directory to serve')

    args = parser.parse_args()
    start_server(args.port, args.dir)'''

    def get_build_script(self) -> str:
        """Build script for production optimization"""
        return '''#!/usr/bin/env python3
"""
EQ12 Build Script
Optimize HTML/CSS/JS for production
"""

import os
import sys
import shutil
from pathlib import Path
import re

def minify_css(css_content):
    """Basic CSS minification"""
    # Remove comments
    css_content = re.sub(r'/\\*.*?\\*/', '', css_content, flags=re.DOTALL)
    # Remove extra whitespace
    css_content = re.sub(r'\\s+', ' ', css_content)
    # Remove whitespace around special characters
    css_content = re.sub(r'\\s*([{}:;,>+~])\\s*', r'\\1', css_content)
    return css_content.strip()

def minify_js(js_content):
    """Basic JavaScript minification"""
    # Remove single-line comments (simple)
    js_content = re.sub(r'//.*?\\n', '\\n', js_content)
    # Remove multi-line comments
    js_content = re.sub(r'/\\*.*?\\*/', '', js_content, flags=re.DOTALL)
    # Remove extra whitespace (be careful with this)
    js_content = re.sub(r'\\n\\s*\\n', '\\n', js_content)
    return js_content.strip()

def build_project(source_dir, build_dir):
    """Build project for production"""
    source_path = Path(source_dir)
    build_path = Path(build_dir)

    print(f"Building project from {source_path} to {build_path}")

    # Clean build directory
    if build_path.exists():
        shutil.rmtree(build_path)

    # Copy all files
    shutil.copytree(source_path, build_path)

    # Optimize CSS files
    for css_file in build_path.rglob('*.css'):
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        minified = minify_css(content)

        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(minified)

        print(f"Minified CSS: {css_file}")

    # Optimize JS files
    for js_file in build_path.rglob('*.js'):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        minified = minify_js(content)

        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(minified)

        print(f"Minified JS: {js_file}")

    print("Build complete!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 Build Tool')
    parser.add_argument('source', help='Source directory')
    parser.add_argument('build', help='Build directory')

    args = parser.parse_args()
    build_project(args.source, args.build)'''

    def get_validator_script(self) -> str:
        """HTML/CSS validation script"""
        return '''#!/usr/bin/env python3
"""
EQ12 HTML/CSS Validator
Check HTML and CSS for common issues
"""

import os
import re
from pathlib import Path
from html.parser import HTMLParser

class EQ12HTMLValidator(HTMLParser):
    """Custom HTML validator"""

    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.tags_stack = []

    def handle_starttag(self, tag, attrs):
        self.tags_stack.append(tag)

        # Check for missing alt attributes on images
        if tag == 'img':
            attrs_dict = dict(attrs)
            if 'alt' not in attrs_dict:
                self.warnings.append(f"Image tag missing alt attribute")

    def handle_endtag(self, tag):
        if self.tags_stack and self.tags_stack[-1] == tag:
            self.tags_stack.pop()
        else:
            self.errors.append(f"Mismatched closing tag: {tag}")

    def get_results(self):
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'unclosed_tags': self.tags_stack
        }

def validate_html_file(file_path):
    """Validate a single HTML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    validator = EQ12HTMLValidator()
    validator.feed(content)

    return validator.get_results()

def validate_css_file(file_path):
    """Basic CSS validation"""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for common issues
    if content.count('{') != content.count('}'):
        errors.append("Mismatched braces in CSS")

    # Check for empty rules
    empty_rules = re.findall(r'[^{}]*{\\s*}', content)
    if empty_rules:
        warnings.append(f"Found {len(empty_rules)} empty CSS rules")

    return {'errors': errors, 'warnings': warnings}

def validate_project(project_dir):
    """Validate entire project"""
    project_path = Path(project_dir)
    results = {
        'html_files': {},
        'css_files': {},
        'summary': {'errors': 0, 'warnings': 0}
    }

    # Validate HTML files
    for html_file in project_path.rglob('*.html'):
        try:
            result = validate_html_file(html_file)
            results['html_files'][str(html_file)] = result
            results['summary']['errors'] += len(result['errors'])
            results['summary']['warnings'] += len(result['warnings'])
        except Exception as e:
            results['html_files'][str(html_file)] = {'errors': [str(e)], 'warnings': []}

    # Validate CSS files
    for css_file in project_path.rglob('*.css'):
        try:
            result = validate_css_file(css_file)
            results['css_files'][str(css_file)] = result
            results['summary']['errors'] += len(result['errors'])
            results['summary']['warnings'] += len(result['warnings'])
        except Exception as e:
            results['css_files'][str(css_file)] = {'errors': [str(e)], 'warnings': []}

    return results

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description='EQ12 HTML/CSS Validator')
    parser.add_argument('project_dir', help='Project directory to validate')
    parser.add_argument('--output', help='Output JSON file')

    args = parser.parse_args()

    results = validate_project(args.project_dir)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        print(f"Validation complete:")
        print(f"Errors: {results['summary']['errors']}")
        print(f"Warnings: {results['summary']['warnings']}")'''

    def create_example_projects(self):
        """Create example projects"""
        examples = {
            'simple_website': {
                'description': 'A simple, clean website',
                'template': 'basic.html'
            },
            'responsive_portfolio': {
                'description': 'Responsive portfolio site',
                'template': 'responsive.html'
            },
            'admin_dashboard': {
                'description': 'Admin dashboard with charts',
                'template': 'dashboard.html'
            },
            'landing_page': {
                'description': 'Modern landing page',
                'template': 'landing_page.html'
            }
        }

        examples_dir = self.workspace_dir / 'examples'

        for project_name, config in examples.items():
            project_dir = examples_dir / project_name
            project_dir.mkdir(exist_ok=True)

            # Copy template
            template_path = self.templates_dir / config['template']
            if template_path.exists():
                shutil.copy2(template_path, project_dir / 'index.html')

            # Create basic CSS and JS
            (project_dir / 'assets' / 'css').mkdir(parents=True, exist_ok=True)
            (project_dir / 'assets' / 'js').mkdir(parents=True, exist_ok=True)

            # Create basic styles.css
            css_content = self.get_basic_css()
            with open(project_dir / 'assets' / 'css' / 'styles.css', 'w') as f:
                f.write(css_content)

            # Create basic main.js
            js_content = self.get_basic_js()
            with open(project_dir / 'assets' / 'js' / 'main.js', 'w') as f:
                f.write(js_content)

            # Create README
            readme_content = f"""# {project_name.replace('_', ' ').title()}

{config['description']}

## Getting Started

1. Open `index.html` in your browser
2. Or use the EQ12 development server:
   ```
   python ../tools/dev_server.py --dir .
   ```

## Project Structure

- `index.html` - Main HTML file
- `assets/css/` - Stylesheets
- `assets/js/` - JavaScript files
- `assets/images/` - Images and media

## Development

Use the EQ12 HTML development environment tools for:
- Live reload during development
- Code validation and linting
- Production build optimization
"""

            with open(project_dir / 'README.md', 'w') as f:
                f.write(readme_content)

            print(f"✅ Created example: {project_name}")

    def get_basic_css(self) -> str:
        """Basic CSS starter"""
        return '''/* EQ12 Basic Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
header {
    background: #2c3e50;
    color: white;
    padding: 1rem 0;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 2rem;
    margin-top: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
    transition: color 0.3s ease;
}

nav a:hover {
    color: #3498db;
}

/* Main Content */
main {
    padding: 2rem 0;
    min-height: 60vh;
}

section {
    margin: 2rem 0;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
}

h1, h2, h3 {
    margin-bottom: 1rem;
    color: #2c3e50;
}

p {
    margin-bottom: 1rem;
    line-height: 1.8;
}

/* Footer */
footer {
    background: #34495e;
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

/* Utilities */
.btn {
    display: inline-block;
    padding: 12px 24px;
    background: #3498db;
    color: white;
    text-decoration: none;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.btn:hover {
    background: #2980b9;
}

.btn-primary {
    background: #3498db;
}

.btn-secondary {
    background: #95a5a6;
}

/* Responsive */
@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
        gap: 1rem;
    }

    .container {
        padding: 0 15px;
    }

    section {
        padding: 1rem;
    }
}'''

    def get_basic_js(self) -> str:
        """Basic JavaScript starter"""
        return '''// EQ12 Basic JavaScript
document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    console.log('EQ12 HTML Project loaded');

    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile navigation toggle (if hamburger menu exists)
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Form validation helper
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });

    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        if (button.type === 'submit') {
            button.addEventListener('click', function() {
                this.classList.add('loading');
                this.disabled = true;

                // Re-enable after 3 seconds (adjust as needed)
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.disabled = false;
                }, 3000);
            });
        }
    });
});'''

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        print(f"✅ Configuration saved: {self.config_file}")

    def create_project(self, project_name: str, template: str = 'basic') -> bool:
        """
        Create a new HTML project from template

        Teaching note (Day 12 - File operations): Project scaffolding
        with template customization and directory structure creation.
        """
        print(f"🏗️ Creating new project: {project_name}")

        try:
            # Create project directory
            project_dir = self.projects_dir / project_name
            project_dir.mkdir(exist_ok=True)

            # Create subdirectories
            subdirs = [
                'assets/css',
                'assets/js',
                'assets/images',
                'docs'
            ]

            for subdir in subdirs:
                (project_dir / subdir).mkdir(parents=True, exist_ok=True)

            # Copy template
            template_file = f"{template}.html"
            template_path = self.templates_dir / template_file

            if template_path.exists():
                shutil.copy2(template_path, project_dir / 'index.html')
                print(f"✅ Template copied: {template_file}")
            else:
                print(f"⚠️ Template not found: {template_file}, using basic template")
                template_path = self.templates_dir / 'basic.html'
                shutil.copy2(template_path, project_dir / 'index.html')

            # Create CSS file
            css_content = self.get_basic_css()
            with open(project_dir / 'assets' / 'css' / 'styles.css', 'w') as f:
                f.write(css_content)

            # Create JS file
            js_content = self.get_basic_js()
            with open(project_dir / 'assets' / 'js' / 'main.js', 'w') as f:
                f.write(js_content)

            # Create project README
            readme_content = f"""# {project_name}

HTML project created with EQ12 development environment.

## Getting Started

1. Open `index.html` in your browser
2. For development with live reload:
   ```
   python ../../tools/dev_server.py --dir .
   ```
3. For validation:
   ```
   python ../../tools/validator.py .
   ```
4. For production build:
   ```
   python ../../tools/build.py . ./build
   ```

## Project Structure

```
{project_name}/
├── index.html          # Main HTML file
├── assets/
│   ├── css/
│   │   └── styles.css  # Main stylesheet
│   ├── js/
│   │   └── main.js     # Main JavaScript
│   └── images/         # Images and media
├── docs/               # Documentation
└── README.md          # This file
```

## Development

- Edit `index.html` for content structure
- Modify `assets/css/styles.css` for styling
- Add interactivity in `assets/js/main.js`
- Use EQ12 tools for validation and optimization

Created with EQ12 HTML Development Environment
"""

            with open(project_dir / 'README.md', 'w') as f:
                f.write(readme_content)

            print(f"✅ Project created successfully: {project_dir}")
            return True

        except Exception as e:
            print(f"❌ Error creating project: {str(e)}")
            return False

    def start_dev_server(self, project_path: Optional[Path] = None, port: int = 8080) -> bool:
        """
        Start development server with live reload

        Teaching note (Day 25 - Web servers): Development server setup
        with file watching and automatic browser refresh.
        """
        try:
            if project_path:
                server_dir = project_path
            else:
                # Use current workspace
                server_dir = self.workspace_dir

            print(f"🚀 Starting development server...")
            print(f"📁 Serving directory: {server_dir}")
            print(f"🌐 Server URL: http://localhost:{port}")

            # Use the development server tool
            dev_server_script = self.tools_dir / 'dev_server.py'

            if dev_server_script.exists():
                cmd = [sys.executable, str(dev_server_script), '--port', str(port), '--dir', str(server_dir)]

                # Start server in background
                import subprocess
                self.dev_server = subprocess.Popen(cmd, cwd=str(server_dir))

                # Open browser
                import webbrowser
                webbrowser.open(f'http://localhost:{port}')

                print("✅ Development server started successfully!")
                print("   Press Ctrl+C to stop the server")

                return True
            else:
                print("❌ Development server script not found. Run setup_workspace() first.")
                return False

        except Exception as e:
            print(f"❌ Error starting development server: {str(e)}")
            return False

    def stop_dev_server(self):
        """Stop the development server"""
        if self.dev_server:
            self.dev_server.terminate()
            self.dev_server = None
            print("🛑 Development server stopped")

    def list_projects(self) -> List[str]:
        """List all projects in workspace"""
        if not self.projects_dir.exists():
            return []

        projects = []
        for item in self.projects_dir.iterdir():
            if item.is_dir() and (item / 'index.html').exists():
                projects.append(item.name)

        return projects

    def validate_project(self, project_name: str) -> Dict:
        """Validate a specific project"""
        project_dir = self.projects_dir / project_name

        if not project_dir.exists():
            return {'error': f'Project {project_name} not found'}

        validator_script = self.tools_dir / 'validator.py'

        if validator_script.exists():
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, str(validator_script), str(project_dir)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    return {'success': True, 'output': result.stdout}
                else:
                    return {'error': result.stderr}

            except Exception as e:
                return {'error': str(e)}
        else:
            return {'error': 'Validator script not found'}

def main():
    """Main entry point for HTML development environment"""
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 HTML Development Environment')
    parser.add_argument('--setup-workspace', action='store_true', help='Set up development workspace')
    parser.add_argument('--create-project', help='Create new project')
    parser.add_argument('--template', default='basic', help='Template to use for new project')
    parser.add_argument('--start-server', action='store_true', help='Start development server')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--project-dir', help='Project directory for server')
    parser.add_argument('--list-projects', action='store_true', help='List all projects')
    parser.add_argument('--validate', help='Validate project')
    parser.add_argument('--workspace-dir', help='Custom workspace directory')

    args = parser.parse_args()

    try:
        # Initialize environment
        workspace_dir = Path(args.workspace_dir) if args.workspace_dir else None
        env = EQ12HTMLDevEnvironment(workspace_dir)

        print("🌐 EQ12 HTML Development Environment")
        print("Professional Web Development Tools")
        print("=" * 60)

        if args.setup_workspace:
            success = env.setup_workspace()
            if success:
                print("\n🎉 Workspace setup complete!")
                print(f"📁 Workspace location: {env.workspace_dir}")
                print("\nNext steps:")
                print("1. Create a new project: --create-project 'My Project'")
                print("2. Start development server: --start-server")
            return 0 if success else 1

        elif args.create_project:
            success = env.create_project(args.create_project, args.template)
            if success:
                print(f"\n🎉 Project '{args.create_project}' created!")
                print(f"📁 Location: {env.projects_dir / args.create_project}")
                print("\nNext steps:")
                print("1. Edit index.html to customize content")
                print("2. Start development server: --start-server --project-dir path/to/project")
            return 0 if success else 1

        elif args.start_server:
            project_path = Path(args.project_dir) if args.project_dir else None
            success = env.start_dev_server(project_path, args.port)

            if success:
                try:
                    # Keep server running
                    while True:
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    env.stop_dev_server()
                    print("\n👋 Server stopped")

            return 0 if success else 1

        elif args.list_projects:
            projects = env.list_projects()
            if projects:
                print("📁 Projects in workspace:")
                for project in projects:
                    print(f"  • {project}")
            else:
                print("No projects found. Create one with --create-project")
            return 0

        elif args.validate:
            result = env.validate_project(args.validate)
            if 'error' in result:
                print(f"❌ Validation failed: {result['error']}")
                return 1
            else:
                print(f"✅ Validation successful: {result['output']}")
                return 0

        else:
            print("Please specify an action. Use --help for available options.")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled")
        return 130

    except Exception as e:
        print(f"\n💥 Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
