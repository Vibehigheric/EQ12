''' <summary>
''' EQ12 Log Inspector - Scan logs for errors, Pylance crashes, UTF-8 issues
''' ASCII dashboard output
''' </summary>
Imports System
Imports System.IO
Imports System.Text
Imports System.Text.RegularExpressions
Imports System.Collections.Generic

Namespace EQ12.Diagnostics

    Public Class LogAnalysisResult
        Public Property TotalFiles As Integer
        Public Property TotalErrors As Integer
        Public Property ErrorsByType As Dictionary(Of String, Integer)
        Public Property ProblematicFiles As List(Of String)

        Public Sub New()
            ErrorsByType = New Dictionary(Of String, Integer)()
            ProblematicFiles = New List(Of String)()
        End Sub
    End Class

    Module Eq12LogInspector

        Sub Main(args As String())
            Dim logDir As String = If(args.Length > 0, args(0), "C:\EQ12\logs")

            Console.OutputEncoding = Encoding.ASCII

            If Not Directory.Exists(logDir) Then
                Console.WriteLine("=== EQ12 LOG INSPECTOR ===")
                Console.WriteLine("Directory does not exist: " & logDir)
                Return
            End If

            Dim result = ScanLogs(logDir)

            PrintDashboard(result)
        End Sub

        Private Function ScanLogs(logDir As String) As LogAnalysisResult
            Dim result As New LogAnalysisResult()

            Dim errorPatterns As New Dictionary(Of String, String) From {
                {"ParserError", "ParserError"},
                {"UnexpectedToken", "Unexpected token"},
                {"MissingBrace", "Missing closing '}'"},
                {"PylanceError", "Pylance: connection to server is erroring"},
                {"EPIPE", "write EPIPE"},
                {"ChannelClosed", "channel closed"},
                {"EncodingIssue", "UTF-8"},
                {"UnicodeError", "UnicodeDecodeError"},
                {"AsciiError", "ascii"},
                {"InfiniteLoop", "InfiniteLoopException"}
            }

            For Each key In errorPatterns.Keys
                result.ErrorsByType(key) = 0
            Next

            Dim files = Directory.GetFiles(logDir, "*.log", SearchOption.AllDirectories)
            result.TotalFiles = files.Length

            For Each file In files
                Try
                    Dim content As String = File.ReadAllText(file, Encoding.UTF8)
                    Dim fileHasErrors As Boolean = False

                    For Each kvp In errorPatterns
                        Dim pattern = kvp.Value
                        Dim count As Integer = Regex.Matches(content, Regex.Escape(pattern), RegexOptions.IgnoreCase).Count

                        If count > 0 Then
                            result.ErrorsByType(kvp.Key) += count
                            result.TotalErrors += count
                            fileHasErrors = True
                        End If
                    Next

                    If fileHasErrors Then
                        result.ProblematicFiles.Add(file)
                    End If

                Catch ex As Exception
                    Console.WriteLine("Error reading file: " & file)
                End Try
            Next

            Return result
        End Function

        Private Sub PrintDashboard(result As LogAnalysisResult)
            Console.WriteLine("================================================================")
            Console.WriteLine("           EQ12 LOG INSPECTOR - DIAGNOSTIC REPORT")
            Console.WriteLine("================================================================")
            Console.WriteLine()
            Console.WriteLine("Scanned Files: " & result.TotalFiles)
            Console.WriteLine("Total Errors: " & result.TotalErrors)
            Console.WriteLine("Problematic Files: " & result.ProblematicFiles.Count)
            Console.WriteLine()
            Console.WriteLine("=== ERROR BREAKDOWN ===")

            For Each kvp In result.ErrorsByType.OrderByDescending(Function(x) x.Value)
                If kvp.Value > 0 Then
                    Dim bar = New String("*"c, Math.Min(kvp.Value, 50))
                    Console.WriteLine($"  {kvp.Key,-20} : {kvp.Value,5} {bar}")
                End If
            Next

            If result.ProblematicFiles.Count > 0 Then
                Console.WriteLine()
                Console.WriteLine("=== PROBLEMATIC FILES ===")
                Dim topFiles = result.ProblematicFiles.Take(10)
                For Each file In topFiles
                    Console.WriteLine("  - " & file)
                Next

                If result.ProblematicFiles.Count > 10 Then
                    Console.WriteLine($"  ... and {result.ProblematicFiles.Count - 10} more")
                End If
            End If

            Console.WriteLine()
            Console.WriteLine("================================================================")
        End Sub

    End Module

End Namespace
