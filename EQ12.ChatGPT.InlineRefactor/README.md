# EQ12 — Send to ChatGPT (Inline Refactor) — Visual Studio 2022 VSIX

Right‑click selected code → **Send to ChatGPT…**. The extension calls the **OpenAI Responses API** and either **replaces the selection** or **inserts below**, based on your preference in *Tools → Options → EQ12 → ChatGPT*.

> Uses only `HttpClient` (no extra SDKs). You can later swap in the official OpenAI .NET SDK if you prefer.

## Build (on your EQ12)

1. Install **Visual Studio 2022** with the **Visual Studio extension development** workload.
2. Open `EQ12.ChatGPT.InlineRefactor.csproj`.
3. Restore packages and **Build**. This produces a `.vsix` in the `bin\Debug` or `bin\Release` folder.
4. Double‑click the `.vsix` to install (or run `VSIXInstaller.exe /quiet your.vsix`).

## Configure

- In VS: **Tools → Options → EQ12 → ChatGPT**:
  - **Service API Key**: your OpenAI service key (kept per‑user on this PC).
  - **Model**: e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`. Keep this editable so you can move fast.
  - **Action**: ReplaceSelection or InsertBelow.
  - **Default Instruction**: used when you don’t type a custom instruction.

## Use

- Select code in the editor → right‑click → **Send to ChatGPT…**
- Enter an instruction (or just press **OK** to use your default), e.g.:
  - “Refactor to async/await and add XML docs.”
  - “Convert C# to VB.NET.”
  - “Add argument validation and early returns.”
  - “Explain the bug and fix it.” (the response may include prose—toggle your instruction accordingly)

The extension extracts fenced code blocks from the response and inserts/replaces accordingly.

## Security notes

- Your API key is **never** sent anywhere except directly to `https://api.openai.com/v1/responses`.
- The key is stored by Visual Studio’s user settings (per‑user). **Do not** commit it to source control.
- Consider setting the `OPENAI_API_KEY` environment variable and copying it manually if you prefer not to store in VS options.

## Swap to the official .NET SDK (optional)

If you prefer the official SDK, add the NuGet package and replace `OpenAiClient` with the SDK’s `OpenAI.Responses` client.

Official docs & SDK:
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- .NET SDK: https://github.com/openai/openai-dotnet

## PowerShell: quick install after build

```powershell
$vsix = Get-ChildItem -Recurse -Filter *.vsix | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$installer = "${env:ProgramFiles(x86)}\Microsoft Visual Studio2\Community\Common7\IDE\VSIXInstaller.exe"
if (-not (Test-Path $installer)) {
  $installer = "${env:ProgramFiles(x86)}\Microsoft Visual Studio2\Professional\Common7\IDE\VSIXInstaller.exe"
}
if (-not (Test-Path $installer)) {
  $installer = "${env:ProgramFiles(x86)}\Microsoft Visual Studio2\Enterprise\Common7\IDE\VSIXInstaller.exe"
}
& $installer $vsix.FullName
```

## Troubleshooting

- If you see **“OpenAI API error (401)”**, check your API key (Tools → Options) and account balance/permissions.
- If the response contains both prose and code, we try to auto‑extract fenced code blocks. Tighten your instruction to “Return code only.”
- If you hit timeouts, increase your network timeout or shorten the selection.

---

© PivotPoint Global Holdings — Built for the EQ12 automation stack.
