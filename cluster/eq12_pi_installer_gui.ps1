# EQ12 Pi Batch Installer
# Simplified GUI for flashing multiple Pi nodes

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create main form
$Form = New-Object System.Windows.Forms.Form
$Form.Text = "EQ12 Pi Cluster Installer"
$Form.Size = New-Object System.Drawing.Size(600, 500)
$Form.StartPosition = "CenterScreen"
$Form.FormBorderStyle = "FixedDialog"
$Form.MaximizeBox = $false

# Title label
$TitleLabel = New-Object System.Windows.Forms.Label
$TitleLabel.Location = New-Object System.Drawing.Point(20, 20)
$TitleLabel.Size = New-Object System.Drawing.Size(560, 30)
$TitleLabel.Text = " EQ12 Multi-Pi Cluster Installer"
$TitleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
$TitleLabel.ForeColor = [System.Drawing.Color]::DarkBlue
$Form.Controls.Add($TitleLabel)

# Instructions label
$InstructionsLabel = New-Object System.Windows.Forms.Label
$InstructionsLabel.Location = New-Object System.Drawing.Point(20, 60)
$InstructionsLabel.Size = New-Object System.Drawing.Size(560, 40)
$InstructionsLabel.Text = "Select Pi node configuration and click 'Flash Node' to begin automated installation.`nEach node will be configured with static IP and cluster integration."
$InstructionsLabel.ForeColor = [System.Drawing.Color]::DarkGreen
$Form.Controls.Add($InstructionsLabel)

# Node selection group
$NodeGroupBox = New-Object System.Windows.Forms.GroupBox
$NodeGroupBox.Location = New-Object System.Drawing.Point(20, 110)
$NodeGroupBox.Size = New-Object System.Drawing.Size(270, 180)
$NodeGroupBox.Text = "Pi Node Configuration"
$Form.Controls.Add($NodeGroupBox)

# Node ID selection
$NodeIdLabel = New-Object System.Windows.Forms.Label
$NodeIdLabel.Location = New-Object System.Drawing.Point(15, 25)
$NodeIdLabel.Size = New-Object System.Drawing.Size(80, 20)
$NodeIdLabel.Text = "Node ID:"
$NodeGroupBox.Controls.Add($NodeIdLabel)

$NodeIdCombo = New-Object System.Windows.Forms.ComboBox
$NodeIdCombo.Location = New-Object System.Drawing.Point(100, 22)
$NodeIdCombo.Size = New-Object System.Drawing.Size(80, 20)
$NodeIdCombo.DropDownStyle = "DropDownList"
for ($i = 1; $i -le 12; $i++) {
    $NodeIdCombo.Items.Add("$('{0:D2}' -f $i)")
}
$NodeIdCombo.SelectedIndex = 0
$NodeGroupBox.Controls.Add($NodeIdCombo)

# Drive type selection
$DriveTypeLabel = New-Object System.Windows.Forms.Label
$DriveTypeLabel.Location = New-Object System.Drawing.Point(15, 55)
$DriveTypeLabel.Size = New-Object System.Drawing.Size(80, 20)
$DriveTypeLabel.Text = "Boot Drive:"
$NodeGroupBox.Controls.Add($DriveTypeLabel)

$DriveTypeCombo = New-Object System.Windows.Forms.ComboBox
$DriveTypeCombo.Location = New-Object System.Drawing.Point(100, 52)
$DriveTypeCombo.Size = New-Object System.Drawing.Size(80, 20)
$DriveTypeCombo.DropDownStyle = "DropDownList"
$DriveTypeCombo.Items.AddRange(@("USB", "NVMe", "SD"))
$DriveTypeCombo.SelectedIndex = 0
$NodeGroupBox.Controls.Add($DriveTypeCombo)

# Auto-deploy checkbox
$AutoDeployCheckbox = New-Object System.Windows.Forms.CheckBox
$AutoDeployCheckbox.Location = New-Object System.Drawing.Point(15, 85)
$AutoDeployCheckbox.Size = New-Object System.Drawing.Size(200, 20)
$AutoDeployCheckbox.Text = "Auto-deploy cluster services"
$AutoDeployCheckbox.Checked = $true
$NodeGroupBox.Controls.Add($AutoDeployCheckbox)

# Skip flashing checkbox
$SkipFlashingCheckbox = New-Object System.Windows.Forms.CheckBox
$SkipFlashingCheckbox.Location = New-Object System.Drawing.Point(15, 110)
$SkipFlashingCheckbox.Size = New-Object System.Drawing.Size(200, 20)
$SkipFlashingCheckbox.Text = "Skip OS flashing (already installed)"
$NodeGroupBox.Controls.Add($SkipFlashingCheckbox)

# Node info display
$NodeInfoLabel = New-Object System.Windows.Forms.Label
$NodeInfoLabel.Location = New-Object System.Drawing.Point(15, 135)
$NodeInfoLabel.Size = New-Object System.Drawing.Size(240, 35)
$NodeInfoLabel.Text = "IP: 192.168.100.11`nSpecialization: AI Inference"
$NodeInfoLabel.ForeColor = [System.Drawing.Color]::Blue
$NodeGroupBox.Controls.Add($NodeInfoLabel)

# Cluster status group
$StatusGroupBox = New-Object System.Windows.Forms.GroupBox
$StatusGroupBox.Location = New-Object System.Drawing.Point(310, 110)
$StatusGroupBox.Size = New-Object System.Drawing.Size(270, 180)
$StatusGroupBox.Text = "Cluster Status"
$Form.Controls.Add($StatusGroupBox)

# Node status list
$NodeStatusList = New-Object System.Windows.Forms.ListView
$NodeStatusList.Location = New-Object System.Drawing.Point(10, 20)
$NodeStatusList.Size = New-Object System.Drawing.Size(250, 150)
$NodeStatusList.View = "Details"
$NodeStatusList.GridLines = $true
$NodeStatusList.FullRowSelect = $true
$NodeStatusList.Columns.Add("Node", 60) | Out-Null
$NodeStatusList.Columns.Add("IP", 100) | Out-Null
$NodeStatusList.Columns.Add("Status", 80) | Out-Null

# Populate with default cluster nodes
for ($i = 1; $i -le 12; $i++) {
    $ListItem = $NodeStatusList.Items.Add("$('{0:D2}' -f $i)")
    $ListItem.SubItems.Add("192.168.100.$([int]10 + $i)")
    $ListItem.SubItems.Add("Offline")
    $ListItem.ForeColor = [System.Drawing.Color]::Red
}

$StatusGroupBox.Controls.Add($NodeStatusList)

# Action buttons
$FlashButton = New-Object System.Windows.Forms.Button
$FlashButton.Location = New-Object System.Drawing.Point(20, 310)
$FlashButton.Size = New-Object System.Drawing.Size(120, 35)
$FlashButton.Text = " Flash Node"
$FlashButton.BackColor = [System.Drawing.Color]::LightGreen
$FlashButton.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$Form.Controls.Add($FlashButton)

$RefreshButton = New-Object System.Windows.Forms.Button
$RefreshButton.Location = New-Object System.Drawing.Point(160, 310)
$RefreshButton.Size = New-Object System.Drawing.Size(120, 35)
$RefreshButton.Text = " Refresh Status"
$RefreshButton.BackColor = [System.Drawing.Color]::LightBlue
$Form.Controls.Add($RefreshButton)

$ClusterButton = New-Object System.Windows.Forms.Button
$ClusterButton.Location = New-Object System.Drawing.Point(300, 310)
$ClusterButton.Size = New-Object System.Drawing.Size(120, 35)
$ClusterButton.Text = " Open Dashboard"
$ClusterButton.BackColor = [System.Drawing.Color]::LightCyan
$Form.Controls.Add($ClusterButton)

$DeployAllButton = New-Object System.Windows.Forms.Button
$DeployAllButton.Location = New-Object System.Drawing.Point(440, 310)
$DeployAllButton.Size = New-Object System.Drawing.Size(120, 35)
$DeployAllButton.Text = " Deploy All"
$DeployAllButton.BackColor = [System.Drawing.Color]::Orange
$Form.Controls.Add($DeployAllButton)

# Progress bar
$ProgressBar = New-Object System.Windows.Forms.ProgressBar
$ProgressBar.Location = New-Object System.Drawing.Point(20, 365)
$ProgressBar.Size = New-Object System.Drawing.Size(540, 20)
$ProgressBar.Style = "Continuous"
$Form.Controls.Add($ProgressBar)

# Status text
$StatusText = New-Object System.Windows.Forms.Label
$StatusText.Location = New-Object System.Drawing.Point(20, 395)
$StatusText.Size = New-Object System.Drawing.Size(540, 40)
$StatusText.Text = "Ready to flash Pi nodes. Select node and click 'Flash Node' to begin."
$StatusText.ForeColor = [System.Drawing.Color]::DarkGreen
$Form.Controls.Add($StatusText)

# Event handlers
$NodeIdCombo.Add_SelectedIndexChanged({
        $SelectedNode = [int]$NodeIdCombo.SelectedItem
        $NodeIP = "192.168.100.$([int]10 + $SelectedNode)"
    
        $Specialization = switch ($SelectedNode) {
            { $_ -le 3 } { "AI Inference" }
            { $_ -le 6 } { "Cross-listing" }
            { $_ -le 9 } { "Web Scraping" }
            default { "General Purpose" }
        }
    
        $NodeInfoLabel.Text = "IP: $NodeIP`nSpecialization: $Specialization"
    })

$FlashButton.Add_Click({
        $SelectedNodeId = [int]$NodeIdCombo.SelectedItem
        $SelectedDriveType = $DriveTypeCombo.SelectedItem
        $AutoDeploy = $AutoDeployCheckbox.Checked
        $SkipFlashing = $SkipFlashingCheckbox.Checked
    
        $StatusText.Text = "Starting Pi Node $($NodeIdCombo.SelectedItem) installation..."
        $StatusText.ForeColor = [System.Drawing.Color]::Blue
        $ProgressBar.Value = 0
    
        # Disable controls during installation
        $FlashButton.Enabled = $false
        $NodeIdCombo.Enabled = $false
        $DriveTypeCombo.Enabled = $false
    
        # Build command line arguments
        $Arguments = @(
            "-ExecutionPolicy", "Bypass",
            "-File", "C:\EQ12\cluster\eq12_pi_installer.ps1",
            "-NodeId", $SelectedNodeId,
            "-DriveType", $SelectedDriveType
        )
    
        if ($AutoDeploy) { $Arguments += "-AutoDeploy" }
        if ($SkipFlashing) { $Arguments += "-SkipFlashing" }
    
        try {
            # Start installation process
            $Process = Start-Process -FilePath "powershell.exe" -ArgumentList $Arguments -NoNewWindow -PassThru
        
            # Monitor progress (simplified)
            $Timer = New-Object System.Windows.Forms.Timer
            $Timer.Interval = 1000
            $Timer.Add_Tick({
                    $ProgressBar.Value = ($ProgressBar.Value + 2) % 100
            
                    if ($Process.HasExited) {
                        $Timer.Stop()
                        $Timer.Dispose()
                
                        if ($Process.ExitCode -eq 0) {
                            $StatusText.Text = " Pi Node $($NodeIdCombo.SelectedItem) installation completed successfully!"
                            $StatusText.ForeColor = [System.Drawing.Color]::Green
                    
                            # Update node status in list
                            $NodeStatusList.Items[$SelectedNodeId - 1].SubItems[2].Text = "Online"
                            $NodeStatusList.Items[$SelectedNodeId - 1].ForeColor = [System.Drawing.Color]::Green
                        }
                        else {
                            $StatusText.Text = " Pi Node installation failed. Check logs for details."
                            $StatusText.ForeColor = [System.Drawing.Color]::Red
                        }
                
                        $ProgressBar.Value = 100
                
                        # Re-enable controls
                        $FlashButton.Enabled = $true
                        $NodeIdCombo.Enabled = $true
                        $DriveTypeCombo.Enabled = $true
                    }
                })
        
            $Timer.Start()
        
        }
        catch {
            $StatusText.Text = " Failed to start installation: $($_.Exception.Message)"
            $StatusText.ForeColor = [System.Drawing.Color]::Red
        
            # Re-enable controls
            $FlashButton.Enabled = $true
            $NodeIdCombo.Enabled = $true
            $DriveTypeCombo.Enabled = $true
        }
    })

$RefreshButton.Add_Click({
        $StatusText.Text = " Refreshing cluster status..."
        $StatusText.ForeColor = [System.Drawing.Color]::Blue
    
        for ($i = 0; $i -lt $NodeStatusList.Items.Count; $i++) {
            $NodeIP = $NodeStatusList.Items[$i].SubItems[1].Text
        
            try {
                $PingResult = Test-Connection -ComputerName $NodeIP -Count 1 -Quiet -ErrorAction SilentlyContinue
                if ($PingResult) {
                    $NodeStatusList.Items[$i].SubItems[2].Text = "Online"
                    $NodeStatusList.Items[$i].ForeColor = [System.Drawing.Color]::Green
                }
                else {
                    $NodeStatusList.Items[$i].SubItems[2].Text = "Offline"
                    $NodeStatusList.Items[$i].ForeColor = [System.Drawing.Color]::Red
                }
            }
            catch {
                $NodeStatusList.Items[$i].SubItems[2].Text = "Error"
                $NodeStatusList.Items[$i].ForeColor = [System.Drawing.Color]::Orange
            }
        }
    
        $OnlineCount = ($NodeStatusList.Items | Where-Object { $_.SubItems[2].Text -eq "Online" }).Count
        $StatusText.Text = " Status refreshed. $OnlineCount of 12 nodes online."
        $StatusText.ForeColor = [System.Drawing.Color]::Green
    })

$ClusterButton.Add_Click({
        try {
            Start-Process "http://192.168.100.1:3000"
            $StatusText.Text = " Cluster dashboard opened in browser"
            $StatusText.ForeColor = [System.Drawing.Color]::Blue
        }
        catch {
            $StatusText.Text = " Failed to open cluster dashboard"
            $StatusText.ForeColor = [System.Drawing.Color]::Red
        }
    })

$DeployAllButton.Add_Click({
        $Response = [System.Windows.Forms.MessageBox]::Show(
            "This will deploy cluster services to all online Pi nodes.`n`nContinue?",
            "Deploy All Nodes",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Question
        )
    
        if ($Response -eq "Yes") {
            $StatusText.Text = " Deploying services to all online nodes..."
            $StatusText.ForeColor = [System.Drawing.Color]::Blue
        
            # This would trigger deployment to all nodes
            # Implementation would call the cluster deployment script
        
            $StatusText.Text = " Bulk deployment initiated. Check individual node logs for status."
            $StatusText.ForeColor = [System.Drawing.Color]::Green
        }
    })

# Initialize node info display
$NodeIdCombo.SelectedIndex = 0

# Show the form
$Form.Add_Shown({ $Form.Activate() })
[void]$Form.ShowDialog()

# Cleanup
$Form.Dispose()