using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Diagnostics;
using System.Threading;
using LiveCharts;
using LiveCharts.Wpf;
using LiveCharts.Configurations;
using Opc.Ua;
using Opc.Ua.Client;
using Newtonsoft.Json;
using System.Data.SQLite;

namespace EQ12.MarketplaceSCADA
{
    public partial class MarketplaceHMI : Form
    {
        private Session opcSession;
        private ApplicationConfiguration opcConfig;
        private Timer dataUpdateTimer;
        private Timer statusTimer;

        // SCADA Data Points
        private Dictionary<string, MonitoredItem> monitoredItems;
        private Dictionary<string, double> currentValues;

        // EQ12 Integration
        private string eq12WorkspacePath = @"C:\EQ12";
        private string databasePath;

        public MarketplaceHMI()
        {
            InitializeComponent();
            InitializeSCADA();
            SetupIndustrialTheme();
            InitializeCharts();
            LoadEQ12Configuration();
        }

        private void InitializeSCADA()
        {
            this.Text = "EQ12 Marketplace SCADA Control - Industrial HMI v1.0";
            this.WindowState = FormWindowState.Maximized;
            this.BackColor = Color.FromArgb(45, 45, 48); // Dark industrial theme

            monitoredItems = new Dictionary<string, MonitoredItem>();
            currentValues = new Dictionary<string, double>();
            databasePath = Path.Combine(eq12WorkspacePath, "data", "marketplace_automation.db");

            // Initialize timers
            dataUpdateTimer = new Timer();
            dataUpdateTimer.Interval = 5000; // 5 second updates
            dataUpdateTimer.Tick += DataUpdateTimer_Tick;
            dataUpdateTimer.Start();

            statusTimer = new Timer();
            statusTimer.Interval = 1000; // 1 second status updates
            statusTimer.Tick += StatusTimer_Tick;
            statusTimer.Start();

            LogToConsole("🔧 SCADA System Initialized");
        }

        private void SetupIndustrialTheme()
        {
            // Industrial control room color scheme
            Color primaryBg = Color.FromArgb(45, 45, 48);
            Color secondaryBg = Color.FromArgb(62, 62, 66);
            Color accentGreen = Color.FromArgb(0, 255, 127);
            Color accentBlue = Color.FromArgb(0, 162, 232);
            Color warningAmber = Color.FromArgb(255, 191, 0);
            Color alarmRed = Color.FromArgb(255, 69, 58);

            this.BackColor = primaryBg;

            // Apply industrial styling to all controls
            foreach (Control control in this.Controls)
            {
                ApplyIndustrialStyling(control, primaryBg, secondaryBg, accentGreen);
            }
        }

        private void ApplyIndustrialStyling(Control control, Color bg, Color secondary, Color accent)
        {
            if (control is Panel || control is GroupBox)
            {
                control.BackColor = secondary;
                control.ForeColor = Color.White;
            }
            else if (control is Button)
            {
                control.BackColor = accent;
                control.ForeColor = Color.Black;
                control.FlatStyle = FlatStyle.Flat;
                ((Button)control).FlatAppearance.BorderSize = 0;
            }
            else if (control is Label)
            {
                control.ForeColor = Color.White;
                control.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            }
            else if (control is TextBox || control is ComboBox)
            {
                control.BackColor = Color.FromArgb(30, 30, 30);
                control.ForeColor = Color.White;
            }

            // Recursively apply to child controls
            foreach (Control child in control.Controls)
            {
                ApplyIndustrialStyling(child, bg, secondary, accent);
            }
        }

        private void InitializeCharts()
        {
            // Revenue chart
            var revenueMapper = Mappers.Xy<MarketplaceMetric>()
                .X(model => model.DateTime.Ticks)
                .Y(model => model.Revenue);

            Charting.For<MarketplaceMetric>(revenueMapper);

            // Listings chart  
            var listingsMapper = Mappers.Xy<MarketplaceMetric>()
                .X(model => model.DateTime.Ticks)
                .Y(model => model.ActiveListings);

            Charting.For<MarketplaceMetric>(listingsMapper);

            LogToConsole("📊 Real-time charts initialized");
        }

        private async void ConnectToOPCUA()
        {
            try
            {
                string endpointUrl = "opc.tcp://localhost:4841/freeopcua/server/";

                opcConfig = new ApplicationConfiguration()
                {
                    ApplicationName = "EQ12 Marketplace HMI Client",
                    ApplicationType = ApplicationType.Client,
                    SecurityConfiguration = new SecurityConfiguration
                    {
                        ApplicationCertificate = new CertificateIdentifier(),
                        AutoAcceptUntrustedCertificates = true
                    },
                    ClientConfiguration = new ClientConfiguration
                    {
                        DefaultSessionTimeout = 60000,
                        WellKnownDiscoveryUrls = new StringCollection { endpointUrl }
                    }
                };

                await opcConfig.Validate(ApplicationType.Client);

                var application = new ApplicationInstance(opcConfig);

                var selectedEndpoint = CoreClientUtils.SelectEndpoint(endpointUrl, false);
                var endpointConfiguration = EndpointConfiguration.Create(opcConfig);
                var endpoint = new ConfiguredEndpoint(null, selectedEndpoint, endpointConfiguration);

                opcSession = await Session.Create(
                    opcConfig,
                    endpoint,
                    false,
                    "EQ12MarketplaceHMI",
                    60000,
                    new UserIdentity(new AnonymousIdentityToken()),
                    null
                );

                if (opcSession != null && opcSession.Connected)
                {
                    lblOPCStatus.Text = "🟢 OPC UA Connected";
                    lblOPCStatus.ForeColor = Color.FromArgb(0, 255, 127);

                    // Subscribe to SCADA variables
                    await SubscribeToSCADAVariables();

                    LogToConsole("✅ OPC UA connection established");
                }
            }
            catch (Exception ex)
            {
                lblOPCStatus.Text = "🔴 OPC UA Disconnected";
                lblOPCStatus.ForeColor = Color.FromArgb(255, 69, 58);
                LogToConsole($"❌ OPC UA connection failed: {ex.Message}");
            }
        }

        private async Task SubscribeToSCADAVariables()
        {
            if (opcSession == null || !opcSession.Connected) return;

            try
            {
                var subscription = new Subscription(opcSession.DefaultSubscription)
                {
                    PublishingInterval = 1000,
                    PublishingEnabled = true
                };

                // Monitor key marketplace variables
                var variables = new[]
                {
                    "ns=2;s=EQ12_Marketplace.TotalListings",
                    "ns=2;s=EQ12_Marketplace.TotalSales",
                    "ns=2;s=EQ12_Marketplace.eBayStatus",
                    "ns=2;s=EQ12_Marketplace.FacebookStatus",
                    "ns=2;s=EQ12_Marketplace.AutomationActive"
                };

                foreach (var variable in variables)
                {
                    var monitoredItem = new MonitoredItem(subscription.DefaultItem)
                    {
                        DisplayName = variable,
                        StartNodeId = variable
                    };

                    monitoredItem.Notification += MonitoredItem_Notification;
                    subscription.AddItem(monitoredItem);
                    monitoredItems[variable] = monitoredItem;
                }

                opcSession.AddSubscription(subscription);
                subscription.Create();

                LogToConsole("📡 SCADA variable monitoring active");
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ SCADA subscription failed: {ex.Message}");
            }
        }

        private void MonitoredItem_Notification(MonitoredItem item, MonitoredItemNotificationEventArgs e)
        {
            foreach (var value in item.DequeueValues())
            {
                var variableName = item.DisplayName;

                this.Invoke(new Action(() =>
                {
                    UpdateSCADADisplay(variableName, value.Value);
                }));
            }
        }

        private void UpdateSCADADisplay(string variableName, object value)
        {
            try
            {
                switch (variableName)
                {
                    case "ns=2;s=EQ12_Marketplace.TotalListings":
                        lblTotalListings.Text = $"📦 Active Listings: {value}";
                        if (double.TryParse(value.ToString(), out double listings))
                        {
                            currentValues["TotalListings"] = listings;
                        }
                        break;

                    case "ns=2;s=EQ12_Marketplace.TotalSales":
                        lblTotalSales.Text = $"💰 Total Sales: ${value:F2}";
                        if (double.TryParse(value.ToString(), out double sales))
                        {
                            currentValues["TotalSales"] = sales;
                        }
                        break;

                    case "ns=2;s=EQ12_Marketplace.eBayStatus":
                        lblEBayStatus.Text = $"eBay: {value}";
                        lblEBayStatus.ForeColor = value.ToString() == "online" ?
                            Color.FromArgb(0, 255, 127) : Color.FromArgb(255, 69, 58);
                        break;

                    case "ns=2;s=EQ12_Marketplace.FacebookStatus":
                        lblFacebookStatus.Text = $"Facebook: {value}";
                        lblFacebookStatus.ForeColor = value.ToString() == "online" ?
                            Color.FromArgb(0, 255, 127) : Color.FromArgb(255, 69, 58);
                        break;

                    case "ns=2;s=EQ12_Marketplace.AutomationActive":
                        bool isActive = Convert.ToBoolean(value);
                        lblAutomationStatus.Text = isActive ? "🤖 Automation: ACTIVE" : "⏸️ Automation: PAUSED";
                        lblAutomationStatus.ForeColor = isActive ?
                            Color.FromArgb(0, 255, 127) : Color.FromArgb(255, 191, 0);
                        break;
                }
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ SCADA display update error: {ex.Message}");
            }
        }

        private void DataUpdateTimer_Tick(object sender, EventArgs e)
        {
            UpdateLocalData();
            UpdateCharts();
        }

        private void StatusTimer_Tick(object sender, EventArgs e)
        {
            lblSystemTime.Text = $"⏰ {DateTime.Now:yyyy-MM-dd HH:mm:ss}";

            // Update system health indicators
            UpdateSystemHealth();
        }

        private void UpdateLocalData()
        {
            try
            {
                if (!File.Exists(databasePath)) return;

                using (var connection = new SQLiteConnection($"Data Source={databasePath}"))
                {
                    connection.Open();

                    // Get marketplace metrics
                    var command = new SQLiteCommand(@"
                        SELECT marketplace, active_listings, total_sales, conversion_rate 
                        FROM marketplace_metrics", connection);

                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            var marketplace = reader.GetString("marketplace");
                            var listings = reader.GetInt32("active_listings");
                            var sales = reader.GetDouble("total_sales");
                            var conversion = reader.GetDouble("conversion_rate");

                            UpdateMarketplacePanel(marketplace, listings, sales, conversion);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ Data update error: {ex.Message}");
            }
        }

        private void UpdateMarketplacePanel(string marketplace, int listings, double sales, double conversion)
        {
            switch (marketplace.ToLower())
            {
                case "ebay":
                    lblEBayListings.Text = $"📦 {listings} listings";
                    lblEBaySales.Text = $"💰 ${sales:F2}";
                    lblEBayConversion.Text = $"📈 {conversion:F1}%";
                    break;

                case "facebook":
                    lblFacebookListings.Text = $"📦 {listings} listings";
                    lblFacebookSales.Text = $"💰 ${sales:F2}";
                    lblFacebookConversion.Text = $"📈 {conversion:F1}%";
                    break;

                case "mercari":
                    lblMercariListings.Text = $"📦 {listings} listings";
                    lblMercariSales.Text = $"💰 ${sales:F2}";
                    lblMercariConversion.Text = $"📈 {conversion:F1}%";
                    break;
            }
        }

        private void UpdateCharts()
        {
            // Update revenue trend chart
            if (currentValues.ContainsKey("TotalSales"))
            {
                var newPoint = new MarketplaceMetric
                {
                    DateTime = DateTime.Now,
                    Revenue = currentValues["TotalSales"],
                    ActiveListings = currentValues.ContainsKey("TotalListings") ?
                        (int)currentValues["TotalListings"] : 0
                };

                // Add to chart series (implementation depends on LiveCharts setup)
                AddChartDataPoint(newPoint);
            }
        }

        private void AddChartDataPoint(MarketplaceMetric metric)
        {
            // Implementation for adding data to LiveCharts
            // This would connect to your chart controls
        }

        private void UpdateSystemHealth()
        {
            try
            {
                // Check EQ12 system processes
                var pythonProcesses = Process.GetProcessesByName("python");
                var eq12Processes = pythonProcesses.Where(p =>
                    p.MainModule?.FileName?.Contains("EQ12") == true).Count();

                lblSystemHealth.Text = $"🏥 EQ12 Processes: {eq12Processes}";
                lblSystemHealth.ForeColor = eq12Processes > 0 ?
                    Color.FromArgb(0, 255, 127) : Color.FromArgb(255, 191, 0);

                // Update memory usage
                var currentProcess = Process.GetCurrentProcess();
                lblMemoryUsage.Text = $"🧠 Memory: {currentProcess.WorkingSet64 / 1024 / 1024:F0} MB";

            }
            catch (Exception ex)
            {
                LogToConsole($"❌ System health update error: {ex.Message}");
            }
        }

        private void LoadEQ12Configuration()
        {
            try
            {
                var configPath = Path.Combine(eq12WorkspacePath, "configs", "eq12_master_config.json");
                if (File.Exists(configPath))
                {
                    var json = File.ReadAllText(configPath);
                    var config = JsonConvert.DeserializeObject<EQ12Config>(json);

                    lblEQ12Components.Text = $"🔧 EQ12 Components: {config.Components?.Count ?? 0}";

                    LogToConsole($"✅ Loaded EQ12 config: {config.Components?.Count ?? 0} components");
                }
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ EQ12 config load error: {ex.Message}");
            }
        }

        private void LogToConsole(string message)
        {
            if (txtConsoleLog.InvokeRequired)
            {
                txtConsoleLog.Invoke(new Action(() => LogToConsole(message)));
                return;
            }

            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            txtConsoleLog.AppendText($"[{timestamp}] {message}\r\n");
            txtConsoleLog.ScrollToCaret();
        }

        // Button event handlers
        private void btnStartAutomation_Click(object sender, EventArgs e)
        {
            StartMarketplaceAutomation();
        }

        private void btnStopAutomation_Click(object sender, EventArgs e)
        {
            StopMarketplaceAutomation();
        }

        private void btnGenerateProducts_Click(object sender, EventArgs e)
        {
            GenerateProductsFromEQ12();
        }

        private void btnConnectOPC_Click(object sender, EventArgs e)
        {
            ConnectToOPCUA();
        }

        private async void StartMarketplaceAutomation()
        {
            try
            {
                lblAutomationStatus.Text = "🚀 Starting automation...";
                lblAutomationStatus.ForeColor = Color.FromArgb(255, 191, 0);

                // Start Python automation engine
                var pythonScript = Path.Combine(eq12WorkspacePath, "marketplace_automation",
                    "eq12_marketplace_scada_engine.py");

                if (File.Exists(pythonScript))
                {
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"\"{pythonScript}\"",
                        WorkingDirectory = eq12WorkspacePath,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };

                    Process.Start(startInfo);

                    lblAutomationStatus.Text = "🤖 Automation: ACTIVE";
                    lblAutomationStatus.ForeColor = Color.FromArgb(0, 255, 127);

                    LogToConsole("✅ Marketplace automation started");
                }
                else
                {
                    LogToConsole("❌ Python automation script not found");
                }
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ Automation start error: {ex.Message}");
            }
        }

        private void StopMarketplaceAutomation()
        {
            try
            {
                // Stop automation processes
                var pythonProcesses = Process.GetProcessesByName("python");
                foreach (var process in pythonProcesses)
                {
                    if (process.MainModule?.FileName?.Contains("marketplace") == true)
                    {
                        process.Kill();
                    }
                }

                lblAutomationStatus.Text = "⏸️ Automation: STOPPED";
                lblAutomationStatus.ForeColor = Color.FromArgb(255, 69, 58);

                LogToConsole("⏸️ Marketplace automation stopped");
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ Automation stop error: {ex.Message}");
            }
        }

        private async void GenerateProductsFromEQ12()
        {
            try
            {
                LogToConsole("🔄 Generating products from EQ12 systems...");

                // This would trigger the Python product generation
                var pythonScript = Path.Combine(eq12WorkspacePath, "marketplace_automation",
                    "eq12_marketplace_scada_engine.py");

                var startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{pythonScript}\" --generate-products",
                    WorkingDirectory = eq12WorkspacePath,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true
                };

                using (var process = Process.Start(startInfo))
                {
                    var output = await process.StandardOutput.ReadToEndAsync();
                    LogToConsole($"📦 Product generation: {output}");
                }
            }
            catch (Exception ex)
            {
                LogToConsole($"❌ Product generation error: {ex.Message}");
            }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            // Cleanup OPC UA connection
            try
            {
                opcSession?.Close();
                opcSession?.Dispose();
            }
            catch { }

            // Stop timers
            dataUpdateTimer?.Stop();
            statusTimer?.Stop();

            base.OnFormClosing(e);
        }
    }

    // Data models
    public class MarketplaceMetric
    {
        public DateTime DateTime { get; set; }
        public double Revenue { get; set; }
        public int ActiveListings { get; set; }
        public double ConversionRate { get; set; }
    }

    public class EQ12Config
    {
        public List<EQ12Component> Components { get; set; }
    }

    public class EQ12Component
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public string Status { get; set; }
    }
}