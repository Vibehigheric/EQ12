#nullable enable
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;

namespace EQ12.ChatGPT.InlineRefactor.Services
{
    internal class OpenAiClient
    {
        private readonly HttpClient _http;

        public OpenAiClient(HttpClient? httpClient = null)
        {
            _http = httpClient ?? new HttpClient();
            _http.Timeout = TimeSpan.FromSeconds(90);
            _http.DefaultRequestHeaders.UserAgent.ParseAdd("EQ12-VSIX/1.0");
        }

        public async Task<string> CreateResponseAsync(string apiKey, string model, string instruction, string selectedCode, CancellationToken ct)
        {
            if (string.IsNullOrWhiteSpace(apiKey))
                throw new InvalidOperationException("OpenAI API key is not configured. Set it under Tools → Options → EQ12 → ChatGPT.");

            var endpoint = "https://api.openai.com/v1/chat/completions";

            using var req = new HttpRequestMessage(HttpMethod.Post, endpoint);
            req.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", apiKey);

            var payload = new
            {
                model = model,
                messages = new[]
                {
                    new { role = "user", content = BuildPrompt(instruction, selectedCode) }
                },
                temperature = 0.2,
                max_tokens = 2000
            };

            var json = JsonSerializer.Serialize(payload);
            req.Content = new StringContent(json, Encoding.UTF8, "application/json");

            using var resp = await _http.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct).ConfigureAwait(false);
            var body = await resp.Content.ReadAsStringAsync().ConfigureAwait(false);

            if (!resp.IsSuccessStatusCode)
            {
                throw new InvalidOperationException($"OpenAI API error ({(int)resp.StatusCode}): {body}");
            }

            try
            {
                using var doc = JsonDocument.Parse(body);
                // Prefer 'output_text' when available (Responses API), otherwise try common fallbacks.
                if (doc.RootElement.TryGetProperty("output_text", out var outputTextProp))
                {
                    return outputTextProp.GetString() ?? "";
                }

                // Fallback: responses[].content[].text (older/alt schema)
                if (doc.RootElement.TryGetProperty("output", out var outputArr) && outputArr.ValueKind == JsonValueKind.Array)
                {
                    foreach (var item in outputArr.EnumerateArray())
                    {
                        if (item.TryGetProperty("content", out var contentArr) && contentArr.ValueKind == JsonValueKind.Array)
                        {
                            foreach (var c in contentArr.EnumerateArray())
                            {
                                if (c.TryGetProperty("text", out var textProp))
                                {
                                    var s = textProp.GetString();
                                    if (!string.IsNullOrWhiteSpace(s))
                                        return s!;
                                }
                            }
                        }
                    }
                }

                // Last resort: return the raw JSON body (so user sees something)
                return body;
            }
            catch (Exception)
            {
                return body;
            }
        }

        private static string BuildPrompt(string instruction, string code)
        {
            var header = "You are a senior .NET/VB/C# engineer. When asked to modify code, respond with CODE ONLY. If replacement is intended, return just the revised code. Avoid explanations unless explicitly requested.";
            var sb = new StringBuilder();
            sb.AppendLine(header);
            sb.AppendLine();
            sb.AppendLine("Task:");
            sb.AppendLine(instruction?.Trim() ?? "");
            sb.AppendLine();
            sb.AppendLine("Selected code:");
            sb.AppendLine("```");
            sb.AppendLine(code ?? string.Empty);
            sb.AppendLine("```");
            return sb.ToString();
        }
    }
}
