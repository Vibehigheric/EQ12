#!/usr/bin/env python3
"""
EQ12 VB.NET Copilot Integration & Expert Programming Assistant
Advanced Visual Basic .NET utilities with GitHub Copilot optimization

Features:
- VB.NET code generation and optimization
- Windows Forms designer patterns
- Installer creation utilities
- Command-line tool builders
- Legacy code modernization
- Expert programming prompts for Copilot
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/vbnet_copilot_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VBNetProjectType(Enum):
    """VB.NET project types"""
    CONSOLE_APP = "Console Application"
    WINDOWS_FORMS = "Windows Forms App"
    WPF_APP = "WPF Application"
    CLASS_LIBRARY = "Class Library"
    INSTALLER = "Setup Project"
    SERVICE = "Windows Service"


class CopilotPromptCategory(Enum):
    """Categories for Copilot prompts"""
    CODE_GENERATION = auto()
    REFACTORING = auto()
    DEBUGGING = auto()
    OPTIMIZATION = auto()
    MODERNIZATION = auto()


@dataclass
class VBNetProject:
    """VB.NET project configuration"""
    name: str
    project_type: VBNetProjectType
    target_framework: str = "net6.0-windows"
    output_path: Path = None
    dependencies: List[str] = None
    copilot_prompts: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.copilot_prompts is None:
            self.copilot_prompts = []
        if self.output_path is None:
            self.output_path = Path("C:/EQ12/vbnet_projects") / self.name


class EQ12VBNetCopilotAssistant:
    """Advanced VB.NET development assistant with Copilot integration"""

    def __init__(self, eq12_root: Path = Path("C:/EQ12")):
        self.eq12_root = eq12_root
        self.vbnet_templates = {}
        self.copilot_prompts = {}
        self._initialize_templates()
        self._initialize_copilot_prompts()

    def _initialize_templates(self):
        """Initialize VB.NET code templates"""
        self.vbnet_templates = {
            VBNetProjectType.CONSOLE_APP: self._get_console_template(),
            VBNetProjectType.WINDOWS_FORMS: self._get_winforms_template(),
            VBNetProjectType.WPF_APP: self._get_wpf_template(),
            VBNetProjectType.CLASS_LIBRARY: self._get_library_template(),
            VBNetProjectType.INSTALLER: self._get_installer_template(),
            VBNetProjectType.SERVICE: self._get_service_template()
        }

    def _initialize_copilot_prompts(self):
        """Initialize expert Copilot prompts for VB.NET"""
        self.copilot_prompts = {
            CopilotPromptCategory.CODE_GENERATION: [
                "Create a robust VB.NET class with proper error handling, " +
                "XML documentation, and modern .NET practices",

                "Generate a Windows Forms application with MVVM pattern, " +
                "data binding, and responsive UI design",

                "Build a VB.NET installer with custom actions, registry " +
                "modifications, and proper uninstall procedures",

                "Create a VB.NET command-line tool with argument parsing, " +
                "logging, and cross-platform compatibility"
            ],

            CopilotPromptCategory.REFACTORING: [
                "Refactor this VB.NET code to use modern async/await " +
                "patterns with proper exception handling",

                "Convert this legacy VB.NET Windows Forms code to use " +
                "dependency injection and SOLID principles",

                "Modernize this VB6 code to VB.NET with current best " +
                "practices and design patterns"
            ],

            CopilotPromptCategory.OPTIMIZATION: [
                "Optimize this VB.NET code for performance using LINQ, " +
                "parallel processing, and memory-efficient patterns",

                "Improve this VB.NET Windows Forms application startup " +
                "time and responsiveness using lazy loading"
            ],

            CopilotPromptCategory.DEBUGGING: [
                "Add comprehensive logging and error handling to this " +
                "VB.NET application with NLog integration",

                "Create unit tests for this VB.NET class using MSTest " +
                "with proper mocking and assertions"
            ]
        }

    def _get_console_template(self) -> str:
        """Get console application template"""
        return '''Imports System
Imports System.Threading.Tasks
Imports System.CommandLine
Imports Microsoft.Extensions.Logging
# VB.NET code commented out for Python compatibility:
# Imports Microsoft.Extensions.DependencyInjection
# Imports Microsoft.Extensions.Hosting

# ''' <summary>
# ''' EQ12 VB.NET Console Application
# ''' Expert-level implementation with modern .NET practices
# ''' </summary>
# Module Program
    Private _logger As ILogger(Of Object)

    ''' <summary>
    ''' Application entry point with dependency injection
    ''' </summary>
    Sub Main(args As String())
        Try
            CreateHostBuilder(args).Build().Run()
        Catch ex As Exception
            Console.WriteLine($"Fatal error: {ex.Message}")
            Environment.Exit(1)
        End Try
    End Sub

    ''' <summary>
    ''' Configure host builder with services
    ''' </summary>
    Function CreateHostBuilder(args As String()) As IHostBuilder
        Return Host.CreateDefaultBuilder(args) _
            .ConfigureServices(Sub(context, services)
                services.AddLogging()
                services.AddSingleton(Of IApplicationService, ApplicationService)()
            End Sub)
    End Function
End Module

''' <summary>
''' Main application service with expert patterns
''' </summary>
Public Class ApplicationService
    Implements IApplicationService

    Private ReadOnly _logger As ILogger(Of ApplicationService)

    Public Sub New(logger As ILogger(Of ApplicationService))
        _logger = logger ?? throw New ArgumentNullException(NameOf(logger))
    End Sub

    ''' <summary>
    ''' Execute main application logic asynchronously
    ''' </summary>
    Public Async Function ExecuteAsync(cancellationToken As CancellationToken) As Task _
        Implements IApplicationService.ExecuteAsync

        Try
            _logger.LogInformation("Starting EQ12 VB.NET application...")

            ' TODO: Implement your application logic here
            ' Use modern async/await patterns
            ' Implement proper error handling
            ' Add comprehensive logging

            Await Task.Delay(1000, cancellationToken)
            _logger.LogInformation("Application completed successfully")

        Catch ex As OperationCanceledException
            _logger.LogWarning("Application was cancelled")
            Throw
        Catch ex As Exception
            _logger.LogError(ex, "Application failed with error: {Message}", ex.Message)
            Throw
        End Try
    End Function
End Class

Public Interface IApplicationService
    Function ExecuteAsync(cancellationToken As CancellationToken) As Task
End Interface'''

    def _get_winforms_template(self) -> str:
        """Get Windows Forms template with modern patterns"""
        return """Imports System
Imports System.ComponentModel
Imports System.Threading.Tasks
Imports System.Windows.Forms
Imports Microsoft.Extensions.DependencyInjection
Imports Microsoft.Extensions.Logging

""" <summary>
''' EQ12 VB.NET Windows Forms Application
''' Modern MVVM-inspired architecture with dependency injection
''' </summary>
<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Public Partial Class MainForm
    Inherits Form

    Private ReadOnly _logger As ILogger(Of MainForm)
    Private ReadOnly _viewModel As IMainViewModel
    Private components As IContainer

    ''' <summary>
    ''' Initialize form with dependency injection
    ''' </summary>
    Public Sub New(logger As ILogger(Of MainForm), viewModel As IMainViewModel)
        _logger = logger ?? throw New ArgumentNullException(NameOf(logger))
        _viewModel = viewModel ?? throw New ArgumentNullException(NameOf(viewModel))

        InitializeComponent()
        InitializeDataBinding()

        _logger.LogInformation("MainForm initialized successfully")
    End Sub

    ''' <summary>
    ''' Initialize UI components with modern design
    ''' </summary>
    Private Sub InitializeComponent()
        Me.components = New Container()

        ' Configure form properties
        Me.AutoScaleDimensions = New SizeF(8.0F, 16.0F)
        Me.AutoScaleMode = AutoScaleMode.Font
        Me.ClientSize = New Size(800, 600)
        Me.Text = "EQ12 VB.NET Windows Forms App"
        Me.StartPosition = FormStartPosition.CenterScreen

        ' Add modern styling
        Me.BackColor = Color.FromArgb(240, 240, 240)
        Me.Font = New Font("Segoe UI", 9.0F, FontStyle.Regular)

        ' TODO: Add your controls here
        ' Use modern UI patterns
        ' Implement responsive design
        ' Add proper accessibility support
    End Sub

    ''' <summary>
    ''' Setup data binding with view model
    ''' </summary>
    Private Sub InitializeDataBinding()
        Try
            ' TODO: Implement data binding
            ' Use INotifyPropertyChanged for reactive UI
            ' Implement command patterns for actions

            _logger.LogDebug("Data binding initialized")
        Catch ex As Exception
            _logger.LogError(ex, "Failed to initialize data binding")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Handle form load with async initialization
    ''' </summary>
    Private Async Sub MainForm_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Try
            Me.UseWaitCursor = True
            Await _viewModel.InitializeAsync()

            _logger.LogInformation("Form loaded and initialized")
        Catch ex As Exception
            _logger.LogError(ex, "Form initialization failed")
            MessageBox.Show($"Initialization failed: {ex.Message}",
                           "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        Finally
            Me.UseWaitCursor = False
        End Try
    End Sub

    ''' <summary>
    ''' Clean up resources
    ''' </summary>
    Protected Overrides Sub Dispose(disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub
End Class

''' <summary>
''' View model interface for MVVM pattern
''' </summary>
Public Interface IMainViewModel
    Function InitializeAsync() As Task
    Event PropertyChanged As PropertyChangedEventHandler
End Interface

''' <summary>
''' Main view model implementation
''' </summary>
Public Class MainViewModel
    Implements IMainViewModel, INotifyPropertyChanged

    Private ReadOnly _logger As ILogger(Of MainViewModel)

    Public Sub New(logger As ILogger(Of MainViewModel))
        _logger = logger ?? throw New ArgumentNullException(NameOf(logger))
    End Sub

    Public Async Function InitializeAsync() As Task Implements IMainViewModel.InitializeAsync
        Try
            _logger.LogInformation("Initializing view model...")

            ' TODO: Initialize your data and services
            ' Use async patterns for data loading
            ' Implement proper error handling

            Await Task.Delay(500) ' Simulate async initialization

            _logger.LogInformation("View model initialized successfully")
        Catch ex As Exception
            _logger.LogError(ex, "View model initialization failed")
            Throw
        End Try
    End Function

    Public Event PropertyChanged As PropertyChangedEventHandler _
        Implements INotifyPropertyChanged.PropertyChanged

    Protected Sub OnPropertyChanged(<CallerMemberName> propertyName As String = "")
        RaiseEvent PropertyChanged(Me, New PropertyChangedEventArgs(propertyName))
    End Sub
End Class'''

    def _get_wpf_template(self) -> str:
        """Get WPF application template"""
        return '''Imports System
Imports System.Windows
Imports System.Windows.Controls
Imports Microsoft.Extensions.DependencyInjection
Imports Microsoft.Extensions.Hosting
Imports Microsoft.Extensions.Logging

''' <summary>
''' EQ12 VB.NET WPF Application
''' Modern MVVM architecture with dependency injection
''' </summary>
Class Application
    Private Shared _host As IHost

    ''' <summary>
    ''' Application startup with dependency injection
    ''' </summary>
    Private Sub Application_Startup(sender As Object, e As StartupEventArgs) Handles MyBase.Startup
        Try
            _host = CreateHostBuilder().Build()

            Dim mainWindow = _host.Services.GetRequiredService(Of MainWindow)()
            mainWindow.Show()

        Catch ex As Exception
            MessageBox.Show($"Application startup failed: {ex.Message}",
                           "Fatal Error", MessageBoxButton.OK, MessageBoxImage.Error)
            Current.Shutdown(1)
        End Try
    End Sub

    ''' <summary>
    ''' Configure dependency injection
    ''' </summary>
    Private Function CreateHostBuilder() As IHostBuilder
        Return Host.CreateDefaultBuilder() _
            .ConfigureServices(Sub(context, services)
                services.AddLogging()
                services.AddSingleton(Of MainWindow)()
                services.AddSingleton(Of IMainWindowViewModel, MainWindowViewModel)()
            End Sub)
    End Function

    ''' <summary>
    ''' Application exit cleanup
    ''' </summary>
    Private Sub Application_Exit(sender As Object, e As ExitEventArgs) Handles MyBase.Exit
        _host?.Dispose()
    End Sub
End Class

''' <summary>
''' Main WPF window with modern MVVM patterns
''' </summary>
Public Partial Class MainWindow
    Inherits Window

    Private ReadOnly _logger As ILogger(Of MainWindow)

    Public Sub New(logger As ILogger(Of MainWindow), viewModel As IMainWindowViewModel)
        _logger = logger ?? throw New ArgumentNullException(NameOf(logger))
        DataContext = viewModel ?? throw New ArgumentNullException(NameOf(viewModel))

        InitializeComponent()

        _logger.LogInformation("MainWindow initialized with MVVM pattern")
    End Sub
End Class'''

    def _get_library_template(self) -> str:
        """Get class library template"""
        return '''Imports System
Imports System.Threading.Tasks
Imports Microsoft.Extensions.Logging

''' <summary>
''' EQ12 VB.NET Class Library
''' Expert-level implementation with modern .NET patterns
''' </summary>
Namespace EQ12.VBNet.Library

    ''' <summary>
    ''' Main service interface following SOLID principles
    ''' </summary>
    Public Interface IEQ12Service
        Function ProcessAsync(input As String) As Task(Of String)
        Function ValidateInput(input As String) As Boolean
        Event StatusChanged As EventHandler(Of StatusChangedEventArgs)
    End Interface

    ''' <summary>
    ''' Service implementation with comprehensive error handling
    ''' </summary>
    Public Class EQ12Service
        Implements IEQ12Service

        Private ReadOnly _logger As ILogger(Of EQ12Service)

        Public Sub New(logger As ILogger(Of EQ12Service))
            _logger = logger ?? throw New ArgumentNullException(NameOf(logger))
        End Sub

        ''' <summary>
        ''' Process input asynchronously with error handling
        ''' </summary>
        Public Async Function ProcessAsync(input As String) As Task(Of String) _
            Implements IEQ12Service.ProcessAsync

            Try
                If Not ValidateInput(input) Then
                    Throw New ArgumentException("Invalid input provided", NameOf(input))
                End If

                _logger.LogInformation("Processing input: {Input}", input)

                ' TODO: Implement your processing logic
                ' Use async/await patterns
                ' Add proper error handling
                ' Include comprehensive logging

                Await Task.Delay(100) ' Simulate async work

                Dim result = $"Processed: {input} at {DateTime.Now}"

                RaiseEvent StatusChanged(Me, New StatusChangedEventArgs("Processing completed"))

                _logger.LogInformation("Processing completed successfully")
                Return result

            Catch ex As Exception
                _logger.LogError(ex, "Processing failed for input: {Input}", input)
                Throw
            End Try
        End Function

        ''' <summary>
        ''' Validate input with comprehensive checks
        ''' </summary>
        Public Function ValidateInput(input As String) As Boolean _
            Implements IEQ12Service.ValidateInput

            Try
                Return Not String.IsNullOrWhiteSpace(input) AndAlso input.Length <= 1000
            Catch ex As Exception
                _logger.LogWarning(ex, "Input validation failed")
                Return False
            End Try
        End Function

        Public Event StatusChanged As EventHandler(Of StatusChangedEventArgs) _
            Implements IEQ12Service.StatusChanged
    End Class

    ''' <summary>
    ''' Status changed event arguments
    ''' </summary>
    Public Class StatusChangedEventArgs
        Inherits EventArgs

        Public ReadOnly Property Status As String

        Public Sub New(status As String)
            Me.Status = status
        End Sub
    End Class

End Namespace'''

    def _get_installer_template(self) -> str:
        """Get installer project template"""
        return '''Imports System
Imports System.ComponentModel
Imports System.Configuration.Install
Imports System.IO
Imports System.Reflection
Imports Microsoft.Win32

''' <summary>
''' EQ12 VB.NET Custom Installer
''' Advanced installer with registry modifications and custom actions
''' </summary>
<RunInstaller(True)>
Public Class EQ12CustomInstaller
    Inherits Installer

    Private Const ApplicationName As String = "EQ12 VB.NET Application"
    Private Const RegistryKeyPath As String = "SOFTWARE\\EQ12\\VBNetApp"

    ''' <summary>
    ''' Install custom actions
    ''' </summary>
    Public Overrides Sub Install(stateSaver As IDictionary)
        Try
            MyBase.Install(stateSaver)

            ' Create registry entries
            CreateRegistryEntries()

            ' Set up application data folders
            CreateApplicationFolders()

            ' Configure permissions
            SetupPermissions()

            ' Log installation
            LogInstallation("Installation completed successfully")

        Catch ex As Exception
            LogInstallation($"Installation failed: {ex.Message}")
            Throw New InstallException($"Installation failed: {ex.Message}", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Uninstall custom actions
    ''' </summary>
    Public Overrides Sub Uninstall(savedState As IDictionary)
        Try
            MyBase.Uninstall(savedState)

            ' Remove registry entries
            RemoveRegistryEntries()

            ' Clean up application data
            CleanupApplicationFolders()

            LogInstallation("Uninstallation completed successfully")

        Catch ex As Exception
            LogInstallation($"Uninstallation failed: {ex.Message}")
            ' Don't throw exception during uninstall
        End Try
    End Sub

    ''' <summary>
    ''' Create necessary registry entries
    ''' </summary>
    Private Sub CreateRegistryEntries()
        Try
            Using key = Registry.LocalMachine.CreateSubKey(RegistryKeyPath)
                If key IsNot Nothing Then
                    key.SetValue("InstallPath", Context.Parameters("targetdir"))
                    key.SetValue("Version", Assembly.GetExecutingAssembly().GetName().Version.ToString())
                    key.SetValue("InstallDate", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"))
                End If
            End Using
        Catch ex As Exception
            Throw New InstallException("Failed to create registry entries", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Remove registry entries during uninstall
    ''' </summary>
    Private Sub RemoveRegistryEntries()
        Try
            Registry.LocalMachine.DeleteSubKeyTree(RegistryKeyPath, False)
        Catch ex As Exception
            ' Log but don't fail uninstall for registry cleanup issues
            LogInstallation($"Registry cleanup warning: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Create application data folders
    ''' </summary>
    Private Sub CreateApplicationFolders()
        Try
            Dim appDataPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
                ApplicationName
            )

            If Not Directory.Exists(appDataPath) Then
                Directory.CreateDirectory(appDataPath)
            End If

            ' Create logs subfolder
            Dim logsPath = Path.Combine(appDataPath, "Logs")
            If Not Directory.Exists(logsPath) Then
                Directory.CreateDirectory(logsPath)
            End If

        Catch ex As Exception
            Throw New InstallException("Failed to create application folders", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Setup file and folder permissions
    ''' </summary>
    Private Sub SetupPermissions()
        ' TODO: Implement permission setup
        ' Use DirectorySecurity for folder permissions
        ' Consider user account context
        ' Implement least-privilege principle
    End Sub

    ''' <summary>
    ''' Clean up application folders during uninstall
    ''' </summary>
    Private Sub CleanupApplicationFolders()
        Try
            Dim appDataPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
                ApplicationName
            )

            If Directory.Exists(appDataPath) Then
                ' Only delete if directory is empty or contains only logs
                Dim files = Directory.GetFiles(appDataPath, "*", SearchOption.AllDirectories)
                If files.Length <= 10 Then ' Arbitrary small number for safety
                    Directory.Delete(appDataPath, True)
                End If
            End If

        Catch ex As Exception
            LogInstallation($"Cleanup warning: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Log installation events
    ''' </summary>
    Private Sub LogInstallation(message As String)
        Try
            Dim logPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
                ApplicationName, "Logs", "installer.log"
            )

            Directory.CreateDirectory(Path.GetDirectoryName(logPath))

            Using writer As New StreamWriter(logPath, True)
                writer.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss} - {message}")
            End Using

        Catch
            ' Ignore logging errors during installation
        End Try
    End Sub
End Class'''

    def _get_service_template(self) -> str:
        """Get Windows service template"""
        return '''Imports System
Imports System.ServiceProcess
Imports System.Threading
Imports System.Threading.Tasks
Imports Microsoft.Extensions.DependencyInjection
Imports Microsoft.Extensions.Hosting
Imports Microsoft.Extensions.Logging

''' <summary>
''' EQ12 VB.NET Windows Service
''' Modern service implementation with dependency injection and async patterns
''' </summary>
Public Class EQ12WindowsService
    Inherits ServiceBase

    Private _host As IHost
    Private _cancellationTokenSource As CancellationTokenSource

    Public Sub New()
        ServiceName = "EQ12VBNetService"
        CanStop = True
        CanPauseAndContinue = True
        AutoLog = True
    End Sub

    ''' <summary>
    ''' Service start with dependency injection
    ''' </summary>
    Protected Overrides Sub OnStart(args() As String)
        Try
            _cancellationTokenSource = New CancellationTokenSource()

            _host = Host.CreateDefaultBuilder() _
                .UseWindowsService() _
                .ConfigureServices(Sub(context, services)
                    services.AddLogging()
                    services.AddHostedService(Of ServiceWorker)()
                End Sub) _
                .Build()

            _host.StartAsync(_cancellationTokenSource.Token)

        Catch ex As Exception
            EventLog.WriteEntry("Service startup failed: " & ex.Message, EventLogEntryType.Error)
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Service stop with graceful shutdown
    ''' </summary>
    Protected Overrides Sub OnStop()
        Try
            _cancellationTokenSource?.Cancel()
            _host?.StopAsync(TimeSpan.FromSeconds(30)).Wait()
            _host?.Dispose()
        Catch ex As Exception
            EventLog.WriteEntry("Service stop failed: " & ex.Message, EventLogEntryType.Warning)
        End Try
    End Sub

    ''' <summary>
    ''' Service pause
    ''' </summary>
    Protected Overrides Sub OnPause()
        ' TODO: Implement pause logic
        MyBase.OnPause()
    End Sub

    ''' <summary>
    ''' Service continue
    ''' </summary>
    Protected Overrides Sub OnContinue()
        ' TODO: Implement continue logic
        MyBase.OnContinue()
    End Sub
End Class

''' <summary>
''' Service worker with background processing
''' </summary>
Public Class ServiceWorker
    Inherits BackgroundService

    Private ReadOnly _logger As ILogger(Of ServiceWorker)

    Public Sub New(logger As ILogger(Of ServiceWorker))
        _logger = logger ?? throw New ArgumentNullException(NameOf(logger))
    End Sub

    ''' <summary>
    ''' Main service execution loop
    ''' </summary>
    Protected Overrides Async Function ExecuteAsync(stoppingToken As CancellationToken) As Task
        Try
            _logger.LogInformation("EQ12 Windows Service started")

            While Not stoppingToken.IsCancellationRequested
                Try
                    ' TODO: Implement your service logic here
                    ' Use async patterns for I/O operations
                    ' Implement proper error handling
                    ' Add health checks and monitoring

                    Await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken)

                    _logger.LogDebug("Service heartbeat")

                Catch ex As OperationCanceledException
                    ' Expected when service is stopping
                    Exit While
                Catch ex As Exception
                    _logger.LogError(ex, "Service execution error: {Message}", ex.Message)

                    ' Wait before retrying to avoid rapid failures
                    Await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken)
                End Try
            End While

        Catch ex As Exception
            _logger.LogCritical(ex, "Service failed: {Message}", ex.Message)
            Throw
        Finally
            _logger.LogInformation("EQ12 Windows Service stopped")
        End Try
    End Function
End Class

''' <summary>
''' Program entry point for service
''' </summary>
Module Program
    Sub Main()
        Try
            ServiceBase.Run(New EQ12WindowsService())
        Catch ex As Exception
            Console.WriteLine("Service failed to start: " & ex.Message)
            Environment.Exit(1)
        End Try
    End Sub
End Module'''

    async def create_vbnet_project(
        self,
        project: VBNetProject
    ) -> Dict[str, Any]:
        """Create a VB.NET project with Copilot-optimized code"""

        logger.info(f"Creating VB.NET project: {project.name}")

        try:
            # Create project directory
            project.output_path.mkdir(parents=True, exist_ok=True)

            # Generate project file
            project_content = self._generate_project_file(project)
            project_file = project.output_path / f"{project.name}.vbproj"

            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(project_content)

            # Generate main code file
            main_code = self.vbnet_templates[project.project_type]
            main_file = project.output_path / "Program.vb"

            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(main_code)

            # Generate Copilot prompts file
            prompts_content = self._generate_copilot_prompts(project)
            prompts_file = project.output_path / "CopilotPrompts.md"

            with open(prompts_file, 'w', encoding='utf-8') as f:
                f.write(prompts_content)

            # Generate README
            readme_content = self._generate_readme(project)
            readme_file = project.output_path / "README.md"

            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            result = {
                'success': True,
                'project_path': str(project.output_path),
                'files_created': [
                    str(project_file),
                    str(main_file),
                    str(prompts_file),
                    str(readme_file)
                ],
                'copilot_prompts': project.copilot_prompts,
                'build_instructions': self._get_build_instructions(project)
            }

            logger.info(f"VB.NET project created successfully at {project.output_path}")
            return result

        except Exception as e:
            logger.error(f"Failed to create VB.NET project: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_path': str(project.output_path)
            }

    def _generate_project_file(self, project: VBNetProject) -> str:
        """Generate .vbproj file content"""

        project_type_sdk = {
            VBNetProjectType.CONSOLE_APP: "Microsoft.NET.Sdk",
            VBNetProjectType.WINDOWS_FORMS: "Microsoft.NET.Sdk",
            VBNetProjectType.WPF_APP: "Microsoft.NET.Sdk",
            VBNetProjectType.CLASS_LIBRARY: "Microsoft.NET.Sdk",
            VBNetProjectType.SERVICE: "Microsoft.NET.Sdk.Worker"
        }

        sdk = project_type_sdk.get(project.project_type, "Microsoft.NET.Sdk")

        output_type = {
            VBNetProjectType.CONSOLE_APP: "Exe",
            VBNetProjectType.WINDOWS_FORMS: "WinExe",
            VBNetProjectType.WPF_APP: "WinExe",
            VBNetProjectType.CLASS_LIBRARY: "Library",
            VBNetProjectType.SERVICE: "Exe"
        }.get(project.project_type, "Exe")

        use_wpf = "true" if project.project_type == VBNetProjectType.WPF_APP else "false"
        use_winforms = "true" if project.project_type == VBNetProjectType.WINDOWS_FORMS else "false"

        return f'''<Project Sdk="{sdk}">

  <PropertyGroup>
    <OutputType>{output_type}</OutputType>
    <RootNamespace>{project.name}</RootNamespace>
    <TargetFramework>{project.target_framework}</TargetFramework>
    <UseWPF>{use_wpf}</UseWPF>
    <UseWindowsForms>{use_winforms}</UseWindowsForms>
    <GenerateAssemblyInfo>true</GenerateAssemblyInfo>
    <AssemblyTitle>{project.name}</AssemblyTitle>
    <AssemblyDescription>EQ12 VB.NET {project.project_type.value}</AssemblyDescription>
    <AssemblyCompany>EQ12 Systems</AssemblyCompany>
    <AssemblyProduct>{project.name}</AssemblyProduct>
    <Copyright>© 2024 EQ12 Systems</Copyright>
    <AssemblyVersion>1.0.0.0</AssemblyVersion>
    <FileVersion>1.0.0.0</FileVersion>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.Extensions.Hosting" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
    <PackageReference Include="System.CommandLine" Version="2.0.0-beta4.22272.1" />
''' + ''.join([f'    <PackageReference Include="{dep}" />\n' for dep in project.dependencies]) + '''  </ItemGroup>

</Project>'''

    def _generate_copilot_prompts(self, project: VBNetProject) -> str:
        """Generate Copilot prompts file"""

        content = f"""# EQ12 VB.NET Copilot Prompts for {project.name}

## Expert VB.NET Development with GitHub Copilot

This file contains optimized prompts to get the most out of GitHub Copilot when developing VB.NET applications.

### Project Type: {project.project_type.value}

## Code Generation Prompts

"""

        for category, prompts in self.copilot_prompts.items():
            content += f"### {category.name.replace('_', ' ').title()}\n\n"

            for i, prompt in enumerate(prompts, 1):
                content += f"{i}. **{prompt}**\n\n"
                content += "   ```vb\n"
                content += "   ' Use this prompt in a VB.NET comment to trigger Copilot\n"
                content += f"   ' {prompt}\n"
                content += "   ```\n\n"

        content += """
## VB.NET Best Practices for Copilot

### 1. Use Descriptive Comments
```vb
' Create a Windows Forms button with click event handler that validates user input
```

### 2. Specify Patterns and Frameworks
```vb
' Implement repository pattern for data access with Entity Framework
```

### 3. Include Error Handling Requirements
```vb
' Add comprehensive error handling with logging and user-friendly messages
```

### 4. Request Modern .NET Features
```vb
' Use async/await pattern with ConfigureAwait(false) for library methods
```

### 5. Specify UI Requirements
```vb
' Create responsive WPF form with MVVM pattern and data binding
```

## Project-Specific Prompts

Based on your project type, use these specialized prompts:

"""

        # Add project-specific prompts
        project_prompts = {
            VBNetProjectType.CONSOLE_APP: [
                "Create command-line parser with help text and validation",
                "Implement async main with cancellation token support",
                "Add configuration file support with strongly-typed options"
            ],
            VBNetProjectType.WINDOWS_FORMS: [
                "Design modern Windows Forms with Material Design principles",
                "Implement MVVM pattern for Windows Forms application",
                "Create data-bound controls with validation and error providers"
            ],
            VBNetProjectType.WPF_APP: [
                "Build WPF application with MVVM and XAML data binding",
                "Implement WPF commands with ICommand interface",
                "Create responsive WPF layout with Grid and StackPanel"
            ],
            VBNetProjectType.CLASS_LIBRARY: [
                "Design class library with dependency injection support",
                "Implement async methods with proper exception handling",
                "Create extensible architecture with interfaces and abstractions"
            ]
        }

        if project.project_type in project_prompts:
            for prompt in project_prompts[project.project_type]:
                content += f"- {prompt}\n"

        return content

    def _generate_readme(self, project: VBNetProject) -> str:
        """Generate project README"""

        return f"""# {project.name}

EQ12 VB.NET {project.project_type.value} - Expert Implementation

## Overview

This project demonstrates modern VB.NET development practices with GitHub Copilot optimization.

### Features

- Modern .NET {project.target_framework} implementation
- Dependency injection and logging
- Async/await patterns throughout
- Comprehensive error handling
- Expert-level code organization
- GitHub Copilot optimized prompts

### Prerequisites

- .NET 6.0 or later
- Visual Studio 2022 or VS Code with VB.NET extensions
- GitHub Copilot (optional but recommended)

### Building

```bash
dotnet build
```

### Running

```bash
dotnet run
```

### GitHub Copilot Usage

This project includes optimized prompts for GitHub Copilot in `CopilotPrompts.md`.
Use these prompts as comments in your VB.NET code to get expert-level suggestions.

### Project Structure

- `Program.vb` - Main application entry point
- `{project.name}.vbproj` - Project configuration
- `CopilotPrompts.md` - Optimized Copilot prompts
- `README.md` - This file

### Development Guidelines

1. Follow VB.NET naming conventions
2. Use async/await for I/O operations
3. Implement proper error handling
4. Add XML documentation comments
5. Use dependency injection patterns
6. Include comprehensive logging

### Expert VB.NET Patterns Demonstrated

- Modern constructor injection
- Async/await with proper cancellation
- IDisposable implementation
- Event-driven architecture
- SOLID principles application
- Configuration and options patterns

## License

This project is part of the EQ12 system suite.
"""

    def _get_build_instructions(self, project: VBNetProject) -> List[str]:
        """Get build and deployment instructions"""

        instructions = [
            f"cd {project.output_path}",
            "dotnet restore",
            "dotnet build --configuration Release",
        ]

        if project.project_type in [VBNetProjectType.CONSOLE_APP, VBNetProjectType.SERVICE]:
            instructions.extend([
                "dotnet publish --configuration Release --output ./publish",
                "# Run with: dotnet run or dotnet ./publish/{project.name}.dll"
            ])
        elif project.project_type in [VBNetProjectType.WINDOWS_FORMS, VBNetProjectType.WPF_APP]:
            instructions.extend([
                "dotnet publish --configuration Release --output ./publish --self-contained true",
                f"# Run executable: ./publish/{project.name}.exe"
            ])

        return instructions

    async def optimize_existing_vbnet_code(
        self,
        code_file: Path,
        optimization_type: CopilotPromptCategory = CopilotPromptCategory.OPTIMIZATION
    ) -> Dict[str, Any]:
        """Analyze and optimize existing VB.NET code"""

        if not code_file.exists():
            return {'success': False, 'error': 'File not found'}

        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                original_code = f.read()

            # Analyze code structure
            analysis = self._analyze_vbnet_code(original_code)

            # Generate optimization suggestions
            suggestions = self._generate_optimization_suggestions(
                analysis, optimization_type
            )

            # Create optimized version with Copilot prompts
            optimized_prompts = self._create_optimization_prompts(
                suggestions, optimization_type
            )

            result = {
                'success': True,
                'file_analyzed': str(code_file),
                'analysis': analysis,
                'suggestions': suggestions,
                'copilot_prompts': optimized_prompts,
                'optimization_type': optimization_type.name
            }

            # Save optimization report
            report_file = code_file.parent / f"{code_file.stem}_optimization_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_optimization_report(result))

            result['report_file'] = str(report_file)

            return result

        except Exception as e:
            logger.error(f"Code optimization failed: {e}")
            return {'success': False, 'error': str(e)}

    def _analyze_vbnet_code(self, code: str) -> Dict[str, Any]:
        """Analyze VB.NET code structure"""

        analysis = {
            'lines_of_code': len(code.splitlines()),
            'has_async_methods': 'Async Function' in code or 'Async Sub' in code,
            'has_error_handling': 'Try' in code and 'Catch' in code,
            'has_logging': 'ILogger' in code or 'Log.' in code,
            'has_dependency_injection': 'New(' in code and 'As I' in code,
            'uses_modern_patterns': 'Await ' in code,
            'class_count': code.count('Public Class') + code.count('Private Class'),
            'method_count': code.count('Public Function') + code.count('Private Function') +
                           code.count('Public Sub') + code.count('Private Sub'),
            'interface_count': code.count('Public Interface'),
            'has_xml_docs': "'''" in code,
            'complexity_score': self._calculate_complexity_score(code)
        }

        return analysis

    def _calculate_complexity_score(self, code: str) -> int:
        """Calculate code complexity score"""

        complexity = 0

        # Add points for control structures
        complexity += code.count('If ')
        complexity += code.count('For ')
        complexity += code.count('While ')
        complexity += code.count('Select Case')
        complexity += code.count('Try')

        # Add points for nested structures
        lines = code.splitlines()
        indent_level = 0
        max_indent = 0

        for line in lines:
            stripped = line.lstrip()
            if stripped:
                current_indent = len(line) - len(stripped)
                if current_indent > indent_level:
                    indent_level = current_indent
                    max_indent = max(max_indent, current_indent)

        complexity += max_indent // 4  # Assuming 4-space indentation

        return complexity

    def _generate_optimization_suggestions(
        self,
        analysis: Dict[str, Any],
        optimization_type: CopilotPromptCategory
    ) -> List[str]:
        """Generate code optimization suggestions"""

        suggestions = []

        if optimization_type == CopilotPromptCategory.MODERNIZATION:
            if not analysis['has_async_methods']:
                suggestions.append("Convert synchronous methods to async/await pattern")
            if not analysis['has_dependency_injection']:
                suggestions.append("Implement dependency injection for better testability")
            if not analysis['has_logging']:
                suggestions.append("Add comprehensive logging with Microsoft.Extensions.Logging")

        elif optimization_type == CopilotPromptCategory.OPTIMIZATION:
            if analysis['complexity_score'] > 20:
                suggestions.append("Refactor complex methods into smaller, focused functions")
            if not analysis['uses_modern_patterns']:
                suggestions.append("Use modern .NET patterns like LINQ and expression bodied members")

        elif optimization_type == CopilotPromptCategory.REFACTORING:
            if analysis['class_count'] > 5 and analysis['lines_of_code'] > 500:
                suggestions.append("Consider splitting large classes into separate files")
            if not analysis['interface_count'] and analysis['class_count'] > 2:
                suggestions.append("Extract interfaces for better abstraction")

        if not analysis['has_error_handling']:
            suggestions.append("Add comprehensive error handling with try-catch blocks")

        if not analysis['has_xml_docs']:
            suggestions.append("Add XML documentation comments for all public members")

        return suggestions

    def _create_optimization_prompts(
        self,
        suggestions: List[str],
        optimization_type: CopilotPromptCategory
    ) -> List[str]:
        """Create Copilot prompts for optimization"""

        prompts = []

        for suggestion in suggestions:
            if "async/await" in suggestion:
                prompts.append(
                    "Refactor this synchronous method to use async/await pattern " +
                    "with proper cancellation token support and ConfigureAwait(false)"
                )
            elif "dependency injection" in suggestion:
                prompts.append(
                    "Implement constructor injection with interface dependencies " +
                    "following SOLID principles and modern .NET patterns"
                )
            elif "logging" in suggestion:
                prompts.append(
                    "Add structured logging with Microsoft.Extensions.Logging, " +
                    "including appropriate log levels and structured data"
                )
            elif "error handling" in suggestion:
                prompts.append(
                    "Add comprehensive error handling with specific exception types, " +
                    "logging, and graceful failure recovery"
                )
            elif "documentation" in suggestion:
                prompts.append(
                    "Add complete XML documentation comments with parameter " +
                    "descriptions, return values, and usage examples"
                )
            else:
                prompts.append(f"Implement improvement: {suggestion}")

        return prompts

    def _generate_optimization_report(self, result: Dict[str, Any]) -> str:
        """Generate optimization report in markdown"""

        report = f"""# VB.NET Code Optimization Report

## File Analyzed
`{result['file_analyzed']}`

## Code Analysis Results

"""

        analysis = result['analysis']
        for key, value in analysis.items():
            report += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        report += f"\n## Optimization Suggestions\n\n"

        for i, suggestion in enumerate(result['suggestions'], 1):
            report += f"{i}. {suggestion}\n"

        report += f"\n## GitHub Copilot Prompts\n\n"
        report += "Use these prompts as comments in your VB.NET code:\n\n"

        for i, prompt in enumerate(result['copilot_prompts'], 1):
            report += f"### Prompt {i}\n"
            report += f"```vb\n' {prompt}\n```\n\n"

        report += f"""
## Next Steps

1. Open the file in Visual Studio or VS Code
2. Add the Copilot prompts as comments above the relevant code sections
3. Let GitHub Copilot generate improved code suggestions
4. Review and test the generated code
5. Commit improvements to version control

## Best Practices Checklist

- [ ] Use async/await for I/O operations
- [ ] Implement proper error handling
- [ ] Add dependency injection
- [ ] Include comprehensive logging
- [ ] Write XML documentation
- [ ] Follow SOLID principles
- [ ] Use modern .NET patterns
- [ ] Implement proper resource disposal
- [ ] Add unit tests
- [ ] Consider performance implications

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return report


# Integration functions for EQ12 system
async def create_eq12_vbnet_suite() -> Dict[str, Any]:
    """Create comprehensive VB.NET project suite for EQ12"""

    assistant = EQ12VBNetCopilotAssistant()

    projects = [
        VBNetProject(
            name="EQ12ConsoleTools",
            project_type=VBNetProjectType.CONSOLE_APP,
            dependencies=["CommandLineParser", "NLog"]
        ),
        VBNetProject(
            name="EQ12WindowsManager",
            project_type=VBNetProjectType.WINDOWS_FORMS,
            dependencies=["Microsoft.Extensions.Hosting.WindowsServices"]
        ),
        VBNetProject(
            name="EQ12CoreLibrary",
            project_type=VBNetProjectType.CLASS_LIBRARY,
            dependencies=["Newtonsoft.Json"]
        ),
        VBNetProject(
            name="EQ12ServiceManager",
            project_type=VBNetProjectType.SERVICE,
            dependencies=["Microsoft.Extensions.Hosting.WindowsServices"]
        )
    ]

    results = {}

    for project in projects:
        logger.info(f"Creating {project.name}...")
        result = await assistant.create_vbnet_project(project)
        results[project.name] = result

    # Generate master documentation
    master_doc = await _generate_master_documentation(results)

    return {
        'success': True,
        'projects_created': len([r for r in results.values() if r['success']]),
        'project_results': results,
        'master_documentation': master_doc
    }


async def _generate_master_documentation(results: Dict[str, Any]) -> str:
    """Generate master documentation for VB.NET suite"""

    doc = f"""# EQ12 VB.NET Development Suite

Complete VB.NET project collection with GitHub Copilot optimization.

## Projects Created

"""

    for project_name, result in results.items():
        if result['success']:
            doc += f"### {project_name}\n"
            doc += f"- **Path**: `{result['project_path']}`\n"
            doc += f"- **Files**: {len(result['files_created'])} created\n"
            doc += f"- **Copilot Prompts**: {len(result['copilot_prompts'])} available\n\n"

    doc += """
## Quick Start Guide

1. Open any project in Visual Studio 2022 or VS Code
2. Install GitHub Copilot extension
3. Review `CopilotPrompts.md` in each project
4. Use prompts as comments to trigger intelligent code suggestions
5. Build and run projects with `dotnet build` and `dotnet run`

## Expert VB.NET Features Demonstrated

- Modern .NET 6+ patterns
- Async/await throughout
- Dependency injection
- Structured logging
- Error handling best practices
- SOLID principles
- GitHub Copilot optimization

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return doc


def main():
    """Main execution function"""
    print("""
🔧 EQ12 VB.NET COPILOT INTEGRATION SUITE
======================================

Expert VB.NET Development Assistant:
✅ Modern .NET project templates
✅ GitHub Copilot optimized prompts
✅ Windows Forms & WPF patterns
✅ Console applications & services
✅ Advanced installer creation
✅ Code analysis & optimization

Creating comprehensive VB.NET suite...
    """)

    try:
        # Create VB.NET project suite
        results = asyncio.run(create_eq12_vbnet_suite())

        print("\n🎯 VB.NET SUITE CREATION RESULTS")
        print("=" * 40)
        print("Projects Created: {results['projects_created']}")

        for project_name, result in results['project_results'].items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print("\n{project_name}: {status}")

            if result['success']:
                print("  📁 Path: {result['project_path']}")
                print("  📄 Files: {len(result['files_created'])}")
            else:
                print("  ❌ Error: {result.get('error', 'Unknown error')}")

        # Save master documentation
        docs_path = Path("C:/EQ12/logs/vbnet_documentation")
        docs_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_file = docs_path / f"vbnet_suite_docs_{timestamp}.md"

        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(results['master_documentation'])

        print("\n📚 Documentation: {doc_file}")
        print("\n✅ VB.NET COPILOT SUITE COMPLETE!")

        return True

    except Exception as e:
        logger.error(f"VB.NET suite creation failed: {e}")
        print("❌ Error: {e}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
