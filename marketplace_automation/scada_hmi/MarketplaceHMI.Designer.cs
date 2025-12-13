using System;

namespace EQ12.MarketplaceSCADA
{
    partial class MarketplaceHMI
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.mainTableLayout = new System.Windows.Forms.TableLayoutPanel();
            this.headerPanel = new System.Windows.Forms.Panel();
            this.lblTitle = new System.Windows.Forms.Label();
            this.lblSystemTime = new System.Windows.Forms.Label();
            this.lblOPCStatus = new System.Windows.Forms.Label();
            this.statusPanel = new System.Windows.Forms.Panel();
            this.lblSystemHealth = new System.Windows.Forms.Label();
            this.lblMemoryUsage = new System.Windows.Forms.Label();
            this.lblEQ12Components = new System.Windows.Forms.Label();
            this.metricsPanel = new System.Windows.Forms.Panel();
            this.lblTotalListings = new System.Windows.Forms.Label();
            this.lblTotalSales = new System.Windows.Forms.Label();
            this.lblAutomationStatus = new System.Windows.Forms.Label();
            this.marketplacesPanel = new System.Windows.Forms.Panel();
            this.ebayGroupBox = new System.Windows.Forms.GroupBox();
            this.lblEBayStatus = new System.Windows.Forms.Label();
            this.lblEBayListings = new System.Windows.Forms.Label();
            this.lblEBaySales = new System.Windows.Forms.Label();
            this.lblEBayConversion = new System.Windows.Forms.Label();
            this.facebookGroupBox = new System.Windows.Forms.GroupBox();
            this.lblFacebookStatus = new System.Windows.Forms.Label();
            this.lblFacebookListings = new System.Windows.Forms.Label();
            this.lblFacebookSales = new System.Windows.Forms.Label();
            this.lblFacebookConversion = new System.Windows.Forms.Label();
            this.mercariGroupBox = new System.Windows.Forms.GroupBox();
            this.lblMercariStatus = new System.Windows.Forms.Label();
            this.lblMercariListings = new System.Windows.Forms.Label();
            this.lblMercariSales = new System.Windows.Forms.Label();
            this.lblMercariConversion = new System.Windows.Forms.Label();
            this.controlPanel = new System.Windows.Forms.Panel();
            this.btnStartAutomation = new System.Windows.Forms.Button();
            this.btnStopAutomation = new System.Windows.Forms.Button();
            this.btnGenerateProducts = new System.Windows.Forms.Button();
            this.btnConnectOPC = new System.Windows.Forms.Button();
            this.btnEmergencyStop = new System.Windows.Forms.Button();
            this.chartsPanel = new System.Windows.Forms.Panel();
            this.revenueChart = new LiveCharts.WinForms.CartesianChart();
            this.listingsChart = new LiveCharts.WinForms.CartesianChart();
            this.consolePanel = new System.Windows.Forms.Panel();
            this.txtConsoleLog = new System.Windows.Forms.TextBox();
            this.lblConsoleTitle = new System.Windows.Forms.Label();
            this.updateTimer = new System.Windows.Forms.Timer(this.components);
            this.mainTableLayout.SuspendLayout();
            this.headerPanel.SuspendLayout();
            this.statusPanel.SuspendLayout();
            this.metricsPanel.SuspendLayout();
            this.marketplacesPanel.SuspendLayout();
            this.ebayGroupBox.SuspendLayout();
            this.facebookGroupBox.SuspendLayout();
            this.mercariGroupBox.SuspendLayout();
            this.controlPanel.SuspendLayout();
            this.chartsPanel.SuspendLayout();
            this.consolePanel.SuspendLayout();
            this.SuspendLayout();
            // 
            // mainTableLayout
            // 
            this.mainTableLayout.ColumnCount = 3;
            this.mainTableLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 30F));
            this.mainTableLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 40F));
            this.mainTableLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 30F));
            this.mainTableLayout.Controls.Add(this.headerPanel, 0, 0);
            this.mainTableLayout.Controls.Add(this.statusPanel, 0, 1);
            this.mainTableLayout.Controls.Add(this.metricsPanel, 1, 1);
            this.mainTableLayout.Controls.Add(this.marketplacesPanel, 2, 1);
            this.mainTableLayout.Controls.Add(this.controlPanel, 0, 2);
            this.mainTableLayout.Controls.Add(this.chartsPanel, 1, 2);
            this.mainTableLayout.Controls.Add(this.consolePanel, 0, 3);
            this.mainTableLayout.Dock = System.Windows.Forms.DockStyle.Fill;
            this.mainTableLayout.Location = new System.Drawing.Point(0, 0);
            this.mainTableLayout.Name = "mainTableLayout";
            this.mainTableLayout.RowCount = 4;
            this.mainTableLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 80F));
            this.mainTableLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 30F));
            this.mainTableLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 40F));
            this.mainTableLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 30F));
            this.mainTableLayout.Size = new System.Drawing.Size(1400, 900);
            this.mainTableLayout.TabIndex = 0;
            // 
            // headerPanel
            // 
            this.mainTableLayout.SetColumnSpan(this.headerPanel, 3);
            this.headerPanel.Controls.Add(this.lblTitle);
            this.headerPanel.Controls.Add(this.lblSystemTime);
            this.headerPanel.Controls.Add(this.lblOPCStatus);
            this.headerPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.headerPanel.Location = new System.Drawing.Point(3, 3);
            this.headerPanel.Name = "headerPanel";
            this.headerPanel.Size = new System.Drawing.Size(1394, 74);
            this.headerPanel.TabIndex = 0;
            // 
            // lblTitle
            // 
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Segoe UI", 18F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTitle.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(255)))), ((int)(((byte)(127)))));
            this.lblTitle.Location = new System.Drawing.Point(15, 15);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(508, 32);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "🏭 EQ12 Marketplace SCADA Control System";
            // 
            // lblSystemTime
            // 
            this.lblSystemTime.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.lblSystemTime.AutoSize = true;
            this.lblSystemTime.Font = new System.Drawing.Font("Consolas", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSystemTime.ForeColor = System.Drawing.Color.White;
            this.lblSystemTime.Location = new System.Drawing.Point(1150, 15);
            this.lblSystemTime.Name = "lblSystemTime";
            this.lblSystemTime.Size = new System.Drawing.Size(234, 19);
            this.lblSystemTime.TabIndex = 1;
            this.lblSystemTime.Text = "⏰ 2024-01-15 14:30:45";
            // 
            // lblOPCStatus
            // 
            this.lblOPCStatus.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.lblOPCStatus.AutoSize = true;
            this.lblOPCStatus.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblOPCStatus.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(69)))), ((int)(((byte)(58)))));
            this.lblOPCStatus.Location = new System.Drawing.Point(1200, 45);
            this.lblOPCStatus.Name = "lblOPCStatus";
            this.lblOPCStatus.Size = new System.Drawing.Size(184, 21);
            this.lblOPCStatus.TabIndex = 2;
            this.lblOPCStatus.Text = "🔴 OPC UA Disconnected";
            // 
            // statusPanel
            // 
            this.statusPanel.Controls.Add(this.lblSystemHealth);
            this.statusPanel.Controls.Add(this.lblMemoryUsage);
            this.statusPanel.Controls.Add(this.lblEQ12Components);
            this.statusPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.statusPanel.Location = new System.Drawing.Point(3, 83);
            this.statusPanel.Name = "statusPanel";
            this.statusPanel.Size = new System.Drawing.Size(414, 240);
            this.statusPanel.TabIndex = 1;
            // 
            // lblSystemHealth
            // 
            this.lblSystemHealth.AutoSize = true;
            this.lblSystemHealth.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSystemHealth.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(255)))), ((int)(((byte)(127)))));
            this.lblSystemHealth.Location = new System.Drawing.Point(15, 30);
            this.lblSystemHealth.Name = "lblSystemHealth";
            this.lblSystemHealth.Size = new System.Drawing.Size(198, 21);
            this.lblSystemHealth.TabIndex = 0;
            this.lblSystemHealth.Text = "🏥 EQ12 Processes: 12";
            // 
            // lblMemoryUsage
            // 
            this.lblMemoryUsage.AutoSize = true;
            this.lblMemoryUsage.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblMemoryUsage.ForeColor = System.Drawing.Color.White;
            this.lblMemoryUsage.Location = new System.Drawing.Point(15, 70);
            this.lblMemoryUsage.Name = "lblMemoryUsage";
            this.lblMemoryUsage.Size = new System.Drawing.Size(163, 21);
            this.lblMemoryUsage.TabIndex = 1;
            this.lblMemoryUsage.Text = "🧠 Memory: 245 MB";
            // 
            // lblEQ12Components
            // 
            this.lblEQ12Components.AutoSize = true;
            this.lblEQ12Components.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblEQ12Components.ForeColor = System.Drawing.Color.White;
            this.lblEQ12Components.Location = new System.Drawing.Point(15, 110);
            this.lblEQ12Components.Name = "lblEQ12Components";
            this.lblEQ12Components.Size = new System.Drawing.Size(220, 21);
            this.lblEQ12Components.TabIndex = 2;
            this.lblEQ12Components.Text = "🔧 EQ12 Components: 312";
            // 
            // metricsPanel
            // 
            this.metricsPanel.Controls.Add(this.lblTotalListings);
            this.metricsPanel.Controls.Add(this.lblTotalSales);
            this.metricsPanel.Controls.Add(this.lblAutomationStatus);
            this.metricsPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.metricsPanel.Location = new System.Drawing.Point(423, 83);
            this.metricsPanel.Name = "metricsPanel";
            this.metricsPanel.Size = new System.Drawing.Size(554, 240);
            this.metricsPanel.TabIndex = 2;
            // 
            // lblTotalListings
            // 
            this.lblTotalListings.AutoSize = true;
            this.lblTotalListings.Font = new System.Drawing.Font("Segoe UI", 16F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTotalListings.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(162)))), ((int)(((byte)(232)))));
            this.lblTotalListings.Location = new System.Drawing.Point(20, 30);
            this.lblTotalListings.Name = "lblTotalListings";
            this.lblTotalListings.Size = new System.Drawing.Size(268, 30);
            this.lblTotalListings.TabIndex = 0;
            this.lblTotalListings.Text = "📦 Active Listings: 247";
            // 
            // lblTotalSales
            // 
            this.lblTotalSales.AutoSize = true;
            this.lblTotalSales.Font = new System.Drawing.Font("Segoe UI", 16F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTotalSales.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(255)))), ((int)(((byte)(127)))));
            this.lblTotalSales.Location = new System.Drawing.Point(20, 80);
            this.lblTotalSales.Name = "lblTotalSales";
            this.lblTotalSales.Size = new System.Drawing.Size(294, 30);
            this.lblTotalSales.TabIndex = 1;
            this.lblTotalSales.Text = "💰 Total Sales: $12,450.67";
            // 
            // lblAutomationStatus
            // 
            this.lblAutomationStatus.AutoSize = true;
            this.lblAutomationStatus.Font = new System.Drawing.Font("Segoe UI", 14F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblAutomationStatus.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(191)))), ((int)(((byte)(0)))));
            this.lblAutomationStatus.Location = new System.Drawing.Point(20, 130);
            this.lblAutomationStatus.Name = "lblAutomationStatus";
            this.lblAutomationStatus.Size = new System.Drawing.Size(251, 25);
            this.lblAutomationStatus.TabIndex = 2;
            this.lblAutomationStatus.Text = "⏸️ Automation: PAUSED";
            // 
            // marketplacesPanel
            // 
            this.marketplacesPanel.Controls.Add(this.ebayGroupBox);
            this.marketplacesPanel.Controls.Add(this.facebookGroupBox);
            this.marketplacesPanel.Controls.Add(this.mercariGroupBox);
            this.marketplacesPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.marketplacesPanel.Location = new System.Drawing.Point(983, 83);
            this.marketplacesPanel.Name = "marketplacesPanel";
            this.marketplacesPanel.Size = new System.Drawing.Size(414, 240);
            this.marketplacesPanel.TabIndex = 3;
            // 
            // ebayGroupBox
            // 
            this.ebayGroupBox.Controls.Add(this.lblEBayStatus);
            this.ebayGroupBox.Controls.Add(this.lblEBayListings);
            this.ebayGroupBox.Controls.Add(this.lblEBaySales);
            this.ebayGroupBox.Controls.Add(this.lblEBayConversion);
            this.ebayGroupBox.ForeColor = System.Drawing.Color.White;
            this.ebayGroupBox.Location = new System.Drawing.Point(10, 10);
            this.ebayGroupBox.Name = "ebayGroupBox";
            this.ebayGroupBox.Size = new System.Drawing.Size(390, 65);
            this.ebayGroupBox.TabIndex = 0;
            this.ebayGroupBox.TabStop = false;
            this.ebayGroupBox.Text = "📊 eBay";
            // 
            // lblEBayStatus
            // 
            this.lblEBayStatus.AutoSize = true;
            this.lblEBayStatus.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblEBayStatus.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(255)))), ((int)(((byte)(127)))));
            this.lblEBayStatus.Location = new System.Drawing.Point(10, 20);
            this.lblEBayStatus.Name = "lblEBayStatus";
            this.lblEBayStatus.Size = new System.Drawing.Size(89, 15);
            this.lblEBayStatus.TabIndex = 0;
            this.lblEBayStatus.Text = "eBay: ONLINE";
            // 
            // lblEBayListings
            // 
            this.lblEBayListings.AutoSize = true;
            this.lblEBayListings.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblEBayListings.ForeColor = System.Drawing.Color.White;
            this.lblEBayListings.Location = new System.Drawing.Point(120, 20);
            this.lblEBayListings.Name = "lblEBayListings";
            this.lblEBayListings.Size = new System.Drawing.Size(82, 15);
            this.lblEBayListings.TabIndex = 1;
            this.lblEBayListings.Text = "📦 156 listings";
            // 
            // lblEBaySales
            // 
            this.lblEBaySales.AutoSize = true;
            this.lblEBaySales.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblEBaySales.ForeColor = System.Drawing.Color.White;
            this.lblEBaySales.Location = new System.Drawing.Point(10, 40);
            this.lblEBaySales.Name = "lblEBaySales";
            this.lblEBaySales.Size = new System.Drawing.Size(75, 15);
            this.lblEBaySales.TabIndex = 2;
            this.lblEBaySales.Text = "💰 $8,234.50";
            // 
            // lblEBayConversion
            // 
            this.lblEBayConversion.AutoSize = true;
            this.lblEBayConversion.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblEBayConversion.ForeColor = System.Drawing.Color.White;
            this.lblEBayConversion.Location = new System.Drawing.Point(120, 40);
            this.lblEBayConversion.Name = "lblEBayConversion";
            this.lblEBayConversion.Size = new System.Drawing.Size(56, 15);
            this.lblEBayConversion.TabIndex = 3;
            this.lblEBayConversion.Text = "📈 12.3%";
            // 
            // facebookGroupBox
            // 
            this.facebookGroupBox.Controls.Add(this.lblFacebookStatus);
            this.facebookGroupBox.Controls.Add(this.lblFacebookListings);
            this.facebookGroupBox.Controls.Add(this.lblFacebookSales);
            this.facebookGroupBox.Controls.Add(this.lblFacebookConversion);
            this.facebookGroupBox.ForeColor = System.Drawing.Color.White;
            this.facebookGroupBox.Location = new System.Drawing.Point(10, 85);
            this.facebookGroupBox.Name = "facebookGroupBox";
            this.facebookGroupBox.Size = new System.Drawing.Size(390, 65);
            this.facebookGroupBox.TabIndex = 1;
            this.facebookGroupBox.TabStop = false;
            this.facebookGroupBox.Text = "📊 Facebook Marketplace";
            // 
            // lblFacebookStatus
            // 
            this.lblFacebookStatus.AutoSize = true;
            this.lblFacebookStatus.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblFacebookStatus.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(191)))), ((int)(((byte)(0)))));
            this.lblFacebookStatus.Location = new System.Drawing.Point(10, 20);
            this.lblFacebookStatus.Name = "lblFacebookStatus";
            this.lblFacebookStatus.Size = new System.Drawing.Size(119, 15);
            this.lblFacebookStatus.TabIndex = 0;
            this.lblFacebookStatus.Text = "Facebook: PENDING";
            // 
            // lblFacebookListings
            // 
            this.lblFacebookListings.AutoSize = true;
            this.lblFacebookListings.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblFacebookListings.ForeColor = System.Drawing.Color.White;
            this.lblFacebookListings.Location = new System.Drawing.Point(150, 20);
            this.lblFacebookListings.Name = "lblFacebookListings";
            this.lblFacebookListings.Size = new System.Drawing.Size(74, 15);
            this.lblFacebookListings.TabIndex = 1;
            this.lblFacebookListings.Text = "📦 47 listings";
            // 
            // lblFacebookSales
            // 
            this.lblFacebookSales.AutoSize = true;
            this.lblFacebookSales.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblFacebookSales.ForeColor = System.Drawing.Color.White;
            this.lblFacebookSales.Location = new System.Drawing.Point(10, 40);
            this.lblFacebookSales.Name = "lblFacebookSales";
            this.lblFacebookSales.Size = new System.Drawing.Size(75, 15);
            this.lblFacebookSales.TabIndex = 2;
            this.lblFacebookSales.Text = "💰 $2,156.17";
            // 
            // lblFacebookConversion
            // 
            this.lblFacebookConversion.AutoSize = true;
            this.lblFacebookConversion.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblFacebookConversion.ForeColor = System.Drawing.Color.White;
            this.lblFacebookConversion.Location = new System.Drawing.Point(150, 40);
            this.lblFacebookConversion.Name = "lblFacebookConversion";
            this.lblFacebookConversion.Size = new System.Drawing.Size(49, 15);
            this.lblFacebookConversion.TabIndex = 3;
            this.lblFacebookConversion.Text = "📈 8.7%";
            // 
            // mercariGroupBox
            // 
            this.mercariGroupBox.Controls.Add(this.lblMercariStatus);
            this.mercariGroupBox.Controls.Add(this.lblMercariListings);
            this.mercariGroupBox.Controls.Add(this.lblMercariSales);
            this.mercariGroupBox.Controls.Add(this.lblMercariConversion);
            this.mercariGroupBox.ForeColor = System.Drawing.Color.White;
            this.mercariGroupBox.Location = new System.Drawing.Point(10, 160);
            this.mercariGroupBox.Name = "mercariGroupBox";
            this.mercariGroupBox.Size = new System.Drawing.Size(390, 65);
            this.mercariGroupBox.TabIndex = 2;
            this.mercariGroupBox.TabStop = false;
            this.mercariGroupBox.Text = "📊 Mercari";
            // 
            // lblMercariStatus
            // 
            this.lblMercariStatus.AutoSize = true;
            this.lblMercariStatus.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblMercariStatus.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(69)))), ((int)(((byte)(58)))));
            this.lblMercariStatus.Location = new System.Drawing.Point(10, 20);
            this.lblMercariStatus.Name = "lblMercariStatus";
            this.lblMercariStatus.Size = new System.Drawing.Size(105, 15);
            this.lblMercariStatus.TabIndex = 0;
            this.lblMercariStatus.Text = "Mercari: OFFLINE";
            // 
            // lblMercariListings
            // 
            this.lblMercariListings.AutoSize = true;
            this.lblMercariListings.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblMercariListings.ForeColor = System.Drawing.Color.White;
            this.lblMercariListings.Location = new System.Drawing.Point(130, 20);
            this.lblMercariListings.Name = "lblMercariListings";
            this.lblMercariListings.Size = new System.Drawing.Size(74, 15);
            this.lblMercariListings.TabIndex = 1;
            this.lblMercariListings.Text = "📦 44 listings";
            // 
            // lblMercariSales
            // 
            this.lblMercariSales.AutoSize = true;
            this.lblMercariSales.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblMercariSales.ForeColor = System.Drawing.Color.White;
            this.lblMercariSales.Location = new System.Drawing.Point(10, 40);
            this.lblMercariSales.Name = "lblMercariSales";
            this.lblMercariSales.Size = new System.Drawing.Size(75, 15);
            this.lblMercariSales.TabIndex = 2;
            this.lblMercariSales.Text = "💰 $2,060.00";
            // 
            // lblMercariConversion
            // 
            this.lblMercariConversion.AutoSize = true;
            this.lblMercariConversion.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblMercariConversion.ForeColor = System.Drawing.Color.White;
            this.lblMercariConversion.Location = new System.Drawing.Point(130, 40);
            this.lblMercariConversion.Name = "lblMercariConversion";
            this.lblMercariConversion.Size = new System.Drawing.Size(56, 15);
            this.lblMercariConversion.TabIndex = 3;
            this.lblMercariConversion.Text = "📈 15.2%";
            // 
            // controlPanel
            // 
            this.controlPanel.Controls.Add(this.btnStartAutomation);
            this.controlPanel.Controls.Add(this.btnStopAutomation);
            this.controlPanel.Controls.Add(this.btnGenerateProducts);
            this.controlPanel.Controls.Add(this.btnConnectOPC);
            this.controlPanel.Controls.Add(this.btnEmergencyStop);
            this.controlPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.controlPanel.Location = new System.Drawing.Point(3, 329);
            this.controlPanel.Name = "controlPanel";
            this.controlPanel.Size = new System.Drawing.Size(414, 322);
            this.controlPanel.TabIndex = 4;
            // 
            // btnStartAutomation
            // 
            this.btnStartAutomation.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(255)))), ((int)(((byte)(127)))));
            this.btnStartAutomation.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnStartAutomation.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnStartAutomation.ForeColor = System.Drawing.Color.Black;
            this.btnStartAutomation.Location = new System.Drawing.Point(15, 20);
            this.btnStartAutomation.Name = "btnStartAutomation";
            this.btnStartAutomation.Size = new System.Drawing.Size(180, 50);
            this.btnStartAutomation.TabIndex = 0;
            this.btnStartAutomation.Text = "🚀 START AUTOMATION";
            this.btnStartAutomation.UseVisualStyleBackColor = false;
            this.btnStartAutomation.Click += new System.EventHandler(this.btnStartAutomation_Click);
            // 
            // btnStopAutomation
            // 
            this.btnStopAutomation.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(191)))), ((int)(((byte)(0)))));
            this.btnStopAutomation.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnStopAutomation.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnStopAutomation.ForeColor = System.Drawing.Color.Black;
            this.btnStopAutomation.Location = new System.Drawing.Point(210, 20);
            this.btnStopAutomation.Name = "btnStopAutomation";
            this.btnStopAutomation.Size = new System.Drawing.Size(180, 50);
            this.btnStopAutomation.TabIndex = 1;
            this.btnStopAutomation.Text = "⏸️ STOP AUTOMATION";
            this.btnStopAutomation.UseVisualStyleBackColor = false;
            this.btnStopAutomation.Click += new System.EventHandler(this.btnStopAutomation_Click);
            // 
            // btnGenerateProducts
            // 
            this.btnGenerateProducts.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(162)))), ((int)(((byte)(232)))));
            this.btnGenerateProducts.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnGenerateProducts.Font = new System.Drawing.Font("Segoe UI", 11F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnGenerateProducts.ForeColor = System.Drawing.Color.White;
            this.btnGenerateProducts.Location = new System.Drawing.Point(15, 90);
            this.btnGenerateProducts.Name = "btnGenerateProducts";
            this.btnGenerateProducts.Size = new System.Drawing.Size(180, 50);
            this.btnGenerateProducts.TabIndex = 2;
            this.btnGenerateProducts.Text = "📦 GENERATE PRODUCTS";
            this.btnGenerateProducts.UseVisualStyleBackColor = false;
            this.btnGenerateProducts.Click += new System.EventHandler(this.btnGenerateProducts_Click);
            // 
            // btnConnectOPC
            // 
            this.btnConnectOPC.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(156)))), ((int)(((byte)(39)))), ((int)(((byte)(176)))));
            this.btnConnectOPC.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnConnectOPC.Font = new System.Drawing.Font("Segoe UI", 11F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnConnectOPC.ForeColor = System.Drawing.Color.White;
            this.btnConnectOPC.Location = new System.Drawing.Point(210, 90);
            this.btnConnectOPC.Name = "btnConnectOPC";
            this.btnConnectOPC.Size = new System.Drawing.Size(180, 50);
            this.btnConnectOPC.TabIndex = 3;
            this.btnConnectOPC.Text = "🔗 CONNECT OPC UA";
            this.btnConnectOPC.UseVisualStyleBackColor = false;
            this.btnConnectOPC.Click += new System.EventHandler(this.btnConnectOPC_Click);
            // 
            // btnEmergencyStop
            // 
            this.btnEmergencyStop.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(69)))), ((int)(((byte)(58)))));
            this.btnEmergencyStop.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnEmergencyStop.Font = new System.Drawing.Font("Segoe UI", 14F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnEmergencyStop.ForeColor = System.Drawing.Color.White;
            this.btnEmergencyStop.Location = new System.Drawing.Point(15, 160);
            this.btnEmergencyStop.Name = "btnEmergencyStop";
            this.btnEmergencyStop.Size = new System.Drawing.Size(375, 70);
            this.btnEmergencyStop.TabIndex = 4;
            this.btnEmergencyStop.Text = "🛑 EMERGENCY STOP";
            this.btnEmergencyStop.UseVisualStyleBackColor = false;
            // 
            // chartsPanel
            // 
            this.chartsPanel.Controls.Add(this.revenueChart);
            this.chartsPanel.Controls.Add(this.listingsChart);
            this.chartsPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.chartsPanel.Location = new System.Drawing.Point(423, 329);
            this.chartsPanel.Name = "chartsPanel";
            this.chartsPanel.Size = new System.Drawing.Size(554, 322);
            this.chartsPanel.TabIndex = 5;
            // 
            // revenueChart
            // 
            this.revenueChart.Location = new System.Drawing.Point(10, 10);
            this.revenueChart.Name = "revenueChart";
            this.revenueChart.Size = new System.Drawing.Size(530, 150);
            this.revenueChart.TabIndex = 0;
            this.revenueChart.Text = "Revenue Trend";
            // 
            // listingsChart
            // 
            this.listingsChart.Location = new System.Drawing.Point(10, 170);
            this.listingsChart.Name = "listingsChart";
            this.listingsChart.Size = new System.Drawing.Size(530, 140);
            this.listingsChart.TabIndex = 1;
            this.listingsChart.Text = "Active Listings";
            // 
            // consolePanel
            // 
            this.mainTableLayout.SetColumnSpan(this.consolePanel, 3);
            this.consolePanel.Controls.Add(this.txtConsoleLog);
            this.consolePanel.Controls.Add(this.lblConsoleTitle);
            this.consolePanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.consolePanel.Location = new System.Drawing.Point(3, 657);
            this.consolePanel.Name = "consolePanel";
            this.consolePanel.Size = new System.Drawing.Size(1394, 240);
            this.consolePanel.TabIndex = 6;
            // 
            // txtConsoleLog
            // 
            this.txtConsoleLog.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(30)))), ((int)(((byte)(30)))), ((int)(((byte)(30)))));
            this.txtConsoleLog.Font = new System.Drawing.Font("Consolas", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtConsoleLog.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(255)))), ((int)(((byte)(127)))));
            this.txtConsoleLog.Location = new System.Drawing.Point(15, 35);
            this.txtConsoleLog.Multiline = true;
            this.txtConsoleLog.Name = "txtConsoleLog";
            this.txtConsoleLog.ReadOnly = true;
            this.txtConsoleLog.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtConsoleLog.Size = new System.Drawing.Size(1365, 190);
            this.txtConsoleLog.TabIndex = 1;
            this.txtConsoleLog.Text = "[14:30:45] 🔧 SCADA System Initialized\r\n[14:30:45] 📊 Real-time charts initialize" +
    "d\r\n[14:30:45] ✅ Marketplace database initialized\r\n";
            // 
            // lblConsoleTitle
            // 
            this.lblConsoleTitle.AutoSize = true;
            this.lblConsoleTitle.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblConsoleTitle.ForeColor = System.Drawing.Color.White;
            this.lblConsoleTitle.Location = new System.Drawing.Point(15, 10);
            this.lblConsoleTitle.Name = "lblConsoleTitle";
            this.lblConsoleTitle.Size = new System.Drawing.Size(224, 21);
            this.lblConsoleTitle.TabIndex = 0;
            this.lblConsoleTitle.Text = "📝 System Console - Live Log";
            // 
            // updateTimer
            // 
            this.updateTimer.Enabled = true;
            this.updateTimer.Interval = 1000;
            // 
            // MarketplaceHMI
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(45)))), ((int)(((byte)(45)))), ((int)(((byte)(48)))));
            this.ClientSize = new System.Drawing.Size(1400, 900);
            this.Controls.Add(this.mainTableLayout);
            this.Name = "MarketplaceHMI";
            this.Text = "EQ12 Marketplace SCADA Control System";
            this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
            this.mainTableLayout.ResumeLayout(false);
            this.headerPanel.ResumeLayout(false);
            this.headerPanel.PerformLayout();
            this.statusPanel.ResumeLayout(false);
            this.statusPanel.PerformLayout();
            this.metricsPanel.ResumeLayout(false);
            this.metricsPanel.PerformLayout();
            this.marketplacesPanel.ResumeLayout(false);
            this.ebayGroupBox.ResumeLayout(false);
            this.ebayGroupBox.PerformLayout();
            this.facebookGroupBox.ResumeLayout(false);
            this.facebookGroupBox.PerformLayout();
            this.mercariGroupBox.ResumeLayout(false);
            this.mercariGroupBox.PerformLayout();
            this.controlPanel.ResumeLayout(false);
            this.chartsPanel.ResumeLayout(false);
            this.consolePanel.ResumeLayout(false);
            this.consolePanel.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TableLayoutPanel mainTableLayout;
        private System.Windows.Forms.Panel headerPanel;
        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Label lblSystemTime;
        private System.Windows.Forms.Label lblOPCStatus;
        private System.Windows.Forms.Panel statusPanel;
        private System.Windows.Forms.Label lblSystemHealth;
        private System.Windows.Forms.Label lblMemoryUsage;
        private System.Windows.Forms.Label lblEQ12Components;
        private System.Windows.Forms.Panel metricsPanel;
        private System.Windows.Forms.Label lblTotalListings;
        private System.Windows.Forms.Label lblTotalSales;
        private System.Windows.Forms.Label lblAutomationStatus;
        private System.Windows.Forms.Panel marketplacesPanel;
        private System.Windows.Forms.GroupBox ebayGroupBox;
        private System.Windows.Forms.Label lblEBayStatus;
        private System.Windows.Forms.Label lblEBayListings;
        private System.Windows.Forms.Label lblEBaySales;
        private System.Windows.Forms.Label lblEBayConversion;
        private System.Windows.Forms.GroupBox facebookGroupBox;
        private System.Windows.Forms.Label lblFacebookStatus;
        private System.Windows.Forms.Label lblFacebookListings;
        private System.Windows.Forms.Label lblFacebookSales;
        private System.Windows.Forms.Label lblFacebookConversion;
        private System.Windows.Forms.GroupBox mercariGroupBox;
        private System.Windows.Forms.Label lblMercariStatus;
        private System.Windows.Forms.Label lblMercariListings;
        private System.Windows.Forms.Label lblMercariSales;
        private System.Windows.Forms.Label lblMercariConversion;
        private System.Windows.Forms.Panel controlPanel;
        private System.Windows.Forms.Button btnStartAutomation;
        private System.Windows.Forms.Button btnStopAutomation;
        private System.Windows.Forms.Button btnGenerateProducts;
        private System.Windows.Forms.Button btnConnectOPC;
        private System.Windows.Forms.Button btnEmergencyStop;
        private System.Windows.Forms.Panel chartsPanel;
        private LiveCharts.WinForms.CartesianChart revenueChart;
        private LiveCharts.WinForms.CartesianChart listingsChart;
        private System.Windows.Forms.Panel consolePanel;
        private System.Windows.Forms.TextBox txtConsoleLog;
        private System.Windows.Forms.Label lblConsoleTitle;
        private System.Windows.Forms.Timer updateTimer;
    }
}