using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace EQ12.ChatGPT.InlineRefactor.Options
{
    [Guid("b5a7d74a-9d0c-4a44-9fb3-6c4f4d8b7e8a")]
    public sealed class ChatGptOptionsPage : DialogPage
    {
        [Category("OpenAI")]
        [DisplayName("Service API Key")]
        [Description("Your OpenAI Service API key. Stored per-user on this machine.")]
        public string OpenAiApiKey { get; set; } = "";

        [Category("OpenAI")]
        [DisplayName("Model")]
        [Description("Responses API model (e.g., gpt-4o, gpt-4o-mini, gpt-4.1).")]
        public string Model { get; set; } = "gpt-4o-mini";

        [Category("Behavior")]
        [DisplayName("Replace selection by default")]
        [Description("If true, replaces selection; if false, inserts the result below selection.")]
        public bool ReplaceByDefault { get; set; } = true;

        [Category("Prompting")]
        [DisplayName("Default instruction")]
        [Description("Instruction used when no custom instruction is supplied.")]
        public string DefaultInstruction { get; set; } =
            "Refactor the selected code and return only the improved code without commentary.";
    }
}
