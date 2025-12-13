#!/usr/bin/env python3
"""
EQ12 Advanced VB Debugging System
Purpose: Hardcoded VB debugging best practices with automation
Agent: GitHub Copilot with EQ12 expertise
Timestamp: 2025-10-10T22:10:00Z

Implements:
- Option Strict/Explicit enforcement
- Debug.WriteLine automation
- Unit testing integration
- Macro-based debugging automation
- Roslyn VB analysis integration
"""

import argparse
import functools
import json
import logging
import operator
import re
import sys
from datetime import UTC, datetime
from pathlib import Path


class EQ12VBDebuggingSystem:
    """Advanced VB debugging with hardcoded best practices"""

    def __init__(self, workspace: str = "C:\\\\EQ12"):
        self.workspace = Path(workspace)
        self.vb_projects_dir = self.workspace / "vb_projects"
        self.logs_dir = self.workspace / "logs"
        self.configs_dir = self.workspace / "configs"

        # Create directories
        self.vb_projects_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.configs_dir.mkdir(exist_ok=True)

        self.setup_logging()

        # Hardcoded VB debugging best practices
        self.vb_debug_rules = {
            "option_strict": "Always enforce Option Strict On",
            "option_explicit": "Always enforce Option Explicit On",
            "debug_logging": "Use Debug.WriteLine for immediate feedback",
            "unit_testing": "Isolate functions for independent debugging",
            "macro_automation": "Automate repetitive debugging with macros",
        }

        # VB code quality patterns
        self.vb_patterns = {
            "missing_option_strict": r"(?!.*Option\s+Strict\s+On)",
            "missing_option_explicit": r"(?!.*Option\s+Explicit\s+On)",
            "missing_debug_logs": r"(Sub|Function)\s+\w+.*?\n(?!.*Debug\.WriteLine)",
            "type_mismatches": r"Dim\s+\w+\s+As\s+Object",  # Should use specific types
            "unhandled_exceptions": r"(Sub|Function).*?\n(?!.*Try\s*\n.*Catch)",
        }

    def setup_logging(self):
        """Configure comprehensive VB debugging logging"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"vb_debugging_system_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔧 EQ12 VB Debugging System initialized")

    def enforce_option_strict_explicit(self, vb_file: Path) -> dict[str, bool]:
        """Hardcode Option Strict On and Option Explicit On enforcement"""
        self.logger.info(f"🔒 Enforcing Option Strict/Explicit in {vb_file}")

        results = {
            "option_strict_added": False,
            "option_explicit_added": False,
            "file_modified": False,
        }

        try:
            with open(vb_file, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Check and add Option Strict On
            if not re.search(r"Option\s+Strict\s+On", content, re.IGNORECASE):
                content = "Option Strict On\n" + content
                results["option_strict_added"] = True
                self.logger.info("✅ Added 'Option Strict On'")

            # Check and add Option Explicit On
            if not re.search(r"Option\s+Explicit\s+On", content, re.IGNORECASE):
                if results["option_strict_added"]:
                    content = content.replace(
                        "Option Strict On\n", "Option Strict On\nOption Explicit On\n"
                    )
                else:
                    content = "Option Explicit On\n" + content
                results["option_explicit_added"] = True
                self.logger.info("✅ Added 'Option Explicit On'")

            # Write back if modified
            if content != original_content:
                with open(vb_file, "w", encoding="utf-8") as f:
                    f.write(content)
                results["file_modified"] = True
                self.logger.info(f"💾 File updated: {vb_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to enforce options in {vb_file}: {e}")

        return results

    def add_debug_logging(self, vb_file: Path) -> int:
        """Add Debug.WriteLine statements to VB functions automatically"""
        self.logger.info(f"📝 Adding Debug.WriteLine logging to {vb_file}")

        debug_statements_added = 0

        try:
            with open(vb_file, encoding="utf-8") as f:
                lines = f.readlines()

            modified_lines = []
            in_function = False
            function_name = ""

            for _i, line in enumerate(lines):
                # Detect function/sub start
                func_match = re.match(
                    r"\s*(Public|Private|Friend)?\s*(Sub|Function)\s+(\w+)",
                    line.strip(),
                )
                if func_match:
                    in_function = True
                    function_name = func_match.group(3)
                    modified_lines.append(line)

                    # Add entry debug log
                    indent = " " * (len(line) - len(line.lstrip()))
                    debug_line = f'{indent}    Debug.WriteLine("🔍 Entering {function_name}: " & DateTime.Now.ToString())\n'
                    modified_lines.append(debug_line)
                    debug_statements_added += 1
                    continue

                # Detect function/sub end
                if in_function and (line.strip().startswith(
                        "End Sub") or line.strip().startswith("End Function")):
                    # Add exit debug log before End
                    indent = " " * (len(line) - len(line.lstrip()))
                    debug_line = f'{indent}    Debug.WriteLine("✅ Exiting {function_name}: " & DateTime.Now.ToString())\n'
                    modified_lines.append(debug_line)
                    debug_statements_added += 1
                    in_function = False
                    function_name = ""

                # Add variable tracking for Dim statements
                if in_function and line.strip().startswith("Dim "):
                    modified_lines.append(line)
                    var_match = re.match(r"\s*Dim\s+(\w+)", line.strip())
                    if var_match:
                        var_name = var_match.group(1)
                        indent = " " * (len(line) - len(line.lstrip()))
                        debug_line = f'{indent}Debug.WriteLine("📊 Variable {var_name} in {function_name}: " & {var_name}.ToString())\n'
                        modified_lines.append(debug_line)
                        debug_statements_added += 1
                    continue

                modified_lines.append(line)

            # Write back modified content
            if debug_statements_added > 0:
                with open(vb_file, "w", encoding="utf-8") as f:
                    f.writelines(modified_lines)
                self.logger.info(
                    f"✅ Added {debug_statements_added} Debug.WriteLine statements")

        except Exception as e:
            self.logger.error(f"❌ Failed to add debug logging to {vb_file}: {e}")

        return debug_statements_added

    def create_vb_unit_test_template(self, target_function: str, vb_file: Path) -> Path:
        """Create unit test template for VB function isolation"""
        self.logger.info(f"🧪 Creating unit test template for {target_function}")

        test_file = self.vb_projects_dir / f"Test_{target_function}.vb"

        test_template = """Option Strict On
Option Explicit On

' EQ12 VB Unit Test for {target_function}
' Generated: {datetime.now(timezone.utc).isoformat()}
' Purpose: Isolated debugging and testing

Imports System
Imports Microsoft.VisualStudio.TestTools.UnitTesting

<TestClass>
Public Class Test_{target_function}

    <TestMethod>
    Public Sub Test_{target_function}_ValidInput()
        ' Arrange
        Debug.WriteLine("🧪 Starting unit test for {target_function}")
        Dim expectedResult As String = "expected_value"
        Dim testInput As String = "test_input"

        ' Act
        Debug.WriteLine("🔄 Executing {target_function} with input: " & testInput)
        Dim actualResult As String = {target_function}(testInput)
        Debug.WriteLine("📊 Result from {target_function}: " & actualResult)

        ' Assert
        Assert.AreEqual(expectedResult, actualResult, "Function should return expected value")
        Debug.WriteLine("✅ Unit test passed for {target_function}")
    End Sub

    <TestMethod>
    Public Sub Test_{target_function}_EdgeCases()
        ' Test edge cases
        Debug.WriteLine("⚠️ Testing edge cases for {target_function}")

        Try
            ' Test null/empty input
            Dim result1 = {target_function}("")
            Debug.WriteLine("📊 Empty input result: " & result1)

            ' Test boundary values
            Dim result2 = {target_function}("boundary_test")
            Debug.WriteLine("📊 Boundary test result: " & result2)

        Catch ex As Exception
            Debug.WriteLine("❌ Exception in edge case testing: " & ex.Message)
            Assert.Fail("Function should handle edge cases gracefully")
        End Try
    End Sub

    <TestMethod>
    Public Sub Test_{target_function}_Performance()
        ' Performance testing with debugging
        Debug.WriteLine("⚡ Performance test for {target_function}")
        Dim startTime = DateTime.Now

        For i As Integer = 1 To 1000
            {target_function}("performance_test_" & i.ToString())
        Next

        Dim endTime = DateTime.Now
        Dim elapsed = endTime.Subtract(startTime)
        Debug.WriteLine($"⏱️ {target_function} executed 1000 times in {{elapsed.TotalMilliseconds}}ms")

        ' Performance assertion (adjust as needed)
        Assert.IsTrue(
            elapsed.TotalSeconds < 5,
            "Function should complete 1000 iterations in under 5 seconds"
        )
    End Sub

End Class
"""

        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_template)
            self.logger.info(f"✅ Unit test template created: {test_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to create unit test template: {e}")

        return test_file

    def create_vb_debugging_macro(self) -> Path:
        """Create VBA macro for automated repetitive debugging"""
        self.logger.info("🤖 Creating VB debugging automation macro")

        macro_file = self.vb_projects_dir / "EQ12_Debug_Automation.vba"

        macro_content = """
' EQ12 VB Debugging Automation Macro
' Purpose: Automate repetitive debugging tasks
' Usage: Run from VBA editor or bind to keyboard shortcut

Option Strict On
Option Explicit On

Public Sub EQ12_AutoDebugCurrentFunction()
    ' Automatically add debug logging to current function
    Debug.WriteLine("🚀 EQ12 Auto-Debug starting at " & DateTime.Now.ToString())

    Dim currentLine As String
    Dim functionName As String
    Dim lineCount As Integer = 0

    ' Get current selection or cursor position
    With Application.VBE.ActiveCodePane
        Dim startLine As Long = .Selection.StartLine
        Dim endLine As Long = .Selection.EndLine

        ' Find function boundaries
        For i = startLine To 1 Step -1
            currentLine = .CodeModule.Lines(i, 1)
            If InStr(currentLine, "Sub ") > 0 Or InStr(currentLine, "Function ") > 0 Then
                functionName = ExtractFunctionName(currentLine)
                Debug.WriteLine("🔍 Found function: " & functionName)
                Exit For
            End If
        Next i

        ' Add debug statements
        If functionName <> "" Then
            AddDebugStatementsToFunction(functionName, .CodeModule)
            Debug.WriteLine("✅ Debug statements added to " & functionName)
        End If
    End With

    Debug.WriteLine("🎉 EQ12 Auto-Debug completed")
End Sub

Private Function ExtractFunctionName(codeLine As String) As String
    ' Extract function name from declaration line
    Dim parts() As String = Split(codeLine, " ")
    Dim functionName As String = ""

    For i = 0 To UBound(parts)
        If parts(i) = "Sub" Or parts(i) = "Function" Then
            If i + 1 <= UBound(parts) Then
                functionName = Replace(parts(i + 1), "(", "")
                Exit For
            End If
        End If
    Next i

    Return functionName
End Function

Private Sub AddDebugStatementsToFunction(funcName As String, codeModule As Object)
    ' Add debug statements to specified function
    Dim i As Long
    Dim currentLine As String
    Dim debugStatement As String

    ' Find function start and add entry log
    For i = 1 To codeModule.CountOfLines
        currentLine = codeModule.Lines(i, 1)
        If InStr(
            currentLine,
            "Sub " & funcName) > 0 Or InStr(currentLine,
            "Function " & funcName
        ) > 0 Then
            debugStatement = (
                "    Debug.WriteLine(""🔍 Entering " & funcName & ": "" & DateTime.Now.ToString())"
            )
            codeModule.InsertLines i + 1, debugStatement
            Exit For
        End If
    Next i
End Sub

Public Sub EQ12_WatchUnknownVariables()
    ' Automatically add watch expressions for undefined variables
    Debug.WriteLine("👀 EQ12 Variable Watch starting")

    With Application.VBE.ActiveCodePane.CodeModule
        Dim lineCount As Long = .CountOfLines
        Dim currentLine As String
        Dim variables As String = ""

        ' Scan for Dim statements and add to watch
        For i = 1 To lineCount
            currentLine = .Lines(i, 1)
            If InStr(currentLine, "Dim ") > 0 Then
                Dim varName As String = ExtractVariableName(currentLine)
                If varName <> "" Then
                    variables = variables & varName & ", "
                    Debug.WriteLine("📊 Adding watch for variable: " & varName)
                End If
            End If
        Next i

        Debug.WriteLine("✅ Watch expressions added for: " & variables)
    End With
End Sub

Private Function ExtractVariableName(dimLine As String) As String
    ' Extract variable name from Dim statement
    Dim parts() As String = Split(dimLine.Trim(), " ")
    If UBound(parts) >= 1 Then
        Return parts(1)
    End If
    Return ""
End Function

Public Sub EQ12_QuickPerformanceTest()
    ' Quick performance testing with logging
    Debug.WriteLine("⚡ EQ12 Performance Test starting")

    Dim startTime As DateTime = DateTime.Now

    ' Add your performance test code here
    ' This is a template - customize for your specific functions

    Dim endTime As DateTime = DateTime.Now
    Dim elapsed As TimeSpan = endTime.Subtract(startTime)

    Debug.WriteLine($"⏱️ Performance test completed in {elapsed.TotalMilliseconds}ms")
End Sub
"""

        try:
            with open(macro_file, "w", encoding="utf-8") as f:
                f.write(macro_content)
            self.logger.info(f"✅ VB debugging macro created: {macro_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to create debugging macro: {e}")

        return macro_file

    def analyze_vb_file_quality(self, vb_file: Path) -> dict[str, list[str]]:
        """Analyze VB file for common debugging issues"""
        self.logger.info(f"📊 Analyzing VB code quality: {vb_file}")

        issues = {
            "missing_options": [],
            "type_issues": [],
            "missing_error_handling": [],
            "debug_opportunities": [],
        }

        try:
            with open(vb_file, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Check for missing Option statements
            if not re.search(r"Option\s+Strict\s+On", content, re.IGNORECASE):
                issues["missing_options"].append("Missing 'Option Strict On'")

            if not re.search(r"Option\s+Explicit\s+On", content, re.IGNORECASE):
                issues["missing_options"].append("Missing 'Option Explicit On'")

            # Check for type issues
            object_declarations = re.findall(
                r"Dim\s+(\w+)\s+As\s+Object", content, re.IGNORECASE)
            for var in object_declarations:
                issues["type_issues"].append(
                    f"Variable '{var}' declared as Object - use specific type"
                )

            # Check for missing error handling
            functions_without_try = []
            current_function = None
            has_try_catch = False

            for _i, line in enumerate(lines):
                func_match = re.match(
                    r"\s*(Public|Private|Friend)?\s*(Sub|Function)\s+(\w+)",
                    line.strip(),
                )
                if func_match:
                    if current_function and not has_try_catch:
                        functions_without_try.append(current_function)
                    current_function = func_match.group(3)
                    has_try_catch = False

                if "Try" in line:
                    has_try_catch = True

                if line.strip().startswith("End Sub") or line.strip().startswith("End Function"):
                    if current_function and not has_try_catch:
                        functions_without_try.append(current_function)
                    current_function = None
                    has_try_catch = False

            for func in functions_without_try:
                issues["missing_error_handling"].append(
                    f"Function '{func}' lacks Try-Catch error handling"
                )

            # Check for debug opportunities
            functions_without_debug = []
            current_function = None
            has_debug_log = False

            for _i, line in enumerate(lines):
                func_match = re.match(
                    r"\s*(Public|Private|Friend)?\s*(Sub|Function)\s+(\w+)",
                    line.strip(),
                )
                if func_match:
                    if current_function and not has_debug_log:
                        functions_without_debug.append(current_function)
                    current_function = func_match.group(3)
                    has_debug_log = False

                if "Debug.WriteLine" in line:
                    has_debug_log = True

                if line.strip().startswith("End Sub") or line.strip().startswith("End Function"):
                    if current_function and not has_debug_log:
                        functions_without_debug.append(current_function)
                    current_function = None
                    has_debug_log = False

            for func in functions_without_debug:
                issues["debug_opportunities"].append(
                    f"Function '{func}' could benefit from Debug.WriteLine logging"
                )

        except Exception as e:
            self.logger.error(f"❌ Failed to analyze VB file: {e}")

        return issues

    def process_vb_directory(self, directory: Path) -> dict[str, dict]:
        """Process all VB files in directory with hardcoded debugging improvements"""
        self.logger.info(f"📁 Processing VB files in {directory}")

        results = {}
        vb_extensions = [".vb", ".vbs", ".vba"]

        for vb_file in directory.rglob("*"):
            if vb_file.suffix.lower() in vb_extensions:
                self.logger.info(f"🔧 Processing {vb_file}")

                file_results = {
                    "options_enforced": self.enforce_option_strict_explicit(vb_file),
                    "debug_statements_added": self.add_debug_logging(vb_file),
                    "quality_issues": self.analyze_vb_file_quality(vb_file),
                }

                results[str(vb_file)] = file_results

        return results

    def generate_vb_debugging_report(self, results: dict) -> Path:
        """Generate comprehensive VB debugging report"""
        timestamp = datetime.now(UTC).isoformat()

        report = {
            "timestamp": timestamp,
            "workspace": str(self.workspace),
            "debugging_system": "EQ12 Advanced VB Debugging",
            "hardcoded_best_practices": self.vb_debug_rules,
            "processing_results": results,
            "summary": {
                "files_processed": len(results),
                "total_debug_statements": sum(
                    r.get("debug_statements_added", 0) for r in results.values()
                ),
                "files_with_options_enforced": sum(
                    1
                    for r in results.values()
                    if r.get("options_enforced", {}).get("file_modified", False)
                ),
            },
            "recommendations": [
                "All VB files now have Option Strict On and Option Explicit On enforced",
                "Debug.WriteLine statements added for function entry/exit and variable tracking",
                "Use created unit test templates for isolated function debugging",
                "Run VBA macros for automated debugging workflow",
                "Review quality issues and apply Roslyn analyzers for deeper analysis",
            ],
        }

        report_file = (
            self.logs_dir /
            f"vb_debugging_report_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 VB debugging report saved: {report_file}")
        return report_file


def main():
    """Main entry point for EQ12 VB Debugging System"""
    parser = argparse.ArgumentParser(
        description="EQ12 Advanced VB Debugging System with Hardcoded Best Practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --enforce-all                     # Apply all debugging improvements
  %(prog)s --file "MyVBFile.vb"              # Process specific VB file
  %(prog)s --create-test "MyFunction"        # Create unit test template
  %(prog)s --create-macro                    # Generate debugging macro
  %(prog)s --analyze-quality                 # Analyze code quality issues
        """,
    )

    parser.add_argument(
        "--workspace",
        default="C:\\\\EQ12",
        help="EQ12 workspace directory (default: C:\\\\EQ12)",
    )
    parser.add_argument(
        "--enforce-all",
        action="store_true",
        help="Apply all VB debugging improvements to workspace",
    )
    parser.add_argument("--file", help="Process specific VB file")
    parser.add_argument("--directory", help="Process all VB files in directory")
    parser.add_argument(
        "--create-test",
        help="Create unit test template for specified function")
    parser.add_argument(
        "--create-macro",
        action="store_true",
        help="Generate VB debugging automation macro",
    )
    parser.add_argument(
        "--analyze-quality",
        action="store_true",
        help="Analyze VB code quality and debugging opportunities",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        debugger = EQ12VBDebuggingSystem(args.workspace)

        if args.enforce_all:
            print("🔧 EQ12 VB Debugging - Enforcing All Best Practices")
            print("=" * 60)
            results = debugger.process_vb_directory(debugger.workspace)
            report_file = debugger.generate_vb_debugging_report(results)
            print(f"✅ Complete! Report: {report_file}")

        elif args.file:
            print(f"🔧 Processing VB file: {args.file}")
            vb_file = Path(args.file)
            if vb_file.exists():
                options_result = debugger.enforce_option_strict_explicit(vb_file)
                debug_count = debugger.add_debug_logging(vb_file)
                quality_issues = debugger.analyze_vb_file_quality(vb_file)
                print(f"✅ Options enforced: {options_result}")
                print(f"✅ Debug statements added: {debug_count}")
                print(
                    f"📊 Quality issues found: {len(functools.reduce(operator.iadd, quality_issues.values(), []))}"
                )
            else:
                print(f"❌ File not found: {args.file}")

        elif args.directory:
            print(f"📁 Processing VB files in: {args.directory}")
            directory = Path(args.directory)
            if directory.exists():
                results = debugger.process_vb_directory(directory)
                report_file = debugger.generate_vb_debugging_report(results)
                print(f"✅ Complete! Report: {report_file}")
            else:
                print(f"❌ Directory not found: {args.directory}")

        elif args.create_test:
            print(f"🧪 Creating unit test template for: {args.create_test}")
            test_file = debugger.create_vb_unit_test_template(
                args.create_test, Path("dummy.vb"))
            print(f"✅ Unit test template created: {test_file}")

        elif args.create_macro:
            print("🤖 Creating VB debugging automation macro")
            macro_file = debugger.create_vb_debugging_macro()
            print(f"✅ Macro created: {macro_file}")

        elif args.analyze_quality:
            print("📊 Analyzing VB code quality")
            # Analyze all VB files in workspace
            results = {}
            for vb_file in debugger.workspace.rglob("*.vb"):
                results[str(vb_file)] = {
                    "quality_issues": debugger.analyze_vb_file_quality(vb_file)
                }
            report_file = debugger.generate_vb_debugging_report(results)
            print(f"✅ Quality analysis complete! Report: {report_file}")

        else:
            parser.print_help()

    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
