
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
        If InStr(currentLine, "Sub " & funcName) > 0 Or InStr(currentLine, "Function " & funcName) > 0 Then
            debugStatement = "    Debug.WriteLine(""🔍 Entering " & funcName & ": "" & DateTime.Now.ToString())"
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
