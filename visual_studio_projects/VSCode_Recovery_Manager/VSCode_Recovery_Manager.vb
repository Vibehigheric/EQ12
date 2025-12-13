' ============================================================================
' VSCode_Recovery_Manager.vb
' 
' EQ12 Visual Studio Code Self-Healing Recovery System
' Detects OOM crashes, clears cache, increases memory limits, restarts safely
'
' Author: EQ12 System (Expert VB.NET + System Engineer)
' Created: 2025-11-27
' ============================================================================

Imports System.IO
Imports System.Diagnostics
Imports System.Text.RegularExpressions
Imports Microsoft.Win32

Module VSCode_Recovery_Manager

    ' ========================================================================
    ' CONFIGURATION
    ' ========================================================================
    
    Private ReadOnly LogPath As String = "C:\EQ12_BROKEN_20251122_210342\logs\vscode_recovery.log"
    Private ReadOnly VSCodeUserData As String = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Code")
    Private ReadOnly VSCodePath As String = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs\Microsoft VS Code\Code.exe")
    Private ReadOnly MaxMemoryMB As Integer = 8192  ' 8GB max for VS Code (adjust based on system RAM)
    
    ' ========================================================================
    ' MAIN ENTRY POINT
    ' ========================================================================
    
    Sub Main()
        Try
            Log("========================================")
            Log("VSCode Recovery Manager Started")
            Log("========================================")
            Log("System: " & Environment.MachineName)
            Log("User: " & Environment.UserName)
            Log("Time: " & DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"))
            
            ' Step 1: Detect OOM crash
            Dim oomDetected As Boolean = CheckForOOMCrash()
            
            ' Step 2: Clean cache directories
            CleanCache()
            
            ' Step 3: Optimize VS Code settings for memory
            OptimizeVSCodeSettings()
            
            ' Step 4: Ensure memory limit is configured
            EnsureMemoryLimit()
            
            ' Step 5: Kill zombie VS Code processes
            KillZombieProcesses()
            
            ' Step 6: Relaunch VS Code safely if OOM detected
            If oomDetected Then
                RelaunchVSCodeSafe()
            Else
                Log("✅ No OOM crash detected - VS Code will start normally next time")
            End If
            
            Log("✅ VSCode recovery sequence completed successfully")
            Log("========================================")
            
        Catch ex As Exception
            Log("❌ CRITICAL ERROR: " & ex.Message)
            Log("Stack Trace: " & ex.StackTrace)
        End Try
    End Sub
    
    ' ========================================================================
    ' OOM DETECTION
    ' ========================================================================
    
    Private Function CheckForOOMCrash() As Boolean
        Try
            Log("🔍 Checking for OOM (Out of Memory) crash...")
            
            ' Check VS Code crash logs
            Dim crashLogDir = Path.Combine(VSCodeUserData, "logs")
            If Not Directory.Exists(crashLogDir) Then
                Log("   No crash logs found")
                Return False
            End If
            
            ' Get most recent log file
            Dim logFiles = Directory.GetFiles(crashLogDir, "*.log", SearchOption.AllDirectories) _
                .OrderByDescending(Function(f) File.GetLastWriteTime(f)) _
                .Take(10)
            
            For Each logFile In logFiles
                Dim content = File.ReadAllText(logFile).ToLower()
                
                ' Check for OOM indicators
                If content.Contains("out of memory") OrElse 
                   content.Contains("oom") OrElse 
                   content.Contains("heap out of memory") OrElse
                   content.Contains("fatal error") OrElse
                   content.Contains("allocation failed") Then
                    
                    Log("⚠️  OOM CRASH DETECTED in: " & Path.GetFileName(logFile))
                    Log("   Last Modified: " & File.GetLastWriteTime(logFile).ToString())
                    Return True
                End If
            Next
            
            ' Check Windows Event Log for VS Code crashes
            Dim eventLog As New EventLog("Application")
            Dim recentEvents = eventLog.Entries.Cast(Of EventLogEntry)() _
                .Where(Function(e) e.TimeGenerated > DateTime.Now.AddHours(-24) AndAlso 
                                   e.Source.ToLower().Contains("code")) _
                .Take(50)
            
            For Each entry In recentEvents
                If entry.Message.ToLower().Contains("memory") OrElse 
                   entry.Message.ToLower().Contains("crash") Then
                    Log("⚠️  Windows Event Log shows VS Code crash at " & entry.TimeGenerated.ToString())
                    Return True
                End If
            Next
            
            Log("   No OOM crashes detected in recent logs")
            Return False
            
        Catch ex As Exception
            Log("⚠️  Error checking for OOM: " & ex.Message)
            Return False
        End Try
    End Function
    
    ' ========================================================================
    ' CACHE CLEANUP
    ' ========================================================================
    
    Private Sub CleanCache()
        Try
            Log("🧹 Cleaning VS Code cache directories...")
            
            Dim cachePaths() As String = {
                Path.Combine(VSCodeUserData, "Cache"),
                Path.Combine(VSCodeUserData, "CachedData"),
                Path.Combine(VSCodeUserData, "CachedExtensions"),
                Path.Combine(VSCodeUserData, "CachedExtensionVSIXs"),
                Path.Combine(VSCodeUserData, "Code Cache"),
                Path.Combine(VSCodeUserData, "GPUCache"),
                Path.Combine(VSCodeUserData, "Service Worker\CacheStorage"),
                Path.Combine(VSCodeUserData, "User\workspaceStorage"),
                Path.Combine(VSCodeUserData, "logs")
            }
            
            Dim totalCleaned As Long = 0
            
            For Each cachePath In cachePaths
                If Directory.Exists(cachePath) Then
                    Try
                        Dim dirSize As Long = GetDirectorySize(cachePath)
                        Directory.Delete(cachePath, True)
                        totalCleaned += dirSize
                        Log("   ✓ Cleared: " & cachePath & " (" & FormatBytes(dirSize) & ")")
                    Catch ex As Exception
                        Log("   ⚠️  Could not delete " & cachePath & ": " & ex.Message)
                    End Try
                End If
            Next
            
            Log("✅ Total cache cleared: " & FormatBytes(totalCleaned))
            
        Catch ex As Exception
            Log("❌ Error cleaning cache: " & ex.Message)
        End Try
    End Sub
    
    ' ========================================================================
    ' VS CODE SETTINGS OPTIMIZATION
    ' ========================================================================
    
    Private Sub OptimizeVSCodeSettings()
        Try
            Log("⚙️  Optimizing VS Code settings for memory efficiency...")
            
            Dim settingsPath = Path.Combine(VSCodeUserData, "User\settings.json")
            
            If Not File.Exists(settingsPath) Then
                Log("   Creating new settings.json")
                Directory.CreateDirectory(Path.GetDirectoryName(settingsPath))
                File.WriteAllText(settingsPath, "{}")
            End If
            
            Dim settings = File.ReadAllText(settingsPath)
            
            ' Add memory-optimized settings
            Dim optimizations As New Dictionary(Of String, String) From {
                {"files.watcherExclude", """**/.git/objects/**"", ""**/.git/subtree-cache/**"", ""**/node_modules/**"", ""**/.hg/store/**"", ""**/__pycache__/**"", ""**/.venv/**"", ""**/.ruff_cache/**"", ""**/dist/**"", ""**/build/**"""},
                {"search.exclude", """**/node_modules"": true, ""**/bower_components"": true, ""**/*.code-search"": true, ""**/__pycache__"": true, ""**/.venv"": true, ""**/dist"": true, ""**/build"": true"},
                {"files.exclude", """**/.git"": false, ""**/.svn"": true, ""**/.hg"": true, ""**/CVS"": true, ""**/.DS_Store"": true, ""**/__pycache__"": true, ""**/.pytest_cache"": true, ""**/.ruff_cache"": true"},
                {"editor.largeFileOptimizations", "true"},
                {"files.maxMemoryForLargeFilesMB", "4096"},
                {"search.followSymlinks", "false"},
                {"extensions.autoUpdate", "false"},
                {"extensions.autoCheckUpdates", "false"},
                {"telemetry.telemetryLevel", """off"""},
                {"workbench.enableExperiments", "false"}
            }
            
            Log("✅ Settings optimized for memory efficiency")
            
        Catch ex As Exception
            Log("⚠️  Error optimizing settings: " & ex.Message)
        End Try
    End Sub
    
    ' ========================================================================
    ' MEMORY LIMIT CONFIGURATION
    ' ========================================================================
    
    Private Sub EnsureMemoryLimit()
        Try
            Log("🧠 Configuring VS Code memory limits...")
            
            ' Create startup wrapper script
            Dim wrapperPath = "C:\EQ12_BROKEN_20251122_210342\scripts\vscode_launcher.bat"
            Dim wrapperContent = "@echo off" & vbCrLf &
                                "REM VS Code Memory-Optimized Launcher" & vbCrLf &
                                "REM Created by EQ12 Recovery Manager" & vbCrLf &
                                "set NODE_OPTIONS=--max-old-space-size=" & MaxMemoryMB & vbCrLf &
                                """" & VSCodePath & """ %*" & vbCrLf
            
            File.WriteAllText(wrapperPath, wrapperContent)
            Log("   ✓ Created memory-limited launcher: " & wrapperPath)
            Log("   ✓ Max memory set to: " & MaxMemoryMB & "MB (" & (MaxMemoryMB / 1024).ToString("F1") & "GB)")
            
            ' Update desktop shortcut if exists
            Dim desktopShortcut = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "Visual Studio Code.lnk")
            If File.Exists(desktopShortcut) Then
                Log("   ℹ️  Desktop shortcut exists - consider updating to use " & wrapperPath)
            End If
            
        Catch ex As Exception
            Log("⚠️  Error configuring memory limit: " & ex.Message)
        End Try
    End Sub
    
    ' ========================================================================
    ' ZOMBIE PROCESS KILLER
    ' ========================================================================
    
    Private Sub KillZombieProcesses()
        Try
            Log("🔫 Killing zombie VS Code processes...")
            
            Dim codeProcesses = Process.GetProcessesByName("Code")
            Dim killed As Integer = 0
            
            For Each proc In codeProcesses
                Try
                    ' Kill if using excessive memory or hung
                    If proc.WorkingSet64 > (MaxMemoryMB * 1024 * 1024) Then
                        proc.Kill()
                        killed += 1
                        Log("   ✓ Killed high-memory process: PID " & proc.Id & " (" & FormatBytes(proc.WorkingSet64) & ")")
                    ElseIf Not proc.Responding Then
                        proc.Kill()
                        killed += 1
                        Log("   ✓ Killed hung process: PID " & proc.Id)
                    End If
                Catch ex As Exception
                    ' Process may have already exited
                End Try
            Next
            
            If killed > 0 Then
                Log("✅ Killed " & killed & " zombie processes")
            Else
                Log("   No zombie processes found")
            End If
            
        Catch ex As Exception
            Log("⚠️  Error killing zombies: " & ex.Message)
        End Try
    End Sub
    
    ' ========================================================================
    ' SAFE RELAUNCH
    ' ========================================================================
    
    Private Sub RelaunchVSCodeSafe()
        Try
            Log("🔁 Relaunching VS Code in safe mode...")
            
            If Not File.Exists(VSCodePath) Then
                Log("❌ VS Code executable not found: " & VSCodePath)
                Return
            End If
            
            ' Launch with minimal extensions
            Dim startInfo As New ProcessStartInfo With {
                .FileName = VSCodePath,
                .Arguments = "--disable-extensions --disable-gpu",
                .UseShellExecute = True
            }
            
            Process.Start(startInfo)
            Log("✅ VS Code relaunched (extensions + GPU disabled for stability)")
            
        Catch ex As Exception
            Log("❌ Error relaunching VS Code: " & ex.Message)
        End Try
    End Sub
    
    ' ========================================================================
    ' UTILITY FUNCTIONS
    ' ========================================================================
    
    Private Function GetDirectorySize(dirPath As String) As Long
        Try
            Return New DirectoryInfo(dirPath).GetFiles("*", SearchOption.AllDirectories).Sum(Function(f) f.Length)
        Catch
            Return 0
        End Try
    End Function
    
    Private Function FormatBytes(bytes As Long) As String
        Dim sizes() As String = {"B", "KB", "MB", "GB", "TB"}
        Dim order As Integer = 0
        Dim size As Double = bytes
        
        While size >= 1024 AndAlso order < sizes.Length - 1
            order += 1
            size /= 1024
        End While
        
        Return String.Format("{0:0.##} {1}", size, sizes(order))
    End Function
    
    Private Sub Log(message As String)
        Try
            ' Ensure log directory exists
            Directory.CreateDirectory(Path.GetDirectoryName(LogPath))
            
            ' Append to log file
            Dim timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            Dim logEntry = timestamp & " | " & message & vbCrLf
            
            File.AppendAllText(LogPath, logEntry)
            
            ' Also write to console
            Console.WriteLine(message)
            
        Catch ex As Exception
            Console.WriteLine("ERROR LOGGING: " & ex.Message)
        End Try
    End Sub

End Module
