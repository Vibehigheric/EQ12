' EQ12 Control Center - Main Dashboard
' VB.NET WPF Application - Entry Point

Imports System.Net.Http
Imports System.Threading
Imports Newtonsoft.Json
Imports System.Data.SQLite

Public Class MainWindow
    ' HTTP client for Python API communication
    Private ReadOnly httpClient As New HttpClient()
    Private ReadOnly pythonApiBase As String = "http://localhost:5000"
    
    ' Background worker for status updates
    Private statusUpdateTimer As DispatcherTimer
    
    ' System state
    Private systemState As EQ12SystemState
    
    Public Sub New()
        InitializeComponent()
        
        ' Configure HTTP client
        httpClient.Timeout = TimeSpan.FromSeconds(10)
        
        ' Initialize status update timer (5 second interval)
        statusUpdateTimer = New DispatcherTimer()
        statusUpdateTimer.Interval = TimeSpan.FromSeconds(5)
        AddHandler statusUpdateTimer.Tick, AddressOf UpdateStatus
        statusUpdateTimer.Start()
        
        ' Initialize system state
        systemState = New EQ12SystemState()
        
        ' Set initial UI state
        InitializeUI()
    End Sub
    
    Private Sub InitializeUI()
        ' Set window properties
        Me.Title = "EQ12 Control Center - Real-Time Automation Dashboard"
        Me.Width = 1400
        Me.Height = 900
        
        ' Status bar
        statusLabel.Content = "Connecting to Python backend..."
        statusIcon.Fill = Brushes.Orange
        
        ' Initial button states
        btnStartScanner.IsEnabled = True
        btnStopScanner.IsEnabled = False
        btnStartValidator.IsEnabled = True
        btnStopValidator.IsEnabled = False
        
        ' Load configuration from database
        LoadConfiguration()
    End Sub
    
    Private Async Sub UpdateStatus(sender As Object, e As EventArgs)
        ' Poll Python backend for status updates
        Try
            Dim response = Await httpClient.GetAsync($"{pythonApiBase}/status")
            
            If response.IsSuccessStatusCode Then
                Dim json = Await response.Content.ReadAsStringAsync()
                systemState = JsonConvert.DeserializeObject(Of EQ12SystemState)(json)
                
                ' Update UI on main thread
                Dispatcher.Invoke(Sub()
                    UpdateDashboard()
                    statusLabel.Content = "Connected | Last Update: " & DateTime.Now.ToString("HH:mm:ss")
                    statusIcon.Fill = Brushes.Green
                End Sub)
            Else
                ' Connection failed
                Dispatcher.Invoke(Sub()
                    statusLabel.Content = "Connection Lost | Retrying..."
                    statusIcon.Fill = Brushes.Red
                End Sub)
            End If
            
        Catch ex As Exception
            ' Handle errors gracefully
            Dispatcher.Invoke(Sub()
                statusLabel.Content = "Error: " & ex.Message
                statusIcon.Fill = Brushes.Red
            End Sub)
        End Try
    End Sub
    
    Private Sub UpdateDashboard()
        ' Update resource gauges
        cpuProgressBar.Value = systemState.CpuPercent
        memoryProgressBar.Value = systemState.MemoryPercent
        diskProgressBar.Value = systemState.DiskPercent
        
        lblCpuValue.Content = $"{systemState.CpuPercent:F1}%"
        lblMemoryValue.Content = $"{systemState.MemoryPercent:F1}% ({systemState.MemoryUsedGB:F1} GB)"
        lblDiskValue.Content = $"{systemState.DiskFreeGB:F0} GB Free"
        
        ' Update worker counts
        lblActiveWorkers.Content = systemState.ActiveWorkers.ToString()
        lblScannerWorkers.Content = systemState.ScannerWorkers.ToString()
        lblValidatorWorkers.Content = systemState.ValidatorWorkers.ToString()
        
        ' Update task status
        lblScannerStatus.Content = systemState.ScannerStatus
        lblValidatorStatus.Content = systemState.ValidatorStatus
        lblBankrollStatus.Content = systemState.BankrollStatus
        
        ' Update opportunities counter
        lblTotalOpportunities.Content = systemState.TotalOpportunities.ToString("N0")
        
        ' Update latest opportunities list
        If systemState.LatestOpportunities IsNot Nothing AndAlso systemState.LatestOpportunities.Count > 0 Then
            lstOpportunities.ItemsSource = systemState.LatestOpportunities
        End If
        
        ' Color-code based on health
        If systemState.MemoryPercent > 85 Then
            memoryProgressBar.Foreground = Brushes.Red
        ElseIf systemState.MemoryPercent > 75 Then
            memoryProgressBar.Foreground = Brushes.Orange
        Else
            memoryProgressBar.Foreground = Brushes.Green
        End If
    End Sub
    
    ' Button Click Handlers
    Private Async Sub btnStartScanner_Click(sender As Object, e As RoutedEventArgs)
        Try
            btnStartScanner.IsEnabled = False
            btnStopScanner.IsEnabled = True
            
            ' Get worker count from UI
            Dim workers = CInt(txtWorkerCount.Text)
            Dim duration = CInt(txtDuration.Text)
            
            ' Build request
            Dim requestData = New With {
                .workers = workers,
                .duration = duration
            }
            Dim content As New StringContent(JsonConvert.SerializeObject(requestData), System.Text.Encoding.UTF8, "application/json")
            
            ' Call Python API
            Dim response = Await httpClient.PostAsync($"{pythonApiBase}/scanner/start", content)
            
            If response.IsSuccessStatusCode Then
                MessageBox.Show($"Scanner started with {workers} workers for {duration} minutes", "Success", MessageBoxButton.OK, MessageBoxImage.Information)
            Else
                MessageBox.Show("Failed to start scanner: " & Await response.Content.ReadAsStringAsync(), "Error", MessageBoxButton.OK, MessageBoxImage.Error)
                btnStartScanner.IsEnabled = True
                btnStopScanner.IsEnabled = False
            End If
            
        Catch ex As Exception
            MessageBox.Show("Error starting scanner: " & ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error)
            btnStartScanner.IsEnabled = True
            btnStopScanner.IsEnabled = False
        End Try
    End Sub
    
    Private Async Sub btnStopScanner_Click(sender As Object, e As RoutedEventArgs)
        Try
            Dim response = Await httpClient.PostAsync($"{pythonApiBase}/scanner/stop", Nothing)
            
            If response.IsSuccessStatusCode Then
                btnStartScanner.IsEnabled = True
                btnStopScanner.IsEnabled = False
                MessageBox.Show("Scanner stopped successfully", "Success", MessageBoxButton.OK, MessageBoxImage.Information)
            End If
            
        Catch ex As Exception
            MessageBox.Show("Error stopping scanner: " & ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error)
        End Try
    End Sub
    
    Private Async Sub btnStartValidator_Click(sender As Object, e As RoutedEventArgs)
        Try
            btnStartValidator.IsEnabled = False
            btnStopValidator.IsEnabled = True
            
            Dim content As New StringContent("{}", System.Text.Encoding.UTF8, "application/json")
            Dim response = Await httpClient.PostAsync($"{pythonApiBase}/validator/start", content)
            
            If response.IsSuccessStatusCode Then
                MessageBox.Show("Parlay Validator started", "Success", MessageBoxButton.OK, MessageBoxImage.Information)
            End If
            
        Catch ex As Exception
            MessageBox.Show("Error starting validator: " & ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error)
            btnStartValidator.IsEnabled = True
            btnStopValidator.IsEnabled = False
        End Try
    End Sub
    
    Private Sub btnStopValidator_Click(sender As Object, e As RoutedEventArgs)
        ' Similar to scanner stop
    End Sub
    
    Private Sub btnViewLogs_Click(sender As Object, e As RoutedEventArgs)
        ' Open logs viewer window
        Dim logsWindow As New LogsViewerWindow()
        logsWindow.Show()
    End Sub
    
    Private Sub btnDataExplorer_Click(sender As Object, e As RoutedEventArgs)
        ' Open data explorer window
        Dim explorerWindow As New DataExplorerWindow()
        explorerWindow.Show()
    End Sub
    
    Private Sub btnBankrollManager_Click(sender As Object, e As RoutedEventArgs)
        ' Open bankroll manager window
        Dim bankrollWindow As New BankrollManagerWindow()
        bankrollWindow.Show()
    End Sub
    
    Private Sub btnSettings_Click(sender As Object, e As RoutedEventArgs)
        ' Open settings window
        Dim settingsWindow As New SettingsWindow()
        If settingsWindow.ShowDialog() = True Then
            ' Reload configuration if saved
            LoadConfiguration()
        End If
    End Sub
    
    Private Sub LoadConfiguration()
        ' Load from database or config file
        Try
            Dim configPath = "C:\EQ12_BROKEN_20251122_210342\config\eq12_config.json"
            If IO.File.Exists(configPath) Then
                Dim json = IO.File.ReadAllText(configPath)
                Dim config = JsonConvert.DeserializeObject(Of EQ12Configuration)(json)
                
                ' Apply to UI
                txtWorkerCount.Text = config.DefaultWorkers.ToString()
                txtDuration.Text = config.DefaultDuration.ToString()
            End If
        Catch ex As Exception
            ' Use defaults
            txtWorkerCount.Text = "6"
            txtDuration.Text = "60"
        End Try
    End Sub
    
    Protected Overrides Sub OnClosing(e As ComponentModel.CancelEventArgs)
        ' Stop timer on close
        statusUpdateTimer.Stop()
        
        ' Confirm exit
        Dim result = MessageBox.Show("Are you sure you want to exit? Running tasks will continue in background.", 
                                     "Confirm Exit", 
                                     MessageBoxButton.YesNo, 
                                     MessageBoxImage.Question)
        
        If result = MessageBoxResult.No Then
            e.Cancel = True
        Else
            MyBase.OnClosing(e)
        End If
    End Sub
End Class

' Data Models
Public Class EQ12SystemState
    Public Property CpuPercent As Double
    Public Property MemoryPercent As Double
    Public Property MemoryUsedGB As Double
    Public Property MemoryAvailableGB As Double
    Public Property DiskPercent As Double
    Public Property DiskFreeGB As Double
    Public Property ActiveWorkers As Integer
    Public Property ScannerWorkers As Integer
    Public Property ValidatorWorkers As Integer
    Public Property BankrollWorkers As Integer
    Public Property ScannerStatus As String
    Public Property ValidatorStatus As String
    Public Property BankrollStatus As String
    Public Property TotalOpportunities As Integer
    Public Property LatestOpportunities As List(Of Opportunity)
End Class

Public Class Opportunity
    Public Property Sport As String
    Public Property Game As String
    Public Property MarketType As String
    Public Property ProfitMargin As Double
    Public Property ExpectedValue As Double
    Public Property Timestamp As DateTime
End Class

Public Class EQ12Configuration
    Public Property DefaultWorkers As Integer
    Public Property DefaultDuration As Integer
    Public Property ApiKey As String
    Public Property DatabasePath As String
    Public Property LogsPath As String
End Class
