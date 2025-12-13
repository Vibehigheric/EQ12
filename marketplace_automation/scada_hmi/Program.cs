using System;
using System.Windows.Forms;

namespace EQ12.MarketplaceSCADA
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the EQ12 Marketplace SCADA application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            // Enable visual styles for modern Windows appearance
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            // Set up error handling
            Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
            Application.ThreadException += Application_ThreadException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;

            try
            {
                // Start the main SCADA HMI form
                Application.Run(new MarketplaceHMI());
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Critical error starting EQ12 Marketplace SCADA:\n\n{ex.Message}\n\nContact technical support.",
                    "EQ12 SCADA - Critical Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private static void Application_ThreadException(object sender, System.Threading.ThreadExceptionEventArgs e)
        {
            MessageBox.Show(
                $"Application error:\n\n{e.Exception.Message}\n\nPlease restart the SCADA system.",
                "EQ12 SCADA - Application Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            );
        }

        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            var exception = e.ExceptionObject as Exception;
            MessageBox.Show(
                $"Unhandled system error:\n\n{exception?.Message ?? "Unknown error"}\n\nSCADA system will terminate.",
                "EQ12 SCADA - System Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}