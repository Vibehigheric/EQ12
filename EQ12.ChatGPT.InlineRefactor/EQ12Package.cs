using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;

namespace EQ12.ChatGPT.InlineRefactor
{
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("#110", "#112", "1.0")]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideOptionPage(typeof(Options.ChatGptOptionsPage), "EQ12", "ChatGPT", 0, 0, true)]
    [Guid(PackageGuidString)]
    public sealed class EQ12Package : AsyncPackage
    {
        public const string PackageGuidString = "44cc9b55-8b1c-4c10-86a1-cc4c6c854c6b";

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
            await Commands.SendToChatGptCommand.InitializeAsync(this);
        }
    }
}
