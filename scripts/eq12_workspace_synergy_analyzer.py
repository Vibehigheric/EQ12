#!/usr/bin/env python3
"""
 EQ12 WORKSPACE SYNERGY ANALYZER
Comprehensive analysis of workspace integration and component dependencies

Created: November 7, 2025
Author: EQ12 System Integration Team
Purpose: Analyze workspace synergy and ensure seamless component integration
Classification: SYSTEM ANALYSIS - WORKSPACE OPTIMIZATION
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("EQ12_SYNERGY_ANALYZER")


@dataclass
class WorkspaceComponent:
    """Workspace component information"""
    name: str
    path: str
    type: str  # python, dotnet, javascript, config, data
    dependencies: List[str]
    exports: List[str]
    integrations: List[str]
    last_modified: str
    size_mb: float
    health_status: str


@dataclass
class SynergyIssue:
    """Synergy issue tracking"""
    component_a: str
    component_b: str
    issue_type: str  # missing_dependency, circular_dependency, version_mismatch
    severity: str   # critical, high, medium, low
    description: str
    recommendation: str


class EQ12WorkspaceSynergyAnalyzer:
    """Comprehensive workspace synergy analysis"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.components: Dict[str, WorkspaceComponent] = {}
        self.synergy_issues: List[SynergyIssue] = []
        self.integration_map: Dict[str, List[str]] = {}
        
        log.info(" EQ12 Workspace Synergy Analyzer initialized")

    def discover_workspace_components(self) -> Dict[str, WorkspaceComponent]:
        """Discover all workspace components"""
        
        log.info(" Discovering workspace components...")
        
        # Main directories to analyze
        main_directories = [
            "scripts", "browser_extensions", "marketplace_analytics", 
            "business_intelligence", "dashboard", "data", "configs",
            "tests", "logs", "incident_response", "ai_models",
            "eq12_math", "eq12_backtester", "eq12_opsbot", 
            "coral_betting_ai", "backend", "frontend", "api_integrations"
        ]
        
        for dir_name in main_directories:
            dir_path = self.workspace_path / dir_name
            if dir_path.exists():
                component = self._analyze_component(dir_name, dir_path)
                self.components[dir_name] = component
        
        # Analyze root-level Python files
        for py_file in self.workspace_path.glob("*.py"):
            component = self._analyze_component(py_file.stem, py_file)
            self.components[py_file.stem] = component
        
        log.info(f" Discovered {len(self.components)} workspace components")
        return self.components

    def _analyze_component(self, name: str, path: Path) -> WorkspaceComponent:
        """Analyze individual component"""
        
        # Determine component type
        component_type = self._determine_component_type(path)
        
        # Get dependencies and exports
        dependencies = self._extract_dependencies(path)
        exports = self._extract_exports(path)
        integrations = self._extract_integrations(path)
        
        # Get metadata
        last_modified = datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        size_mb = self._calculate_size(path)
        health_status = self._assess_health(path, dependencies)
        
        return WorkspaceComponent(
            name=name,
            path=str(path),
            type=component_type,
            dependencies=dependencies,
            exports=exports,
            integrations=integrations,
            last_modified=last_modified,
            size_mb=size_mb,
            health_status=health_status
        )

    def _determine_component_type(self, path: Path) -> str:
        """Determine component type"""
        
        if path.is_file():
            if path.suffix == '.py':
                return 'python'
            elif path.suffix in ['.js', '.ts']:
                return 'javascript'
            elif path.suffix in ['.cs', '.vb']:
                return 'dotnet'
            elif path.suffix in ['.json', '.yaml', '.yml']:
                return 'config'
            else:
                return 'file'
        
        # Directory analysis
        if any(path.glob("*.py")):
            return 'python'
        elif any(path.glob("*.js")) or any(path.glob("*.ts")):
            return 'javascript'
        elif any(path.glob("*.cs")) or any(path.glob("*.vb")):
            return 'dotnet'
        elif any(path.glob("*.json")) or any(path.glob("*.yaml")):
            return 'config'
        elif path.name in ['data', 'logs', 'reports']:
            return 'data'
        else:
            return 'directory'

    def _extract_dependencies(self, path: Path) -> List[str]:
        """Extract component dependencies"""
        
        dependencies = []
        
        if path.is_file():
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    dependencies.extend(self._parse_python_imports(content))
            except Exception:
                pass
        else:
            # Analyze Python files in directory
            for py_file in path.glob("**/*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        dependencies.extend(self._parse_python_imports(content))
                except Exception:
                    continue
        
        return list(set(dependencies))  # Remove duplicates

    def _parse_python_imports(self, content: str) -> List[str]:
        """Parse Python imports from content"""
        
        imports = []
        
        # Standard import patterns
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',
            r'from\s+\.\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        # Filter for EQ12-specific imports
        eq12_imports = [imp for imp in imports if 'eq12' in imp.lower()]
        
        return eq12_imports

    def _extract_exports(self, path: Path) -> List[str]:
        """Extract component exports (functions, classes)"""
        
        exports = []
        
        if path.is_file() and path.suffix == '.py':
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Parse with AST for accurate extraction
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            exports.append(f"function:{node.name}")
                        elif isinstance(node, ast.ClassDef):
                            exports.append(f"class:{node.name}")
                except SyntaxError:
                    # Fallback to regex if AST fails
                    func_matches = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    class_matches = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    exports.extend([f"function:{f}" for f in func_matches])
                    exports.extend([f"class:{c}" for c in class_matches])
                    
            except Exception:
                pass
        
        return exports

    def _extract_integrations(self, path: Path) -> List[str]:
        """Extract integration points"""
        
        integrations = []
        
        # API integration patterns
        api_patterns = [
            'openai', 'stripe', 'ebay', 'paypal', 'telegram', 'discord',
            'chrome', 'firefox', 'edge', 'playwright', 'selenium',
            'fastapi', 'flask', 'django', 'express', 'node'
        ]
        
        if path.is_file():
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for pattern in api_patterns:
                        if pattern in content:
                            integrations.append(pattern)
            except Exception:
                pass
        
        return integrations

    def _calculate_size(self, path: Path) -> float:
        """Calculate component size in MB"""
        
        total_size = 0
        
        if path.is_file():
            total_size = path.stat().st_size
        else:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
        
        return round(total_size / (1024 * 1024), 2)

    def _assess_health(self, path: Path, dependencies: List[str]) -> str:
        """Assess component health"""
        
        # Basic health assessment
        if not path.exists():
            return "missing"
        
        if path.is_file():
            if path.stat().st_size == 0:
                return "empty"
            return "healthy"
        
        # Directory health
        if not any(path.iterdir()):
            return "empty"
        
        # Check for obvious issues
        python_files = list(path.glob("**/*.py"))
        if python_files:
            syntax_errors = 0
            for py_file in python_files[:10]:  # Sample check
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        ast.parse(content)
                except SyntaxError:
                    syntax_errors += 1
                except Exception:
                    continue
            
            if syntax_errors > len(python_files) * 0.5:
                return "issues"
        
        return "healthy"

    def analyze_synergy_issues(self) -> List[SynergyIssue]:
        """Analyze synergy issues between components"""
        
        log.info(" Analyzing synergy issues...")
        
        # Check for missing dependencies
        self._check_missing_dependencies()
        
        # Check for circular dependencies
        self._check_circular_dependencies()
        
        # Check for integration conflicts
        self._check_integration_conflicts()
        
        # Check for version mismatches
        self._check_version_mismatches()
        
        log.info(f" Found {len(self.synergy_issues)} synergy issues")
        return self.synergy_issues

    def _check_missing_dependencies(self):
        """Check for missing dependencies"""
        
        for comp_name, component in self.components.items():
            for dep in component.dependencies:
                # Check if dependency exists as component
                if dep.startswith('eq12') and dep not in self.components:
                    # Look for similar components
                    similar = self._find_similar_components(dep)
                    
                    issue = SynergyIssue(
                        component_a=comp_name,
                        component_b=dep,
                        issue_type="missing_dependency",
                        severity="high" if not similar else "medium",
                        description=f"{comp_name} depends on missing component {dep}",
                        recommendation=f"Create {dep} component or update import" + 
                                     (f". Similar: {similar}" if similar else "")
                    )
                    self.synergy_issues.append(issue)

    def _find_similar_components(self, target: str) -> str:
        """Find similar component names"""
        
        target_parts = target.lower().split('_')
        
        for comp_name in self.components.keys():
            comp_parts = comp_name.lower().split('_')
            
            # Check for partial matches
            common_parts = set(target_parts) & set(comp_parts)
            if len(common_parts) >= 2:
                return comp_name
        
        return ""

    def _check_circular_dependencies(self):
        """Check for circular dependency chains"""
        
        # Build dependency graph
        dep_graph = {}
        for comp_name, component in self.components.items():
            deps = [dep for dep in component.dependencies if dep in self.components]
            dep_graph[comp_name] = deps
        
        # Find cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, path):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                
                issue = SynergyIssue(
                    component_a=cycle[0],
                    component_b=cycle[-2],
                    issue_type="circular_dependency",
                    severity="high",
                    description=f"Circular dependency: {' -> '.join(cycle)}",
                    recommendation="Refactor to remove circular imports"
                )
                self.synergy_issues.append(issue)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dep_graph.get(node, []):
                if has_cycle(neighbor, path + [neighbor]):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for comp in dep_graph:
            if comp not in visited:
                has_cycle(comp, [comp])

    def _check_integration_conflicts(self):
        """Check for integration conflicts"""
        
        # Group components by integration type
        integration_groups = {}
        for comp_name, component in self.components.items():
            for integration in component.integrations:
                if integration not in integration_groups:
                    integration_groups[integration] = []
                integration_groups[integration].append(comp_name)
        
        # Check for potential conflicts
        conflict_patterns = {
            ('chrome', 'firefox'): "Browser extension conflict",
            ('fastapi', 'flask'): "Web framework conflict",
            ('selenium', 'playwright'): "Web automation conflict"
        }
        
        for (int1, int2), description in conflict_patterns.items():
            if int1 in integration_groups and int2 in integration_groups:
                comps1 = integration_groups[int1]
                comps2 = integration_groups[int2]
                
                if comps1 and comps2:
                    issue = SynergyIssue(
                        component_a=comps1[0],
                        component_b=comps2[0],
                        issue_type="integration_conflict",
                        severity="medium",
                        description=f"{description}: {int1} vs {int2}",
                        recommendation="Consider standardizing on one integration"
                    )
                    self.synergy_issues.append(issue)

    def _check_version_mismatches(self):
        """Check for version mismatches"""
        
        # This is a simplified check - in production, would parse actual version files
        version_indicators = ['requirements.txt', 'package.json', 'pyproject.toml']
        
        for indicator in version_indicators:
            files = list(self.workspace_path.rglob(indicator))
            if len(files) > 1:
                issue = SynergyIssue(
                    component_a="workspace",
                    component_b="dependencies",
                    issue_type="version_mismatch",
                    severity="medium",
                    description=f"Multiple {indicator} files found: {len(files)}",
                    recommendation=f"Consolidate {indicator} files for consistent dependencies"
                )
                self.synergy_issues.append(issue)

    def build_integration_map(self) -> Dict[str, List[str]]:
        """Build component integration map"""
        
        log.info(" Building integration map...")
        
        for comp_name, component in self.components.items():
            connections = []
            
            # Direct dependencies
            for dep in component.dependencies:
                if dep in self.components:
                    connections.append(dep)
            
            # Components that depend on this one
            for other_name, other_comp in self.components.items():
                if comp_name in other_comp.dependencies:
                    connections.append(other_name)
            
            self.integration_map[comp_name] = list(set(connections))
        
        return self.integration_map

    def generate_synergy_report(self) -> str:
        """Generate comprehensive synergy analysis report"""
        
        log.info(" Generating synergy report...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate statistics
        total_components = len(self.components)
        healthy_components = len([c for c in self.components.values() if c.health_status == "healthy"])
        total_size = sum(c.size_mb for c in self.components.values())
        
        # Categorize issues by severity
        critical_issues = [i for i in self.synergy_issues if i.severity == "critical"]
        high_issues = [i for i in self.synergy_issues if i.severity == "high"]
        medium_issues = [i for i in self.synergy_issues if i.severity == "medium"]
        low_issues = [i for i in self.synergy_issues if i.severity == "low"]
        
        report_content = f"""#  EQ12 WORKSPACE SYNERGY ANALYSIS REPORT

**Generated:** {timestamp}
**Analyzer:** EQ12 Workspace Synergy Analyzer
**Scope:** Complete workspace integration analysis

##  Executive Summary

The EQ12 workspace consists of **{total_components}** components with **{healthy_components}** healthy components ({healthy_components/total_components*100:.1f}% health rate).

### Key Metrics
- **Total Components:** {total_components}
- **Healthy Components:** {healthy_components} ({healthy_components/total_components*100:.1f}%)
- **Total Workspace Size:** {total_size:.1f} MB
- **Synergy Issues Found:** {len(self.synergy_issues)}

### Issue Severity Breakdown
- **Critical Issues:** {len(critical_issues)} 
- **High Issues:** {len(high_issues)}   
- **Medium Issues:** {len(medium_issues)} 
- **Low Issues:** {len(low_issues)} 

##  Component Architecture

### Component Types Distribution
"""
        
        # Component type distribution
        type_counts = {}
        for component in self.components.values():
            type_counts[component.type] = type_counts.get(component.type, 0) + 1
        
        for comp_type, count in sorted(type_counts.items()):
            report_content += f"- **{comp_type.title()}:** {count} components\n"
        
        report_content += f"""

### Core Components Overview

"""
        
        # List main components
        main_components = ['scripts', 'browser_extensions', 'marketplace_analytics', 
                          'business_intelligence', 'dashboard', 'data']
        
        for comp_name in main_components:
            if comp_name in self.components:
                comp = self.components[comp_name]
                report_content += f"""
**{comp_name.replace('_', ' ').title()}**
- **Type:** {comp.type.title()}
- **Size:** {comp.size_mb:.1f} MB
- **Health:** {comp.health_status.title()}
- **Dependencies:** {len(comp.dependencies)}
- **Integrations:** {', '.join(comp.integrations) if comp.integrations else 'None'}
- **Last Modified:** {comp.last_modified}
"""
        
        report_content += f"""

##  Integration Analysis

### Integration Map
The following components have the strongest integration relationships:

"""
        
        # Show integration connections
        for comp_name, connections in sorted(self.integration_map.items()):
            if connections:
                report_content += f"- **{comp_name}**  {', '.join(connections)}\n"
        
        report_content += f"""

### Integration Patterns
"""
        
        # Analyze integration patterns
        integration_stats = {}
        for component in self.components.values():
            for integration in component.integrations:
                integration_stats[integration] = integration_stats.get(integration, 0) + 1
        
        for integration, count in sorted(integration_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 1:
                report_content += f"- **{integration.title()}:** {count} components\n"
        
        report_content += f"""

##  Synergy Issues Analysis

### Critical Issues ({len(critical_issues)})
"""
        
        for issue in critical_issues:
            report_content += f"""
**{issue.issue_type.replace('_', ' ').title()}**
- **Components:** {issue.component_a}  {issue.component_b}
- **Description:** {issue.description}
- **Recommendation:** {issue.recommendation}
"""
        
        report_content += f"""
### High Priority Issues ({len(high_issues)})
"""
        
        for issue in high_issues:
            report_content += f"""
**{issue.issue_type.replace('_', ' ').title()}**
- **Components:** {issue.component_a}  {issue.component_b}
- **Description:** {issue.description}
- **Recommendation:** {issue.recommendation}
"""
        
        if medium_issues:
            report_content += f"""
### Medium Priority Issues ({len(medium_issues)})
"""
            for issue in medium_issues[:5]:  # Show first 5
                report_content += f"- **{issue.component_a}**  {issue.description}\n"
            
            if len(medium_issues) > 5:
                report_content += f"- ... and {len(medium_issues) - 5} more medium priority issues\n"
        
        report_content += f"""

##  Optimization Recommendations

### Immediate Actions (Next 7 Days)
"""
        
        # Generate specific recommendations
        if critical_issues or high_issues:
            report_content += "1. **Resolve Critical Dependencies:** Fix missing component dependencies\n"
            report_content += "2. **Break Circular Dependencies:** Refactor circular import chains\n"
            report_content += "3. **Consolidate Configurations:** Standardize configuration files\n"
        else:
            report_content += "1. **System Health Excellent:** No critical issues found\n"
            report_content += "2. **Continue Monitoring:** Maintain current integration patterns\n"
        
        report_content += f"""
### Strategic Improvements (Next 30 Days)
1. **Standardize Integration Patterns:** Consolidate similar integrations
2. **Improve Component Documentation:** Add integration documentation
3. **Implement Dependency Management:** Use centralized dependency tracking
4. **Create Integration Tests:** Add automated synergy testing

### Long-term Vision (Next 90 Days)
1. **Microservices Architecture:** Consider splitting large components
2. **API Gateway Pattern:** Standardize component communication
3. **Configuration Management:** Implement centralized configuration
4. **Monitoring Dashboard:** Real-time synergy monitoring

##  Synergy Score

### Overall Workspace Synergy Score: {self._calculate_synergy_score()}/100

**Score Breakdown:**
- **Component Health:** {healthy_components/total_components*30:.1f}/30
- **Integration Quality:** {self._score_integrations()}/25
- **Dependency Management:** {self._score_dependencies()}/25  
- **Issue Resolution:** {self._score_issues()}/20

##  Success Metrics

### Target KPIs
- **Component Health Rate:** >95% (Current: {healthy_components/total_components*100:.1f}%)
- **Critical Issues:** 0 (Current: {len(critical_issues)})
- **Integration Standardization:** >80% (Current: {self._score_integrations():.1f}%)
- **Dependency Conflicts:** <5 (Current: {len([i for i in self.synergy_issues if 'dependency' in i.issue_type])})

### Monitoring Recommendations
1. **Daily Health Checks:** Automated component health monitoring
2. **Weekly Synergy Reports:** Regular integration analysis
3. **Monthly Architecture Reviews:** Component relationship assessment
4. **Quarterly Optimization Sprints:** Major synergy improvements

---

**Next Steps:**
1. Address critical and high priority issues
2. Implement recommended optimizations
3. Set up automated synergy monitoring
4. Schedule regular architecture reviews

**Contact:** EQ12 System Integration Team
**Classification:** System Analysis - Workspace Optimization
**Status:** Analysis Complete - Action Required

---

*Report Generated: {timestamp}*
*Analysis Duration: Complete workspace scan*
*Components Analyzed: {total_components}*
"""
        
        # Save report
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.workspace_path / f"workspace_synergy_analysis_{timestamp_file}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        log.info(f" Synergy analysis report saved: {report_file}")
        return str(report_file)

    def _calculate_synergy_score(self) -> int:
        """Calculate overall synergy score"""
        
        total_components = len(self.components)
        healthy_components = len([c for c in self.components.values() if c.health_status == "healthy"])
        
        # Component health (30 points)
        health_score = (healthy_components / total_components) * 30 if total_components > 0 else 0
        
        # Integration quality (25 points)
        integration_score = self._score_integrations()
        
        # Dependency management (25 points)
        dependency_score = self._score_dependencies()
        
        # Issue resolution (20 points)
        issue_score = self._score_issues()
        
        total_score = health_score + integration_score + dependency_score + issue_score
        return int(min(100, max(0, total_score)))

    def _score_integrations(self) -> float:
        """Score integration quality"""
        
        if not self.components:
            return 0
        
        # Count standardized integrations
        common_integrations = ['openai', 'stripe', 'fastapi', 'playwright']
        standardized_count = 0
        
        for integration in common_integrations:
            components_with_integration = sum(1 for c in self.components.values() 
                                            if integration in c.integrations)
            if components_with_integration > 1:
                standardized_count += 1
        
        return (standardized_count / len(common_integrations)) * 25

    def _score_dependencies(self) -> float:
        """Score dependency management"""
        
        if not self.synergy_issues:
            return 25
        
        dependency_issues = [i for i in self.synergy_issues if 'dependency' in i.issue_type]
        critical_dependency_issues = [i for i in dependency_issues if i.severity == "critical"]
        
        if not dependency_issues:
            return 25
        
        # Penalize based on issue severity
        penalty = len(critical_dependency_issues) * 10 + len(dependency_issues) * 2
        return max(0, 25 - penalty)

    def _score_issues(self) -> float:
        """Score based on issue resolution"""
        
        if not self.synergy_issues:
            return 20
        
        critical_count = len([i for i in self.synergy_issues if i.severity == "critical"])
        high_count = len([i for i in self.synergy_issues if i.severity == "high"])
        
        # Penalize based on severity
        penalty = critical_count * 8 + high_count * 4
        return max(0, 20 - penalty)


def main():
    parser = argparse.ArgumentParser(description=" EQ12 Workspace Synergy Analyzer")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--action", choices=["analyze", "report", "full"], 
                       default="full", help="Analysis action")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = EQ12WorkspaceSynergyAnalyzer(args.workspace)
    
    print("" + "="*70)
    print(" EQ12 WORKSPACE SYNERGY ANALYSIS")
    print("" + "="*70)
    
    # Discover components
    components = analyzer.discover_workspace_components()
    
    # Analyze synergy
    issues = analyzer.analyze_synergy_issues()
    
    # Build integration map
    integration_map = analyzer.build_integration_map()
    
    # Generate report
    report_file = analyzer.generate_synergy_report()
    
    # Summary output
    healthy_count = len([c for c in components.values() if c.health_status == "healthy"])
    synergy_score = analyzer._calculate_synergy_score()
    
    print(f"\n WORKSPACE SYNERGY ANALYSIS COMPLETE")
    print(f"    Components Analyzed: {len(components)}")
    print(f"    Healthy Components: {healthy_count} ({healthy_count/len(components)*100:.1f}%)")
    print(f"    Synergy Issues: {len(issues)}")
    print(f"    Integration Points: {len(integration_map)}")
    print(f"    Synergy Score: {synergy_score}/100")
    
    print(f"\n ISSUE BREAKDOWN")
    critical_issues = [i for i in issues if i.severity == "critical"]
    high_issues = [i for i in issues if i.severity == "high"]
    medium_issues = [i for i in issues if i.severity == "medium"]
    
    print(f"    Critical: {len(critical_issues)}")
    print(f"    High: {len(high_issues)}")
    print(f"    Medium: {len(medium_issues)}")
    
    print(f"\n REPORT GENERATED")
    print(f"    Report File: {report_file}")
    
    if synergy_score >= 80:
        print(f"\n EXCELLENT SYNERGY - Workspace components work well together!")
    elif synergy_score >= 60:
        print(f"\n GOOD SYNERGY - Minor improvements recommended")
    else:
        print(f"\n SYNERGY ISSUES - Action required to improve integration")
    
    print("" + "="*70)


if __name__ == "__main__":
    main()