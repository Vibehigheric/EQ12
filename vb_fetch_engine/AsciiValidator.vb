''' <summary>
''' EQ12 ASCII/Encoding Validator
''' Scans all scripts for non-ASCII characters, generates report
''' </summary>
Imports System
Imports System.IO
Imports System.Text
Imports System.Collections.Generic

Namespace EQ12.Diagnostics

    Public Class EncodingIssue
        Public Property FilePath As String
        Public Property LineNumber As Integer
        Public Property Character As Char
        Public Property CharCode As Integer
        Public Property Context As String
    End Class

    Module Eq12AsciiValidator

        Sub Main(args As String())
            Console.OutputEncoding = Encoding.ASCII

            Dim root As String = If(args.Length > 0, args(0), "C:\EQ12")

            Console.WriteLine("=== EQ12 ASCII VALIDATOR ===")
            Console.WriteLine("Scanning: " & root)
            Console.WriteLine(New String("="c, 60))
            Console.WriteLine()

            Dim issues = ScanForNonAscii(root)

            PrintReport(issues)
        End Sub

        Private Function ScanForNonAscii(root As String) As List(Of EncodingIssue)
            Dim issues As New List(Of EncodingIssue)()

            If Not Directory.Exists(root) Then
                Console.WriteLine("Directory not found: " & root)
                Return issues
            End If

            Dim exts = {".ps1", ".py", ".json", ".txt", ".md", ".vb", ".cs"}
            Dim files = Directory.GetFiles(root, "*.*", SearchOption.AllDirectories)

            For Each file In files
                If Not exts.Contains(Path.GetExtension(file).ToLowerInvariant()) Then
                    Continue For
                End If

                ' Skip certain directories
                If file.Contains("__pycache__") OrElse
                   file.Contains("node_modules") OrElse
                   file.Contains(".git") Then
                    Continue For
                End If

                Try
                    Dim lines = File.ReadAllLines(file, Encoding.UTF8)

                    For lineNum = 0 To lines.Length - 1
                        Dim line = lines(lineNum)

                        For charIdx = 0 To line.Length - 1
                            Dim ch = line(charIdx)
                            Dim code = AscW(ch)

                            If code > 127 Then
                                Dim issue As New EncodingIssue() With {
                                    .FilePath = file,
                                    .LineNumber = lineNum + 1,
                                    .Character = ch,
                                    .CharCode = code,
                                    .Context = GetContext(line, charIdx)
                                }
                                issues.Add(issue)
                            End If
                        Next
                    Next

                Catch ex As Exception
                    Console.WriteLine("Error reading: " & file)
                End Try
            Next

            Return issues
        End Function

        Private Function GetContext(line As String, charIdx As Integer) As String
            Dim start = Math.Max(0, charIdx - 10)
            Dim length = Math.Min(21, line.Length - start)

            If start + length > line.Length Then
                length = line.Length - start
            End If

            Dim context = line.Substring(start, length)
            Return context.Replace(vbTab, " ").Trim()
        End Function

        Private Sub PrintReport(issues As List(Of EncodingIssue))
            If issues.Count = 0 Then
                Console.WriteLine("SUCCESS: No non-ASCII characters detected.")
                Console.WriteLine("All scripts are ASCII-safe.")
                Return
            End If

            Console.WriteLine($"FOUND {issues.Count} non-ASCII characters:")
            Console.WriteLine()

            Dim groupedByFile = issues.GroupBy(Function(i) i.FilePath)

            For Each fileGroup In groupedByFile.Take(20)
                Console.WriteLine("File: " & fileGroup.Key)

                For Each issue In fileGroup.Take(5)
                    Console.WriteLine($"  Line {issue.LineNumber}: Char '{issue.Character}' (code {issue.CharCode})")
                    Console.WriteLine($"    Context: ...{issue.Context}...")
                Next

                If fileGroup.Count() > 5 Then
                    Console.WriteLine($"  ... and {fileGroup.Count() - 5} more issues in this file")
                End If

                Console.WriteLine()
            Next

            If groupedByFile.Count() > 20 Then
                Console.WriteLine($"... and {groupedByFile.Count() - 20} more files with issues")
            End If

            Console.WriteLine()
            Console.WriteLine("=== SUMMARY ===")
            Console.WriteLine($"Files with issues: {groupedByFile.Count()}")
            Console.WriteLine($"Total non-ASCII characters: {issues.Count}")
            Console.WriteLine()
            Console.WriteLine("ACTION REQUIRED: Clean these files to prevent corruption.")
        End Sub

    End Module

End Namespace
