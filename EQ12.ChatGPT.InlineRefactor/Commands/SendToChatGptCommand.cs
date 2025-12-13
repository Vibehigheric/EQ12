using System;
using System.ComponentModel.Design;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using EnvDTE;
using EnvDTE80;
using Microsoft;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Task = System.Threading.Tasks.Task;

namespace EQ12.ChatGPT.InlineRefactor.Commands
{
    internal sealed class SendToChatGptCommand
    {
        public const int CommandId = 0x0100;
        public static readonly Guid CommandSet = new Guid("b4d6f713-2c10-4c20-9b09-17e3f9a66670");

        private readonly AsyncPackage _package;

        private SendToChatGptCommand(AsyncPackage package, OleMenuCommandService commandService)
        {
            _package = package ?? throw new ArgumentNullException(nameof(package));
            var cmdId = new CommandID(CommandSet, CommandId);
            var cmd = new OleMenuCommand(Execute, cmdId);
            commandService.AddCommand(cmd);
        }

        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            var commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Assumes.Present(commandService);

            _ = new SendToChatGptCommand(package, commandService);
        }

        private async void Execute(object sender, EventArgs e)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            try
            {
                var dte = await _package.GetServiceAsync(typeof(SDTE)) as DTE2;
                Assumes.Present(dte);

                if (dte.ActiveDocument == null)
                {
                    VsShellUtilities.ShowMessageBox(_package, "Open a code file and select some text.", "EQ12 → Send to ChatGPT", OLEMSGICON.OLEMSGICON_INFO, OLEMSGBUTTON.OLEMSGBUTTON_OK, OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
                    return;
                }

                var sel = (TextSelection)dte.ActiveDocument.Selection;
                var selectedText = sel?.Text ?? string.Empty;
                if (string.IsNullOrWhiteSpace(selectedText))
                {
                    VsShellUtilities.ShowMessageBox(_package, "Please select some code first.", "EQ12 → Send to ChatGPT", OLEMSGICON.OLEMSGICON_INFO, OLEMSGBUTTON.OLEMSGBUTTON_OK, OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
                    return;
                }

                // Load options
                var options = (Options.ChatGptOptions)_package.GetDialogPage(typeof(Options.ChatGptOptionsPage));

                // Prompt for API key if not set
                string apiKey = options.ApiKey;
                if (string.IsNullOrWhiteSpace(apiKey))
                {
                    apiKey = Microsoft.VisualBasic.Interaction.InputBox("Enter your OpenAI API Key:", "EQ12 → API Key Required", "");
                    if (string.IsNullOrWhiteSpace(apiKey))
                    {
                        VsShellUtilities.ShowMessageBox(_package, "API Key is required to use ChatGPT functionality.", "EQ12 → Send to ChatGPT", OLEMSGICON.OLEMSGICON_WARNING, OLEMSGBUTTON.OLEMSGBUTTON_OK, OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
                        return;
                    }
                    
                    // Optionally save the API key to options for future use
                    var saveResult = MessageBox.Show("Would you like to save this API key for future use?\n\n(It will be stored locally on your machine)", "Save API Key", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
                    if (saveResult == DialogResult.Yes)
                    {
                        options.ApiKey = apiKey;
                        options.SaveSettingsToStorage();
                    }
                }

                // Prompt for instruction
                var instruction = Microsoft.VisualBasic.Interaction.InputBox("Describe what ChatGPT should do with the selection (leave blank to use default).", "EQ12 → Send to ChatGPT", options.DefaultInstruction);
                if (instruction is null)
                {
                    return; // Cancelled
                }

                // Call OpenAI
                using var cts = new CancellationTokenSource(TimeSpan.FromMinutes(2));
                var client = new Services.OpenAiClient();
                string result = await client.CreateResponseAsync(apiKey, options.Model, instruction, selectedText, cts.Token);

                if (string.IsNullOrWhiteSpace(result))
                {
                    VsShellUtilities.ShowMessageBox(_package, "Empty response from ChatGPT.", "EQ12 → Send to ChatGPT", OLEMSGICON.OLEMSGICON_WARNING, OLEMSGBUTTON.OLEMSGBUTTON_OK, OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
                    return;
                }

                // Clean result: if it contains fenced code, extract inside ```
                var cleaned = TryExtractCodeFence(result);

                // Replace or insert
                if (options.ReplaceBehavior == Options.ReplaceBehavior.ReplaceSelection)
                {
                    sel.Delete();
                    sel.Insert(cleaned, (int)EnvDTE.vsInsertFlags.vsInsertFlagsContainNewText);
                }
                else
                {
                    sel.MoveToPoint(sel.ActivePoint);
                    sel.NewLine();
                    sel.Insert(cleaned, (int)EnvDTE.vsInsertFlags.vsInsertFlagsContainNewText);
                    sel.NewLine();
                }
            }
            catch (Exception ex)
            {
                VsShellUtilities.ShowMessageBox(_package, ex.Message, "EQ12 → Send to ChatGPT (Error)", OLEMSGICON.OLEMSGICON_CRITICAL, OLEMSGBUTTON.OLEMSGBUTTON_OK, OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
            }
        }

        private static string TryExtractCodeFence(string input)
        {
            if (string.IsNullOrEmpty(input)) return input;

            // Simple extraction between first pair of triple backticks
            var start = input.IndexOf("```");
            if (start >= 0)
            {
                var end = input.IndexOf("```", start + 3);
                if (end > start + 3)
                {
                    return input.Substring(start + 3, end - (start + 3)).Trim();
                }
            }
            return input.Trim();
        }
    }
}
