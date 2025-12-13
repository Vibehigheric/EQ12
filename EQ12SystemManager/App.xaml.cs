using System;
using System.Configuration;
using System.Data;
using System.Windows;

namespace EQ12SystemManager
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Set up global exception handling
            this.DispatcherUnhandledException += App_DispatcherUnhandledException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;

            // Initialize application
            Current.ShutdownMode = ShutdownMode.OnMainWindowClose;
        }

        private void App_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            MessageBox.Show($"An unexpected error occurred:\n\n{e.Exception.Message}",
                          "EQ12 System Manager Error",
                          MessageBoxButton.OK,
                          MessageBoxImage.Error);
            e.Handled = true;
        }

        private void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            MessageBox.Show($"A critical error occurred:\n\n{e.ExceptionObject}",
                          "EQ12 System Manager Critical Error",
                          MessageBoxButton.OK,
                          MessageBoxImage.Error);
        }
    }
}