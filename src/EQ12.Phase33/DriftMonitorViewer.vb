Imports System.Windows.Forms
Imports System.IO
Imports Newtonsoft.Json
Imports System.Linq

''' <summary>
''' GUI for visualizing ML model drift status
''' Real-time view of PSI scores, feature drift, model health
''' </summary>
Public Class DriftMonitorViewer
    Inherits Form
    
    Private _dataRoot As String
    Private WithEvents timerRefresh As New Timer()
    
    Private pnlStatus As Panel
    Private lblMaxPsi As Label
    Private lblDriftedFeatures As Label
    Private lblModelAge As Label
    Private lstFeatureDrift As ListBox
    Private btnRefreshNow As Button
    Private lblStatusIndicator As Label
    
    Public Sub New(dataRoot As String)
        _dataRoot = dataRoot
        InitializeComponent()
        LoadDriftData()
        timerRefresh.Interval = 30000 ' 30 seconds
        timerRefresh.Start()
    End Sub
    
    Private Sub InitializeComponent()
        Text = "Drift Monitor Viewer — ML Model Health"
        Size = New Size(800, 600)
        BackColor = Color.DarkGray
        
        ' Status panel
        pnlStatus = New Panel With {.Location = New Point(10, 10), .Size = New Size(760, 100), .BackColor = Color.LightGray}
        Controls.Add(pnlStatus)
        
        ' Status indicator
        lblStatusIndicator = New Label With {
            .Text = "🟡 LOADING...",
            .Location = New Point(10, 10),
            .Size = New Size(740, 40),
            .Font = New Font("Courier", 16, FontStyle.Bold),
            .ForeColor = Color.Orange
        }
        pnlStatus.Controls.Add(lblStatusIndicator)
        
        ' Max PSI
        lblMaxPsi = New Label With {
            .Text = "Max PSI: --",
            .Location = New Point(10, 55),
            .Size = New Size(250, 30),
            .Font = New Font("Courier", 12)
        }
        pnlStatus.Controls.Add(lblMaxPsi)
        
        ' Drifted features
        lblDriftedFeatures = New Label With {
            .Text = "Drifted Features: --",
            .Location = New Point(270, 55),
            .Size = New Size(250, 30),
            .Font = New Font("Courier", 12)
        }
        pnlStatus.Controls.Add(lblDriftedFeatures)
        
        ' Model age
        lblModelAge = New Label With {
            .Text = "Model Age: -- days",
            .Location = New Point(530, 55),
            .Size = New Size(220, 30),
            .Font = New Font("Courier", 12)
        }
        pnlStatus.Controls.Add(lblModelAge)
        
        ' Feature drift list
        lstFeatureDrift = New ListBox With {
            .Location = New Point(10, 120),
            .Size = New Size(760, 430),
            .Font = New Font("Courier", 10)
        }
        Controls.Add(lstFeatureDrift)
        
        ' Refresh button
        btnRefreshNow = New Button With {
            .Text = "REFRESH NOW",
            .Location = New Point(10, 560),
            .Size = New Size(120, 30),
            .BackColor = Color.LightBlue
        }
        AddHandler btnRefreshNow.Click, AddressOf BtnRefreshNow_Click
        Controls.Add(btnRefreshNow)
    End Sub
    
    Private Sub LoadDriftData()
        Try
            Dim driftFile = Path.Combine(_dataRoot, "logs", "drift_report_latest.json")
            
            If Not File.Exists(driftFile) Then
                lstFeatureDrift.Items.Clear()
                lstFeatureDrift.Items.Add("[NO DRIFT REPORT FOUND]")
                lstFeatureDrift.Items.Add("Run drift_monitor.py first")
                Return
            End If
            
            Dim json = File.ReadAllText(driftFile)
            Dim report = JsonConvert.DeserializeObject(Of DriftReportData)(json)
            
            ' Update status
            Dim isDrifted = report.MaxPsi > 0.25
            If isDrifted Then
                lblStatusIndicator.Text = "🔴 DRIFT DETECTED — RETRAIN REQUIRED"
                lblStatusIndicator.ForeColor = Color.Red
                pnlStatus.BackColor = Color.LightCoral
            Else
                lblStatusIndicator.Text = "✅ MODEL HEALTHY"
                lblStatusIndicator.ForeColor = Color.Green
                pnlStatus.BackColor = Color.LightGreen
            End If
            
            lblMaxPsi.Text = $"Max PSI: {report.MaxPsi:F3}"
            lblDriftedFeatures.Text = $"Drifted Features: {report.DriftedFeatures.Count}"
            lblModelAge.Text = $"Model Age: {(DateTime.UtcNow - report.Timestamp).Days} days"
            
            ' List features
            lstFeatureDrift.Items.Clear()
            lstFeatureDrift.Items.Add("=== FEATURE DRIFT ANALYSIS ===")
            lstFeatureDrift.Items.Add("")
            
            For Each feature In report.DriftedFeatures
                Dim status = If(feature.Value > 0.25, "⚠️ CRITICAL", "🟡 MODERATE")
                lstFeatureDrift.Items.Add($"{status} | {feature.Key}: PSI = {feature.Value:F3}")
            Next
            
            If report.DriftedFeatures.Count = 0 Then
                lstFeatureDrift.Items.Add("No feature drift detected")
            End If
            
            lstFeatureDrift.Items.Add("")
            lstFeatureDrift.Items.Add($"=== MODEL INFO ===")
            lstFeatureDrift.Items.Add($"Generated: {report.Timestamp:yyyy-MM-dd HH:mm:ss}")
            lstFeatureDrift.Items.Add($"Confidence: {report.Confidence:P}")
            
        Catch ex As Exception
            lstFeatureDrift.Items.Clear()
            lstFeatureDrift.Items.Add($"[ERROR] {ex.Message}")
        End Try
    End Sub
    
    Private Sub BtnRefreshNow_Click(sender As Object, e As EventArgs)
        LoadDriftData()
    End Sub
    
    Private Sub timerRefresh_Tick(sender As Object, e As EventArgs) Handles timerRefresh.Tick
        LoadDriftData()
    End Sub
End Class

Public Class DriftReportData
    <JsonProperty("max_psi")>
    Public Property MaxPsi As Double
    
    <JsonProperty("drifted_features")>
    Public Property DriftedFeatures As Dictionary(Of String, Double)
    
    <JsonProperty("timestamp")>
    Public Property Timestamp As DateTime
    
    <JsonProperty("confidence")>
    Public Property Confidence As Double
    
    <JsonProperty("recommendation")>
    Public Property Recommendation As String
End Class
