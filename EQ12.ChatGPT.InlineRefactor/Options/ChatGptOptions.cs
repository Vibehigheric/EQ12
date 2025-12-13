using System;
using System.ComponentModel;
using Microsoft.VisualStudio.Shell;

namespace EQ12.ChatGPT.InlineRefactor.Options
{
    public class ChatGptOptions : DialogPage
    {
        [Category("OpenAI")]
        [DisplayName("Service API Key")]
        [Description("Your OpenAI Service API key. Stored per-user on this machine.")]
        public string ApiKey { get; set; } = "";

        [Category("OpenAI")]
        [DisplayName("Model")]
        [Description("Model name for the Responses API (e.g., gpt-4o, gpt-4o-mini, gpt-4.1).")]
        public string Model { get; set; } = "gpt-4o-mini";

        [Category("Behavior")]
        [DisplayName("Action")]
        [Description("ReplaceSelection or InsertBelow")]
        public ReplaceBehavior ReplaceBehavior { get; set; } = ReplaceBehavior.ReplaceSelection;

        [Category("Prompting")]
        [DisplayName("Default Instruction")]
        [Description("Instruction sent to ChatGPT if you just click OK without typing anything.")]
        public string DefaultInstruction { get; set; } = "Refactor the selected code and return only the improved code without commentary.";
    }

    public enum ReplaceBehavior
    {
        ReplaceSelection,
        InsertBelow
    }


}
