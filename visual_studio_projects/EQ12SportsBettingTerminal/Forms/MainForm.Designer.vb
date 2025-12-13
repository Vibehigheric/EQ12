<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class MainForm
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()>
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(MainForm))

        ' Main Tab Control
        Me.tcMain = New System.Windows.Forms.TabControl()

        ' Odds Tab
        Me.tpOdds = New System.Windows.Forms.TabPage()
        Me.oddsDataGridView = New System.Windows.Forms.DataGridView()
        Me.btnRefreshOdds = New System.Windows.Forms.Button()
        Me.lblOddsTitle = New System.Windows.Forms.Label()
        Me.pnlOddsControls = New System.Windows.Forms.Panel()

        ' Predictions Tab
        Me.tpPredictions = New System.Windows.Forms.TabPage()
        Me.predictionsDataGridView = New System.Windows.Forms.DataGridView()
        Me.btnRunModel = New System.Windows.Forms.Button()
        Me.lblModelAccuracy = New System.Windows.Forms.Label()
        Me.pnlPredictionsControls = New System.Windows.Forms.Panel()

        ' Bankroll Tab
        Me.tpBankroll = New System.Windows.Forms.TabPage()
        Me.betsDataGridView = New System.Windows.Forms.DataGridView()
        Me.lblCurrentBankroll = New System.Windows.Forms.Label()
        Me.lblTotalProfit = New System.Windows.Forms.Label()
        Me.lblROI = New System.Windows.Forms.Label()
        Me.lblWinRate = New System.Windows.Forms.Label()
        Me.lblSharpeRatio = New System.Windows.Forms.Label()
        Me.pbBankrollGrowth = New System.Windows.Forms.ProgressBar()
        Me.pbRiskLevel = New System.Windows.Forms.ProgressBar()
        Me.pnlBankrollStats = New System.Windows.Forms.Panel()

        ' Trading Tab
        Me.tpTrading = New System.Windows.Forms.TabPage()
        Me.btnPlaceBet = New System.Windows.Forms.Button()
        Me.chkAutoBet = New System.Windows.Forms.CheckBox()
        Me.nudMaxBetSize = New System.Windows.Forms.NumericUpDown()
        Me.lblMaxBetSize = New System.Windows.Forms.Label()
        Me.tradingChart = New System.Windows.Forms.PictureBox()
        Me.pnlTradingControls = New System.Windows.Forms.Panel()

        ' Social Tab
        Me.tpSocial = New System.Windows.Forms.TabPage()
        Me.btnSendTelegramTest = New System.Windows.Forms.Button()
        Me.lstTelegramMessages = New System.Windows.Forms.ListBox()
        Me.txtTwitterStatus = New System.Windows.Forms.TextBox()
        Me.btnPostTweet = New System.Windows.Forms.Button()
        Me.lblTelegramTitle = New System.Windows.Forms.Label()
        Me.lblTwitterTitle = New System.Windows.Forms.Label()

        ' Log Tab
        Me.tpLog = New System.Windows.Forms.TabPage()
        Me.lstLog = New System.Windows.Forms.ListBox()
        Me.btnClearLog = New System.Windows.Forms.Button()
        Me.btnExportLog = New System.Windows.Forms.Button()

        ' Alerts Panel
        Me.pnlAlerts = New System.Windows.Forms.Panel()

        ' Status Strip
        Me.statusStrip = New System.Windows.Forms.StatusStrip()
        Me.toolStripStatusLabel = New System.Windows.Forms.ToolStripStatusLabel()
        Me.toolStripProgressBar = New System.Windows.Forms.ToolStripProgressBar()
        Me.toolStripConnectionStatus = New System.Windows.Forms.ToolStripStatusLabel()

        ' Menu Strip
        Me.menuStrip = New System.Windows.Forms.MenuStrip()
        Me.fileToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.exportDataToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.exitToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.toolsToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.configurationToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.aboutToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()

        ' Data Grid Columns
        Me.colGameId = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colTeams = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colSport = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colTeam1Odds = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colTeam2Odds = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colProbability = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colExpectedValue = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colArbitrage = New System.Windows.Forms.DataGridViewTextBoxColumn()

        ' Bets Grid Columns
        Me.colBetDate = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colBetGame = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colBetType = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colBetAmount = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colBetOdds = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colBetStatus = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.colBetProfit = New System.Windows.Forms.DataGridViewTextBoxColumn()

        CType(Me.oddsDataGridView, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.predictionsDataGridView, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.betsDataGridView, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.nudMaxBetSize, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.tradingChart, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.tcMain.SuspendLayout()
        Me.tpOdds.SuspendLayout()
        Me.tpPredictions.SuspendLayout()
        Me.tpBankroll.SuspendLayout()
        Me.tpTrading.SuspendLayout()
        Me.tpSocial.SuspendLayout()
        Me.tpLog.SuspendLayout()
        Me.pnlOddsControls.SuspendLayout()
        Me.pnlPredictionsControls.SuspendLayout()
        Me.pnlBankrollStats.SuspendLayout()
        Me.pnlTradingControls.SuspendLayout()
        Me.statusStrip.SuspendLayout()
        Me.menuStrip.SuspendLayout()
        Me.SuspendLayout()

        ' Main Form
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(1600, 900)
        Me.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
        Me.MinimumSize = New System.Drawing.Size(1200, 700)
        Me.Name = "MainForm"
        Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
        Me.Text = "EQ12 Sports Betting Quant Terminal v2.0"

        ' Main Tab Control
        Me.tcMain.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.tcMain.Font = New System.Drawing.Font("Segoe UI", 10.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.tcMain.Location = New System.Drawing.Point(12, 80)
        Me.tcMain.Name = "tcMain"
        Me.tcMain.SelectedIndex = 0
        Me.tcMain.Size = New System.Drawing.Size(1576, 750)
        Me.tcMain.TabIndex = 0

        ' Alerts Panel
        Me.pnlAlerts.Anchor = CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.pnlAlerts.BackColor = System.Drawing.Color.LightYellow
        Me.pnlAlerts.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.pnlAlerts.Location = New System.Drawing.Point(12, 27)
        Me.pnlAlerts.Name = "pnlAlerts"
        Me.pnlAlerts.Size = New System.Drawing.Size(1576, 50)
        Me.pnlAlerts.TabIndex = 1

        ' === ODDS TAB ===
        Me.tpOdds.Controls.Add(Me.oddsDataGridView)
        Me.tpOdds.Controls.Add(Me.pnlOddsControls)
        Me.tpOdds.Location = New System.Drawing.Point(4, 28)
        Me.tpOdds.Name = "tpOdds"
        Me.tpOdds.Padding = New System.Windows.Forms.Padding(3)
        Me.tpOdds.Size = New System.Drawing.Size(1568, 718)
        Me.tpOdds.TabIndex = 0
        Me.tpOdds.Text = "🎯 Live Odds"
        Me.tpOdds.UseVisualStyleBackColor = True

        ' Odds Controls Panel
        Me.pnlOddsControls.Controls.Add(Me.btnRefreshOdds)
        Me.pnlOddsControls.Controls.Add(Me.lblOddsTitle)
        Me.pnlOddsControls.Dock = System.Windows.Forms.DockStyle.Top
        Me.pnlOddsControls.Location = New System.Drawing.Point(3, 3)
        Me.pnlOddsControls.Name = "pnlOddsControls"
        Me.pnlOddsControls.Size = New System.Drawing.Size(1562, 50)
        Me.pnlOddsControls.TabIndex = 0

        ' Odds Title
        Me.lblOddsTitle.AutoSize = True
        Me.lblOddsTitle.Font = New System.Drawing.Font("Segoe UI", 14.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblOddsTitle.ForeColor = System.Drawing.Color.DarkBlue
        Me.lblOddsTitle.Location = New System.Drawing.Point(10, 10)
        Me.lblOddsTitle.Name = "lblOddsTitle"
        Me.lblOddsTitle.Size = New System.Drawing.Size(280, 25)
        Me.lblOddsTitle.TabIndex = 0
        Me.lblOddsTitle.Text = "🎯 Real-Time Odds Aggregation"

        ' Refresh Odds Button
        Me.btnRefreshOdds.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.btnRefreshOdds.BackColor = System.Drawing.Color.FromArgb(CType(CType(52, Byte), Integer), CType(CType(152, Byte), Integer), CType(CType(219, Byte), Integer))
        Me.btnRefreshOdds.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnRefreshOdds.ForeColor = System.Drawing.Color.White
        Me.btnRefreshOdds.Location = New System.Drawing.Point(1450, 8)
        Me.btnRefreshOdds.Name = "btnRefreshOdds"
        Me.btnRefreshOdds.Size = New System.Drawing.Size(100, 35)
        Me.btnRefreshOdds.TabIndex = 1
        Me.btnRefreshOdds.Text = "🔄 Refresh"
        Me.btnRefreshOdds.UseVisualStyleBackColor = False

        ' Odds DataGridView
        Me.oddsDataGridView.AllowUserToAddRows = False
        Me.oddsDataGridView.AllowUserToDeleteRows = False
        Me.oddsDataGridView.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.oddsDataGridView.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill
        Me.oddsDataGridView.BackgroundColor = System.Drawing.SystemColors.Window
        Me.oddsDataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.oddsDataGridView.Columns.AddRange(New System.Windows.Forms.DataGridViewColumn() {Me.colGameId, Me.colTeams, Me.colSport, Me.colTeam1Odds, Me.colTeam2Odds, Me.colProbability, Me.colExpectedValue, Me.colArbitrage})
        Me.oddsDataGridView.Location = New System.Drawing.Point(3, 56)
        Me.oddsDataGridView.MultiSelect = False
        Me.oddsDataGridView.Name = "oddsDataGridView"
        Me.oddsDataGridView.ReadOnly = True
        Me.oddsDataGridView.RowHeadersWidth = 51
        Me.oddsDataGridView.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect
        Me.oddsDataGridView.Size = New System.Drawing.Size(1562, 659)
        Me.oddsDataGridView.TabIndex = 1

        ' === PREDICTIONS TAB ===
        Me.tpPredictions.Controls.Add(Me.predictionsDataGridView)
        Me.tpPredictions.Controls.Add(Me.pnlPredictionsControls)
        Me.tpPredictions.Location = New System.Drawing.Point(4, 28)
        Me.tpPredictions.Name = "tpPredictions"
        Me.tpPredictions.Padding = New System.Windows.Forms.Padding(3)
        Me.tpPredictions.Size = New System.Drawing.Size(1568, 718)
        Me.tpPredictions.TabIndex = 1
        Me.tpPredictions.Text = "🧠 AI Predictions"
        Me.tpPredictions.UseVisualStyleBackColor = True

        ' Predictions Controls Panel
        Me.pnlPredictionsControls.Controls.Add(Me.btnRunModel)
        Me.pnlPredictionsControls.Controls.Add(Me.lblModelAccuracy)
        Me.pnlPredictionsControls.Dock = System.Windows.Forms.DockStyle.Top
        Me.pnlPredictionsControls.Location = New System.Drawing.Point(3, 3)
        Me.pnlPredictionsControls.Name = "pnlPredictionsControls"
        Me.pnlPredictionsControls.Size = New System.Drawing.Size(1562, 50)
        Me.pnlPredictionsControls.TabIndex = 0

        ' Model Accuracy Label
        Me.lblModelAccuracy.AutoSize = True
        Me.lblModelAccuracy.Font = New System.Drawing.Font("Segoe UI", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblModelAccuracy.ForeColor = System.Drawing.Color.Green
        Me.lblModelAccuracy.Location = New System.Drawing.Point(10, 15)
        Me.lblModelAccuracy.Name = "lblModelAccuracy"
        Me.lblModelAccuracy.Size = New System.Drawing.Size(180, 21)
        Me.lblModelAccuracy.TabIndex = 0
        Me.lblModelAccuracy.Text = "Model Accuracy: 78.5%"

        ' Run Model Button
        Me.btnRunModel.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.btnRunModel.BackColor = System.Drawing.Color.FromArgb(CType(CType(46, Byte), Integer), CType(CType(125, Byte), Integer), CType(CType(50, Byte), Integer))
        Me.btnRunModel.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnRunModel.ForeColor = System.Drawing.Color.White
        Me.btnRunModel.Location = New System.Drawing.Point(1420, 8)
        Me.btnRunModel.Name = "btnRunModel"
        Me.btnRunModel.Size = New System.Drawing.Size(130, 35)
        Me.btnRunModel.TabIndex = 1
        Me.btnRunModel.Text = "🧠 Run Model"
        Me.btnRunModel.UseVisualStyleBackColor = False

        ' Predictions DataGridView
        Me.predictionsDataGridView.AllowUserToAddRows = False
        Me.predictionsDataGridView.AllowUserToDeleteRows = False
        Me.predictionsDataGridView.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.predictionsDataGridView.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill
        Me.predictionsDataGridView.BackgroundColor = System.Drawing.SystemColors.Window
        Me.predictionsDataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.predictionsDataGridView.Location = New System.Drawing.Point(3, 56)
        Me.predictionsDataGridView.Name = "predictionsDataGridView"
        Me.predictionsDataGridView.ReadOnly = True
        Me.predictionsDataGridView.RowHeadersWidth = 51
        Me.predictionsDataGridView.Size = New System.Drawing.Size(1562, 659)
        Me.predictionsDataGridView.TabIndex = 1

        ' === BANKROLL TAB ===
        Me.tpBankroll.Controls.Add(Me.betsDataGridView)
        Me.tpBankroll.Controls.Add(Me.pnlBankrollStats)
        Me.tpBankroll.Location = New System.Drawing.Point(4, 28)
        Me.tpBankroll.Name = "tpBankroll"
        Me.tpBankroll.Padding = New System.Windows.Forms.Padding(3)
        Me.tpBankroll.Size = New System.Drawing.Size(1568, 718)
        Me.tpBankroll.TabIndex = 2
        Me.tpBankroll.Text = "💰 Bankroll"
        Me.tpBankroll.UseVisualStyleBackColor = True

        ' Bankroll Stats Panel
        Me.pnlBankrollStats.Controls.Add(Me.lblCurrentBankroll)
        Me.pnlBankrollStats.Controls.Add(Me.lblTotalProfit)
        Me.pnlBankrollStats.Controls.Add(Me.lblROI)
        Me.pnlBankrollStats.Controls.Add(Me.lblWinRate)
        Me.pnlBankrollStats.Controls.Add(Me.lblSharpeRatio)
        Me.pnlBankrollStats.Controls.Add(Me.pbBankrollGrowth)
        Me.pnlBankrollStats.Controls.Add(Me.pbRiskLevel)
        Me.pnlBankrollStats.Dock = System.Windows.Forms.DockStyle.Top
        Me.pnlBankrollStats.Location = New System.Drawing.Point(3, 3)
        Me.pnlBankrollStats.Name = "pnlBankrollStats"
        Me.pnlBankrollStats.Size = New System.Drawing.Size(1562, 120)
        Me.pnlBankrollStats.TabIndex = 0

        ' Current Bankroll
        Me.lblCurrentBankroll.AutoSize = True
        Me.lblCurrentBankroll.Font = New System.Drawing.Font("Segoe UI", 16.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblCurrentBankroll.ForeColor = System.Drawing.Color.DarkGreen
        Me.lblCurrentBankroll.Location = New System.Drawing.Point(10, 10)
        Me.lblCurrentBankroll.Name = "lblCurrentBankroll"
        Me.lblCurrentBankroll.Size = New System.Drawing.Size(70, 30)
        Me.lblCurrentBankroll.TabIndex = 0
        Me.lblCurrentBankroll.Text = "$0.00"

        ' Total Profit
        Me.lblTotalProfit.AutoSize = True
        Me.lblTotalProfit.Font = New System.Drawing.Font("Segoe UI", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblTotalProfit.Location = New System.Drawing.Point(200, 15)
        Me.lblTotalProfit.Name = "lblTotalProfit"
        Me.lblTotalProfit.Size = New System.Drawing.Size(50, 21)
        Me.lblTotalProfit.TabIndex = 1
        Me.lblTotalProfit.Text = "$0.00"

        ' ROI
        Me.lblROI.AutoSize = True
        Me.lblROI.Font = New System.Drawing.Font("Segoe UI", 11.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblROI.Location = New System.Drawing.Point(10, 50)
        Me.lblROI.Name = "lblROI"
        Me.lblROI.Size = New System.Drawing.Size(70, 20)
        Me.lblROI.TabIndex = 2
        Me.lblROI.Text = "ROI: 0.0%"

        ' Win Rate
        Me.lblWinRate.AutoSize = True
        Me.lblWinRate.Font = New System.Drawing.Font("Segoe UI", 11.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblWinRate.Location = New System.Drawing.Point(120, 50)
        Me.lblWinRate.Name = "lblWinRate"
        Me.lblWinRate.Size = New System.Drawing.Size(100, 20)
        Me.lblWinRate.TabIndex = 3
        Me.lblWinRate.Text = "Win Rate: 0%"

        ' Sharpe Ratio
        Me.lblSharpeRatio.AutoSize = True
        Me.lblSharpeRatio.Font = New System.Drawing.Font("Segoe UI", 11.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblSharpeRatio.Location = New System.Drawing.Point(250, 50)
        Me.lblSharpeRatio.Name = "lblSharpeRatio"
        Me.lblSharpeRatio.Size = New System.Drawing.Size(110, 20)
        Me.lblSharpeRatio.TabIndex = 4
        Me.lblSharpeRatio.Text = "Sharpe Ratio: 0"

        ' Bankroll Growth Progress Bar
        Me.pbBankrollGrowth.Anchor = CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.pbBankrollGrowth.Location = New System.Drawing.Point(10, 80)
        Me.pbBankrollGrowth.Name = "pbBankrollGrowth"
        Me.pbBankrollGrowth.Size = New System.Drawing.Size(760, 15)
        Me.pbBankrollGrowth.TabIndex = 5
        Me.pbBankrollGrowth.Value = 50

        ' Risk Level Progress Bar
        Me.pbRiskLevel.Anchor = CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.pbRiskLevel.Location = New System.Drawing.Point(780, 80)
        Me.pbRiskLevel.Name = "pbRiskLevel"
        Me.pbRiskLevel.Size = New System.Drawing.Size(760, 15)
        Me.pbRiskLevel.TabIndex = 6
        Me.pbRiskLevel.Value = 25

        ' Bets DataGridView
        Me.betsDataGridView.AllowUserToAddRows = False
        Me.betsDataGridView.AllowUserToDeleteRows = False
        Me.betsDataGridView.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.betsDataGridView.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill
        Me.betsDataGridView.BackgroundColor = System.Drawing.SystemColors.Window
        Me.betsDataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.betsDataGridView.Columns.AddRange(New System.Windows.Forms.DataGridViewColumn() {Me.colBetDate, Me.colBetGame, Me.colBetType, Me.colBetAmount, Me.colBetOdds, Me.colBetStatus, Me.colBetProfit})
        Me.betsDataGridView.Location = New System.Drawing.Point(3, 126)
        Me.betsDataGridView.Name = "betsDataGridView"
        Me.betsDataGridView.ReadOnly = True
        Me.betsDataGridView.RowHeadersWidth = 51
        Me.betsDataGridView.Size = New System.Drawing.Size(1562, 589)
        Me.betsDataGridView.TabIndex = 1

        ' === TRADING TAB ===
        Me.tpTrading.Controls.Add(Me.tradingChart)
        Me.tpTrading.Controls.Add(Me.pnlTradingControls)
        Me.tpTrading.Location = New System.Drawing.Point(4, 28)
        Me.tpTrading.Name = "tpTrading"
        Me.tpTrading.Size = New System.Drawing.Size(1568, 718)
        Me.tpTrading.TabIndex = 3
        Me.tpTrading.Text = "📈 Trading Bot"
        Me.tpTrading.UseVisualStyleBackColor = True

        ' Trading Controls Panel
        Me.pnlTradingControls.Controls.Add(Me.btnPlaceBet)
        Me.pnlTradingControls.Controls.Add(Me.chkAutoBet)
        Me.pnlTradingControls.Controls.Add(Me.nudMaxBetSize)
        Me.pnlTradingControls.Controls.Add(Me.lblMaxBetSize)
        Me.pnlTradingControls.Dock = System.Windows.Forms.DockStyle.Top
        Me.pnlTradingControls.Location = New System.Drawing.Point(0, 0)
        Me.pnlTradingControls.Name = "pnlTradingControls"
        Me.pnlTradingControls.Size = New System.Drawing.Size(1568, 60)
        Me.pnlTradingControls.TabIndex = 0

        ' Place Bet Button
        Me.btnPlaceBet.BackColor = System.Drawing.Color.FromArgb(CType(CType(220, Byte), Integer), CType(CType(53, Byte), Integer), CType(CType(69, Byte), Integer))
        Me.btnPlaceBet.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnPlaceBet.Font = New System.Drawing.Font("Segoe UI", 10.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnPlaceBet.ForeColor = System.Drawing.Color.White
        Me.btnPlaceBet.Location = New System.Drawing.Point(10, 10)
        Me.btnPlaceBet.Name = "btnPlaceBet"
        Me.btnPlaceBet.Size = New System.Drawing.Size(120, 40)
        Me.btnPlaceBet.TabIndex = 0
        Me.btnPlaceBet.Text = "💰 Place Bet"
        Me.btnPlaceBet.UseVisualStyleBackColor = False

        ' Auto Bet Checkbox
        Me.chkAutoBet.AutoSize = True
        Me.chkAutoBet.Font = New System.Drawing.Font("Segoe UI", 10.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.chkAutoBet.Location = New System.Drawing.Point(150, 20)
        Me.chkAutoBet.Name = "chkAutoBet"
        Me.chkAutoBet.Size = New System.Drawing.Size(145, 23)
        Me.chkAutoBet.TabIndex = 1
        Me.chkAutoBet.Text = "🤖 Auto-Betting ON"
        Me.chkAutoBet.UseVisualStyleBackColor = True

        ' Max Bet Size Label
        Me.lblMaxBetSize.AutoSize = True
        Me.lblMaxBetSize.Font = New System.Drawing.Font("Segoe UI", 10.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblMaxBetSize.Location = New System.Drawing.Point(320, 22)
        Me.lblMaxBetSize.Name = "lblMaxBetSize"
        Me.lblMaxBetSize.Size = New System.Drawing.Size(95, 19)
        Me.lblMaxBetSize.TabIndex = 2
        Me.lblMaxBetSize.Text = "Max Bet Size:"

        ' Max Bet Size Numeric UpDown
        Me.nudMaxBetSize.DecimalPlaces = 2
        Me.nudMaxBetSize.Font = New System.Drawing.Font("Segoe UI", 10.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.nudMaxBetSize.Location = New System.Drawing.Point(420, 20)
        Me.nudMaxBetSize.Maximum = New Decimal(New Integer() {10000, 0, 0, 0})
        Me.nudMaxBetSize.Minimum = New Decimal(New Integer() {1, 0, 0, 0})
        Me.nudMaxBetSize.Name = "nudMaxBetSize"
        Me.nudMaxBetSize.Size = New System.Drawing.Size(100, 25)
        Me.nudMaxBetSize.TabIndex = 3
        Me.nudMaxBetSize.Value = New Decimal(New Integer() {100, 0, 0, 0})

        ' Trading Chart PictureBox
        Me.tradingChart.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.tradingChart.BackColor = System.Drawing.SystemColors.Window
        Me.tradingChart.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.tradingChart.Location = New System.Drawing.Point(0, 63)
        Me.tradingChart.Name = "tradingChart"
        Me.tradingChart.Size = New System.Drawing.Size(1568, 655)
        Me.tradingChart.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom
        Me.tradingChart.TabIndex = 1
        Me.tradingChart.TabStop = False

        ' === SOCIAL TAB ===
        Me.tpSocial.Controls.Add(Me.btnSendTelegramTest)
        Me.tpSocial.Controls.Add(Me.lstTelegramMessages)
        Me.tpSocial.Controls.Add(Me.txtTwitterStatus)
        Me.tpSocial.Controls.Add(Me.btnPostTweet)
        Me.tpSocial.Controls.Add(Me.lblTelegramTitle)
        Me.tpSocial.Controls.Add(Me.lblTwitterTitle)
        Me.tpSocial.Location = New System.Drawing.Point(4, 28)
        Me.tpSocial.Name = "tpSocial"
        Me.tpSocial.Size = New System.Drawing.Size(1568, 718)
        Me.tpSocial.TabIndex = 4
        Me.tpSocial.Text = "📱 Social Media"
        Me.tpSocial.UseVisualStyleBackColor = True

        ' Telegram Title
        Me.lblTelegramTitle.AutoSize = True
        Me.lblTelegramTitle.Font = New System.Drawing.Font("Segoe UI", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblTelegramTitle.Location = New System.Drawing.Point(10, 10)
        Me.lblTelegramTitle.Name = "lblTelegramTitle"
        Me.lblTelegramTitle.Size = New System.Drawing.Size(140, 21)
        Me.lblTelegramTitle.TabIndex = 0
        Me.lblTelegramTitle.Text = "📞 Telegram Bot"

        ' Send Telegram Test Button
        Me.btnSendTelegramTest.BackColor = System.Drawing.Color.FromArgb(CType(CType(0, Byte), Integer), CType(CType(136, Byte), Integer), CType(CType(204, Byte), Integer))
        Me.btnSendTelegramTest.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnSendTelegramTest.ForeColor = System.Drawing.Color.White
        Me.btnSendTelegramTest.Location = New System.Drawing.Point(200, 8)
        Me.btnSendTelegramTest.Name = "btnSendTelegramTest"
        Me.btnSendTelegramTest.Size = New System.Drawing.Size(100, 28)
        Me.btnSendTelegramTest.TabIndex = 1
        Me.btnSendTelegramTest.Text = "Send Test"
        Me.btnSendTelegramTest.UseVisualStyleBackColor = False

        ' Telegram Messages ListBox
        Me.lstTelegramMessages.Anchor = CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.lstTelegramMessages.Font = New System.Drawing.Font("Consolas", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lstTelegramMessages.Location = New System.Drawing.Point(10, 40)
        Me.lstTelegramMessages.Name = "lstTelegramMessages"
        Me.lstTelegramMessages.Size = New System.Drawing.Size(1550, 200)
        Me.lstTelegramMessages.TabIndex = 2

        ' Twitter Title
        Me.lblTwitterTitle.AutoSize = True
        Me.lblTwitterTitle.Font = New System.Drawing.Font("Segoe UI", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblTwitterTitle.Location = New System.Drawing.Point(10, 260)
        Me.lblTwitterTitle.Name = "lblTwitterTitle"
        Me.lblTwitterTitle.Size = New System.Drawing.Size(102, 21)
        Me.lblTwitterTitle.TabIndex = 3
        Me.lblTwitterTitle.Text = "🐦 Twitter/X"

        ' Twitter Status TextBox
        Me.txtTwitterStatus.Anchor = CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.txtTwitterStatus.Font = New System.Drawing.Font("Segoe UI", 10.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtTwitterStatus.Location = New System.Drawing.Point(10, 290)
        Me.txtTwitterStatus.Multiline = True
        Me.txtTwitterStatus.Name = "txtTwitterStatus"
        Me.txtTwitterStatus.PlaceholderText = "Enter your tweet here..."
        Me.txtTwitterStatus.Size = New System.Drawing.Size(1400, 80)
        Me.txtTwitterStatus.TabIndex = 4

        ' Post Tweet Button
        Me.btnPostTweet.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.btnPostTweet.BackColor = System.Drawing.Color.FromArgb(CType(CType(29, Byte), Integer), CType(CType(161, Byte), Integer), CType(CType(242, Byte), Integer))
        Me.btnPostTweet.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnPostTweet.ForeColor = System.Drawing.Color.White
        Me.btnPostTweet.Location = New System.Drawing.Point(1420, 290)
        Me.btnPostTweet.Name = "btnPostTweet"
        Me.btnPostTweet.Size = New System.Drawing.Size(140, 35)
        Me.btnPostTweet.TabIndex = 5
        Me.btnPostTweet.Text = "🚀 Post Tweet"
        Me.btnPostTweet.UseVisualStyleBackColor = False

        ' === LOG TAB ===
        Me.tpLog.Controls.Add(Me.lstLog)
        Me.tpLog.Controls.Add(Me.btnClearLog)
        Me.tpLog.Controls.Add(Me.btnExportLog)
        Me.tpLog.Location = New System.Drawing.Point(4, 28)
        Me.tpLog.Name = "tpLog"
        Me.tpLog.Size = New System.Drawing.Size(1568, 718)
        Me.tpLog.TabIndex = 5
        Me.tpLog.Text = "📋 System Log"
        Me.tpLog.UseVisualStyleBackColor = True

        ' Log ListBox
        Me.lstLog.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
            Or System.Windows.Forms.AnchorStyles.Left) _
            Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.lstLog.Font = New System.Drawing.Font("Consolas", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lstLog.Location = New System.Drawing.Point(0, 40)
        Me.lstLog.Name = "lstLog"
        Me.lstLog.Size = New System.Drawing.Size(1568, 678)
        Me.lstLog.TabIndex = 0

        ' Clear Log Button
        Me.btnClearLog.BackColor = System.Drawing.Color.FromArgb(CType(CType(220, Byte), Integer), CType(CType(53, Byte), Integer), CType(CType(69, Byte), Integer))
        Me.btnClearLog.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnClearLog.ForeColor = System.Drawing.Color.White
        Me.btnClearLog.Location = New System.Drawing.Point(10, 8)
        Me.btnClearLog.Name = "btnClearLog"
        Me.btnClearLog.Size = New System.Drawing.Size(80, 28)
        Me.btnClearLog.TabIndex = 1
        Me.btnClearLog.Text = "Clear"
        Me.btnClearLog.UseVisualStyleBackColor = False

        ' Export Log Button
        Me.btnExportLog.BackColor = System.Drawing.Color.FromArgb(CType(CType(40, Byte), Integer), CType(CType(167, Byte), Integer), CType(CType(69, Byte), Integer))
        Me.btnExportLog.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnExportLog.ForeColor = System.Drawing.Color.White
        Me.btnExportLog.Location = New System.Drawing.Point(100, 8)
        Me.btnExportLog.Name = "btnExportLog"
        Me.btnExportLog.Size = New System.Drawing.Size(80, 28)
        Me.btnExportLog.TabIndex = 2
        Me.btnExportLog.Text = "Export"
        Me.btnExportLog.UseVisualStyleBackColor = False

        ' === DATA GRID COLUMNS ===
        ' Odds Grid Columns
        Me.colGameId.HeaderText = "Game ID"
        Me.colGameId.Name = "colGameId"
        Me.colGameId.ReadOnly = True
        Me.colGameId.Width = 100

        Me.colTeams.HeaderText = "Teams"
        Me.colTeams.Name = "colTeams"
        Me.colTeams.ReadOnly = True
        Me.colTeams.Width = 250

        Me.colSport.HeaderText = "Sport"
        Me.colSport.Name = "colSport"
        Me.colSport.ReadOnly = True
        Me.colSport.Width = 100

        Me.colTeam1Odds.HeaderText = "Team 1 Odds"
        Me.colTeam1Odds.Name = "colTeam1Odds"
        Me.colTeam1Odds.ReadOnly = True
        Me.colTeam1Odds.Width = 120

        Me.colTeam2Odds.HeaderText = "Team 2 Odds"
        Me.colTeam2Odds.Name = "colTeam2Odds"
        Me.colTeam2Odds.ReadOnly = True
        Me.colTeam2Odds.Width = 120

        Me.colProbability.HeaderText = "Win Probability"
        Me.colProbability.Name = "colProbability"
        Me.colProbability.ReadOnly = True
        Me.colProbability.Width = 130

        Me.colExpectedValue.HeaderText = "Expected Value"
        Me.colExpectedValue.Name = "colExpectedValue"
        Me.colExpectedValue.ReadOnly = True
        Me.colExpectedValue.Width = 130

        Me.colArbitrage.HeaderText = "Arbitrage %"
        Me.colArbitrage.Name = "colArbitrage"
        Me.colArbitrage.ReadOnly = True
        Me.colArbitrage.Width = 100

        ' Bets Grid Columns
        Me.colBetDate.HeaderText = "Date"
        Me.colBetDate.Name = "colBetDate"
        Me.colBetDate.ReadOnly = True
        Me.colBetDate.Width = 120

        Me.colBetGame.HeaderText = "Game"
        Me.colBetGame.Name = "colBetGame"
        Me.colBetGame.ReadOnly = True
        Me.colBetGame.Width = 200

        Me.colBetType.HeaderText = "Bet Type"
        Me.colBetType.Name = "colBetType"
        Me.colBetType.ReadOnly = True
        Me.colBetType.Width = 100

        Me.colBetAmount.HeaderText = "Amount"
        Me.colBetAmount.Name = "colBetAmount"
        Me.colBetAmount.ReadOnly = True
        Me.colBetAmount.Width = 100

        Me.colBetOdds.HeaderText = "Odds"
        Me.colBetOdds.Name = "colBetOdds"
        Me.colBetOdds.ReadOnly = True
        Me.colBetOdds.Width = 80

        Me.colBetStatus.HeaderText = "Status"
        Me.colBetStatus.Name = "colBetStatus"
        Me.colBetStatus.ReadOnly = True
        Me.colBetStatus.Width = 80

        Me.colBetProfit.HeaderText = "Profit/Loss"
        Me.colBetProfit.Name = "colBetProfit"
        Me.colBetProfit.ReadOnly = True
        Me.colBetProfit.Width = 100

        ' === STATUS STRIP ===
        Me.statusStrip.ImageScalingSize = New System.Drawing.Size(20, 20)
        Me.statusStrip.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.toolStripStatusLabel, Me.toolStripProgressBar, Me.toolStripConnectionStatus})
        Me.statusStrip.Location = New System.Drawing.Point(0, 836)
        Me.statusStrip.Name = "statusStrip"
        Me.statusStrip.Size = New System.Drawing.Size(1600, 26)
        Me.statusStrip.TabIndex = 2
        Me.statusStrip.Text = "StatusStrip1"

        Me.toolStripStatusLabel.Name = "toolStripStatusLabel"
        Me.toolStripStatusLabel.Size = New System.Drawing.Size(200, 20)
        Me.toolStripStatusLabel.Text = "EQ12 Terminal Ready"

        Me.toolStripProgressBar.Name = "toolStripProgressBar"
        Me.toolStripProgressBar.Size = New System.Drawing.Size(100, 18)

        Me.toolStripConnectionStatus.Name = "toolStripConnectionStatus"
        Me.toolStripConnectionStatus.Size = New System.Drawing.Size(150, 20)
        Me.toolStripConnectionStatus.Text = "🟢 All Services Connected"

        ' === MENU STRIP ===
        Me.menuStrip.ImageScalingSize = New System.Drawing.Size(20, 20)
        Me.menuStrip.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.fileToolStripMenuItem, Me.toolsToolStripMenuItem, Me.aboutToolStripMenuItem})
        Me.menuStrip.Location = New System.Drawing.Point(0, 0)
        Me.menuStrip.Name = "menuStrip"
        Me.menuStrip.Size = New System.Drawing.Size(1600, 28)
        Me.menuStrip.TabIndex = 3
        Me.menuStrip.Text = "MenuStrip1"

        Me.fileToolStripMenuItem.DropDownItems.AddRange(New System.Windows.Forms.ToolStripItem() {Me.exportDataToolStripMenuItem, Me.exitToolStripMenuItem})
        Me.fileToolStripMenuItem.Name = "fileToolStripMenuItem"
        Me.fileToolStripMenuItem.Size = New System.Drawing.Size(46, 24)
        Me.fileToolStripMenuItem.Text = "&File"

        Me.exportDataToolStripMenuItem.Name = "exportDataToolStripMenuItem"
        Me.exportDataToolStripMenuItem.Size = New System.Drawing.Size(165, 26)
        Me.exportDataToolStripMenuItem.Text = "&Export Data..."

        Me.exitToolStripMenuItem.Name = "exitToolStripMenuItem"
        Me.exitToolStripMenuItem.Size = New System.Drawing.Size(165, 26)
        Me.exitToolStripMenuItem.Text = "E&xit"

        Me.toolsToolStripMenuItem.DropDownItems.AddRange(New System.Windows.Forms.ToolStripItem() {Me.configurationToolStripMenuItem})
        Me.toolsToolStripMenuItem.Name = "toolsToolStripMenuItem"
        Me.toolsToolStripMenuItem.Size = New System.Drawing.Size(58, 24)
        Me.toolsToolStripMenuItem.Text = "&Tools"

        Me.configurationToolStripMenuItem.Name = "configurationToolStripMenuItem"
        Me.configurationToolStripMenuItem.Size = New System.Drawing.Size(179, 26)
        Me.configurationToolStripMenuItem.Text = "&Configuration..."

        Me.aboutToolStripMenuItem.Name = "aboutToolStripMenuItem"
        Me.aboutToolStripMenuItem.Size = New System.Drawing.Size(64, 24)
        Me.aboutToolStripMenuItem.Text = "&About"

        ' Add tab pages to main tab control
        Me.tcMain.Controls.Add(Me.tpOdds)
        Me.tcMain.Controls.Add(Me.tpPredictions)
        Me.tcMain.Controls.Add(Me.tpBankroll)
        Me.tcMain.Controls.Add(Me.tpTrading)
        Me.tcMain.Controls.Add(Me.tpSocial)
        Me.tcMain.Controls.Add(Me.tpLog)

        ' Add main controls to form
        Me.Controls.Add(Me.tcMain)
        Me.Controls.Add(Me.pnlAlerts)
        Me.Controls.Add(Me.statusStrip)
        Me.Controls.Add(Me.menuStrip)
        Me.MainMenuStrip = Me.menuStrip

        CType(Me.oddsDataGridView, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.predictionsDataGridView, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.betsDataGridView, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.nudMaxBetSize, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.tradingChart, System.ComponentModel.ISupportInitialize).EndInit()
        Me.tcMain.ResumeLayout(False)
        Me.tpOdds.ResumeLayout(False)
        Me.tpPredictions.ResumeLayout(False)
        Me.tpBankroll.ResumeLayout(False)
        Me.tpTrading.ResumeLayout(False)
        Me.tpSocial.ResumeLayout(False)
        Me.tpSocial.PerformLayout()
        Me.tpLog.ResumeLayout(False)
        Me.pnlOddsControls.ResumeLayout(False)
        Me.pnlOddsControls.PerformLayout()
        Me.pnlPredictionsControls.ResumeLayout(False)
        Me.pnlPredictionsControls.PerformLayout()
        Me.pnlBankrollStats.ResumeLayout(False)
        Me.pnlBankrollStats.PerformLayout()
        Me.pnlTradingControls.ResumeLayout(False)
        Me.pnlTradingControls.PerformLayout()
        Me.statusStrip.ResumeLayout(False)
        Me.statusStrip.PerformLayout()
        Me.menuStrip.ResumeLayout(False)
        Me.menuStrip.PerformLayout()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    ' Form Controls
    Friend WithEvents tcMain As TabControl
    Friend WithEvents tpOdds As TabPage
    Friend WithEvents tpPredictions As TabPage
    Friend WithEvents tpBankroll As TabPage
    Friend WithEvents tpTrading As TabPage
    Friend WithEvents tpSocial As TabPage
    Friend WithEvents tpLog As TabPage

    ' Odds Tab Controls
    Friend WithEvents oddsDataGridView As DataGridView
    Friend WithEvents btnRefreshOdds As Button
    Friend WithEvents lblOddsTitle As Label
    Friend WithEvents pnlOddsControls As Panel

    ' Predictions Tab Controls
    Friend WithEvents predictionsDataGridView As DataGridView
    Friend WithEvents btnRunModel As Button
    Friend WithEvents lblModelAccuracy As Label
    Friend WithEvents pnlPredictionsControls As Panel

    ' Bankroll Tab Controls
    Friend WithEvents betsDataGridView As DataGridView
    Friend WithEvents lblCurrentBankroll As Label
    Friend WithEvents lblTotalProfit As Label
    Friend WithEvents lblROI As Label
    Friend WithEvents lblWinRate As Label
    Friend WithEvents lblSharpeRatio As Label
    Friend WithEvents pbBankrollGrowth As ProgressBar
    Friend WithEvents pbRiskLevel As ProgressBar
    Friend WithEvents pnlBankrollStats As Panel

    ' Trading Tab Controls
    Friend WithEvents btnPlaceBet As Button
    Friend WithEvents chkAutoBet As CheckBox
    Friend WithEvents nudMaxBetSize As NumericUpDown
    Friend WithEvents lblMaxBetSize As Label
    Friend WithEvents tradingChart As PictureBox
    Friend WithEvents pnlTradingControls As Panel

    ' Social Tab Controls
    Friend WithEvents btnSendTelegramTest As Button
    Friend WithEvents lstTelegramMessages As ListBox
    Friend WithEvents txtTwitterStatus As TextBox
    Friend WithEvents btnPostTweet As Button
    Friend WithEvents lblTelegramTitle As Label
    Friend WithEvents lblTwitterTitle As Label

    ' Log Tab Controls
    Friend WithEvents lstLog As ListBox
    Friend WithEvents btnClearLog As Button
    Friend WithEvents btnExportLog As Button

    ' Common Controls
    Friend WithEvents pnlAlerts As Panel
    Friend WithEvents statusStrip As StatusStrip
    Friend WithEvents toolStripStatusLabel As ToolStripStatusLabel
    Friend WithEvents toolStripProgressBar As ToolStripProgressBar
    Friend WithEvents toolStripConnectionStatus As ToolStripStatusLabel
    Friend WithEvents menuStrip As MenuStrip
    Friend WithEvents fileToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents exportDataToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents exitToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents toolsToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents configurationToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents aboutToolStripMenuItem As ToolStripMenuItem

    ' Data Grid Columns
    Friend WithEvents colGameId As DataGridViewTextBoxColumn
    Friend WithEvents colTeams As DataGridViewTextBoxColumn
    Friend WithEvents colSport As DataGridViewTextBoxColumn
    Friend WithEvents colTeam1Odds As DataGridViewTextBoxColumn
    Friend WithEvents colTeam2Odds As DataGridViewTextBoxColumn
    Friend WithEvents colProbability As DataGridViewTextBoxColumn
    Friend WithEvents colExpectedValue As DataGridViewTextBoxColumn
    Friend WithEvents colArbitrage As DataGridViewTextBoxColumn

    Friend WithEvents colBetDate As DataGridViewTextBoxColumn
    Friend WithEvents colBetGame As DataGridViewTextBoxColumn
    Friend WithEvents colBetType As DataGridViewTextBoxColumn
    Friend WithEvents colBetAmount As DataGridViewTextBoxColumn
    Friend WithEvents colBetOdds As DataGridViewTextBoxColumn
    Friend WithEvents colBetStatus As DataGridViewTextBoxColumn
    Friend WithEvents colBetProfit As DataGridViewTextBoxColumn

End Class
