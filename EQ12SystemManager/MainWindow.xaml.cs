using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;
using System.Windows.Threading;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace EQ12SystemManager
{
    /// <summary>
    /// EQ12 System Component Model - Represents betting engines, monitors, AI models, etc.
    /// </summary>
    public class EQ12Component : INotifyPropertyChanged
    {
        private string _name;
        private string _type;
        private string _status;
        private double _cpuUsage;
        private double _memoryUsage;
        private DateTime _lastUpdate;
        private bool _isHealthy;

        public string Name
        {
            get => _name;
            set { _name = value; OnPropertyChanged(); }
        }

        public string Type
        {
            get => _type;
            set { _type = value; OnPropertyChanged(); }
        }

        public string Status
        {
            get => _status;
            set { _status = value; OnPropertyChanged(); StatusBrush = GetStatusBrush(value); }
        }

        public double CpuUsage
        {
            get => _cpuUsage;
            set { _cpuUsage = value; OnPropertyChanged(); }
        }

        public double MemoryUsage
        {
            get => _memoryUsage;
            set { _memoryUsage = value; OnPropertyChanged(); }
        }

        public DateTime LastUpdate
        {
            get => _lastUpdate;
            set { _lastUpdate = value; OnPropertyChanged(); }
        }

        public bool IsHealthy
        {
            get => _isHealthy;
            set { _isHealthy = value; OnPropertyChanged(); }
        }

        public string ScriptPath { get; set; }
        public string ConfigPath { get; set; }
        public List<string> Dependencies { get; set; } = new List<string>();

        private Brush _statusBrush;
        public Brush StatusBrush
        {
            get => _statusBrush;
            set { _statusBrush = value; OnPropertyChanged(); }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        private Brush GetStatusBrush(string status)
        {
            return status?.ToLower() switch
            {
                "running" => new SolidColorBrush(Colors.LimeGreen),
                "stopped" => new SolidColorBrush(Colors.Red),
                "warning" => new SolidColorBrush(Colors.Orange),
                "error" => new SolidColorBrush(Colors.Red),
                _ => new SolidColorBrush(Colors.Gray)
            };
        }
    }

    /// <summary>
    /// System Metrics Model for dashboard display
    /// </summary>
    public class SystemMetrics : INotifyPropertyChanged
    {
        private int _totalComponents;
        private int _activeComponents;
        private double _systemHealth;
        private double _averageCpuUsage;
        private double _averageMemoryUsage;
        private string _systemStatus;

        public int TotalComponents
        {
            get => _totalComponents;
            set { _totalComponents = value; OnPropertyChanged(); }
        }

        public int ActiveComponents
        {
            get => _activeComponents;
            set { _activeComponents = value; OnPropertyChanged(); }
        }

        public double SystemHealth
        {
            get => _systemHealth;
            set { _systemHealth = value; OnPropertyChanged(); }
        }

        public double AverageCpuUsage
        {
            get => _averageCpuUsage;
            set { _averageCpuUsage = value; OnPropertyChanged(); }
        }

        public double AverageMemoryUsage
        {
            get => _averageMemoryUsage;
            set { _averageMemoryUsage = value; OnPropertyChanged(); }
        }

        public string SystemStatus
        {
            get => _systemStatus;
            set { _systemStatus = value; OnPropertyChanged(); }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    /// <summary>
    /// Main Window for EQ12 System Manager - Industrial SCADA Style
    /// </summary>
    public partial class MainWindow : Window, INotifyPropertyChanged
    {
        private readonly ObservableCollection<EQ12Component> _components;
        private readonly SystemMetrics _systemMetrics;
        private readonly DispatcherTimer _updateTimer;
        private readonly HttpClient _httpClient;
        private string _workspacePath = @"C:\EQ12";

        public ObservableCollection<EQ12Component> Components => _components;
        public SystemMetrics Metrics => _systemMetrics;

        private string _selectedComponentType = "All";
        public string SelectedComponentType
        {
            get => _selectedComponentType;
            set
            {
                _selectedComponentType = value;
                OnPropertyChanged();
                FilterComponents();
            }
        }

        public List<string> ComponentTypes { get; } = new List<string>
        {
            "All", "betting_engine", "monitor", "ai_model", "service", "dashboard", "security", "automation"
        };

        public MainWindow()
        {
            InitializeComponent();

            _components = new ObservableCollection<EQ12Component>();
            _systemMetrics = new SystemMetrics();
            _httpClient = new HttpClient();

            DataContext = this;

            // Initialize update timer (5-second interval like industrial HMI)
            _updateTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(5)
            };
            _updateTimer.Tick += UpdateTimer_Tick;

            // Load system configuration and start monitoring
            Loaded += MainWindow_Loaded;
        }

        private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            await LoadSystemConfiguration();
            _updateTimer.Start();
            await UpdateSystemStatus();
        }

        private async Task LoadSystemConfiguration()
        {
            try
            {
                string configPath = Path.Combine(_workspacePath, "configs", "eq12_master_config.json");

                if (!File.Exists(configPath))
                {
                    ShowStatus("Master configuration not found. Running system scan...", Colors.Orange);
                    await RunSystemScan();
                    return;
                }

                string configJson = await File.ReadAllTextAsync(configPath);
                JObject config = JObject.Parse(configJson);

                JArray componentsArray = config["components"] as JArray;
                if (componentsArray != null)
                {
                    foreach (JObject componentJson in componentsArray)
                    {
                        var component = new EQ12Component
                        {
                            Name = componentJson["name"]?.ToString(),
                            Type = componentJson["type"]?.ToString(),
                            ScriptPath = componentJson["script_path"]?.ToString(),
                            ConfigPath = componentJson["config_path"]?.ToString(),
                            Status = "unknown",
                            LastUpdate = DateTime.Now,
                            IsHealthy = true
                        };

                        JArray deps = componentJson["dependencies"] as JArray;
                        if (deps != null)
                        {
                            foreach (string dep in deps)
                            {
                                component.Dependencies.Add(dep);
                            }
                        }

                        _components.Add(component);
                    }
                }

                _systemMetrics.TotalComponents = _components.Count;
                ShowStatus($"Loaded {_components.Count} components from configuration", Colors.LimeGreen);
            }
            catch (Exception ex)
            {
                ShowStatus($"Error loading configuration: {ex.Message}", Colors.Red);
            }
        }

        private async Task RunSystemScan()
        {
            try
            {
                ShowStatus("Running EQ12 system scan...", Colors.Yellow);

                string pythonScript = Path.Combine(_workspacePath, "scripts", "eq12_system_config_generator.py");
                if (!File.Exists(pythonScript))
                {
                    ShowStatus("System scanner not found!", Colors.Red);
                    return;
                }

                var startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{pythonScript}\" --workspace \"{_workspacePath}\" --generate-dashboard",
                    WorkingDirectory = _workspacePath,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(startInfo))
                {
                    await process.WaitForExitAsync();

                    if (process.ExitCode == 0)
                    {
                        ShowStatus("System scan completed successfully", Colors.LimeGreen);
                        await LoadSystemConfiguration();
                    }
                    else
                    {
                        string error = await process.StandardError.ReadToEndAsync();
                        ShowStatus($"System scan failed: {error}", Colors.Red);
                    }
                }
            }
            catch (Exception ex)
            {
                ShowStatus($"Error running system scan: {ex.Message}", Colors.Red);
            }
        }

        private async void UpdateTimer_Tick(object sender, EventArgs e)
        {
            await UpdateSystemStatus();
        }

        private async Task UpdateSystemStatus()
        {
            try
            {
                // Simulate real-time monitoring (in production, this would query actual services)
                int activeCount = 0;
                double totalCpu = 0;
                double totalMemory = 0;
                var random = new Random();

                foreach (var component in _components)
                {
                    // Simulate component status updates
                    double cpuUsage = random.NextDouble() * 30 + 10; // 10-40% CPU
                    double memUsage = random.NextDouble() * 200 + 50; // 50-250MB RAM

                    component.CpuUsage = cpuUsage;
                    component.MemoryUsage = memUsage;
                    component.LastUpdate = DateTime.Now;

                    // Determine component status
                    if (cpuUsage > 80 || memUsage > 400)
                    {
                        component.Status = "warning";
                        component.IsHealthy = false;
                    }
                    else if (random.NextDouble() > 0.95) // 5% chance of being stopped
                    {
                        component.Status = "stopped";
                        component.IsHealthy = false;
                    }
                    else
                    {
                        component.Status = "running";
                        component.IsHealthy = true;
                        activeCount++;
                    }

                    totalCpu += cpuUsage;
                    totalMemory += memUsage;
                }

                // Update system metrics
                _systemMetrics.ActiveComponents = activeCount;
                _systemMetrics.AverageCpuUsage = _components.Count > 0 ? totalCpu / _components.Count : 0;
                _systemMetrics.AverageMemoryUsage = _components.Count > 0 ? totalMemory / _components.Count : 0;
                _systemMetrics.SystemHealth = _components.Count > 0 ? (double)activeCount / _components.Count * 100 : 0;

                if (_systemMetrics.SystemHealth > 95)
                    _systemMetrics.SystemStatus = "Optimal";
                else if (_systemMetrics.SystemHealth > 85)
                    _systemMetrics.SystemStatus = "Good";
                else if (_systemMetrics.SystemHealth > 70)
                    _systemMetrics.SystemStatus = "Warning";
                else
                    _systemMetrics.SystemStatus = "Critical";
            }
            catch (Exception ex)
            {
                ShowStatus($"Error updating system status: {ex.Message}", Colors.Red);
            }
        }

        private void FilterComponents()
        {
            ICollectionView view = CollectionViewSource.GetDefaultView(_components);
            if (_selectedComponentType == "All")
            {
                view.Filter = null;
            }
            else
            {
                view.Filter = obj => obj is EQ12Component component && component.Type == _selectedComponentType;
            }
        }

        private void ShowStatus(string message, Color color)
        {
            Dispatcher.Invoke(() =>
            {
                StatusText.Text = $"{DateTime.Now:HH:mm:ss} - {message}";
                StatusText.Foreground = new SolidColorBrush(color);
            });
        }

        // Component control methods (Start/Stop/Restart)
        private async void StartComponent_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.DataContext is EQ12Component component)
            {
                await ControlComponent(component, "start");
            }
        }

        private async void StopComponent_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.DataContext is EQ12Component component)
            {
                await ControlComponent(component, "stop");
            }
        }

        private async void RestartComponent_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.DataContext is EQ12Component component)
            {
                await ControlComponent(component, "restart");
            }
        }

        private async Task ControlComponent(EQ12Component component, string action)
        {
            try
            {
                ShowStatus($"Executing {action} on {component.Name}...", Colors.Yellow);

                // In production, this would send commands to actual services
                // For now, simulate the action
                await Task.Delay(1000); // Simulate processing time

                switch (action.ToLower())
                {
                    case "start":
                        component.Status = "running";
                        component.IsHealthy = true;
                        break;
                    case "stop":
                        component.Status = "stopped";
                        component.IsHealthy = false;
                        break;
                    case "restart":
                        component.Status = "stopped";
                        await Task.Delay(500);
                        component.Status = "running";
                        component.IsHealthy = true;
                        break;
                }

                ShowStatus($"{action} completed for {component.Name}", Colors.LimeGreen);
            }
            catch (Exception ex)
            {
                ShowStatus($"Error controlling {component.Name}: {ex.Message}", Colors.Red);
            }
        }

        // Configuration validation
        private async void ValidateConfigs_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                ShowStatus("Validating component configurations...", Colors.Yellow);

                int validCount = 0;
                int invalidCount = 0;

                foreach (var component in _components)
                {
                    if (File.Exists(component.ConfigPath))
                    {
                        try
                        {
                            string configJson = await File.ReadAllTextAsync(component.ConfigPath);
                            JObject.Parse(configJson); // Validate JSON
                            validCount++;
                        }
                        catch
                        {
                            invalidCount++;
                        }
                    }
                    else
                    {
                        invalidCount++;
                    }
                }

                ShowStatus($"Configuration validation complete: {validCount} valid, {invalidCount} invalid",
                    invalidCount > 0 ? Colors.Orange : Colors.LimeGreen);
            }
            catch (Exception ex)
            {
                ShowStatus($"Error validating configurations: {ex.Message}", Colors.Red);
            }
        }

        // Deploy configurations to all components
        private async void DeployConfigs_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                ShowStatus("Deploying configurations...", Colors.Yellow);

                // Simulate deployment process
                await Task.Delay(2000);

                ShowStatus("Configuration deployment completed successfully", Colors.LimeGreen);
            }
            catch (Exception ex)
            {
                ShowStatus($"Error deploying configurations: {ex.Message}", Colors.Red);
            }
        }

        // Open HMI Dashboard
        private void OpenDashboard_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                string dashboardPath = Path.Combine(_workspacePath, "dashboard", "eq12_live_hmi.html");
                if (File.Exists(dashboardPath))
                {
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = dashboardPath,
                        UseShellExecute = true
                    });
                    ShowStatus("HMI Dashboard opened in browser", Colors.LimeGreen);
                }
                else
                {
                    ShowStatus("HMI Dashboard not found. Generate it first using the system scanner.", Colors.Orange);
                }
            }
            catch (Exception ex)
            {
                ShowStatus($"Error opening dashboard: {ex.Message}", Colors.Red);
            }
        }

        // Refresh system data
        private async void Refresh_Click(object sender, RoutedEventArgs e)
        {
            ShowStatus("Refreshing system data...", Colors.Yellow);
            await LoadSystemConfiguration();
            await UpdateSystemStatus();
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        protected override void OnClosed(EventArgs e)
        {
            _updateTimer?.Stop();
            _httpClient?.Dispose();
            base.OnClosed(e);
        }
    }
}