using System;
using System.Threading;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text;
using System.Text.Json;

namespace EQ12.ChatGPT.TestConsole
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("=== EQ12 ChatGPT API Key Test Console ===\n");
            
            // Prompt for API Key
            Console.Write("Enter your OpenAI API Key: ");
            string apiKey = Console.ReadLine()?.Trim() ?? "";
            
            if (string.IsNullOrWhiteSpace(apiKey))
            {
                Console.WriteLine("❌ API Key is required! Exiting...");
                return;
            }
            
            // Prompt for model (optional)
            Console.Write("Enter model name (default: gpt-4o-mini): ");
            string model = Console.ReadLine()?.Trim();
            if (string.IsNullOrWhiteSpace(model))
                model = "gpt-4o-mini";
            
            // Prompt for code to refactor
            Console.WriteLine("\nEnter the code you want to refactor (press Enter twice to finish):");
            StringBuilder codeBuilder = new StringBuilder();
            string line;
            int emptyLines = 0;
            
            while ((line = Console.ReadLine()) != null)
            {
                if (string.IsNullOrEmpty(line))
                {
                    emptyLines++;
                    if (emptyLines >= 2)
                        break;
                }
                else
                {
                    emptyLines = 0;
                }
                codeBuilder.AppendLine(line);
            }
            
            string codeToRefactor = codeBuilder.ToString().Trim();
            if (string.IsNullOrWhiteSpace(codeToRefactor))
            {
                Console.WriteLine("❌ No code provided! Exiting...");
                return;
            }
            
            // Prompt for instruction
            Console.Write("\nEnter refactoring instruction (default: 'Refactor and improve this code'): ");
            string instruction = Console.ReadLine()?.Trim();
            if (string.IsNullOrWhiteSpace(instruction))
                instruction = "Refactor the following code and return only the improved code without commentary.";
                
            // Test the API call
            Console.WriteLine("\n🔄 Sending request to OpenAI...\n");
            
            try
            {
                using var client = new TestOpenAiClient();
                using var cts = new CancellationTokenSource(TimeSpan.FromMinutes(2));
                
                string result = await client.SendAsync(apiKey, model, instruction, codeToRefactor, cts.Token);
                
                Console.WriteLine("✅ Response received successfully!");
                Console.WriteLine("\n=== REFACTORED CODE ===");
                Console.WriteLine(result);
                Console.WriteLine("=== END ===\n");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error: {ex.Message}");
                if (ex.InnerException != null)
                    Console.WriteLine($"   Inner: {ex.InnerException.Message}");
            }
            
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
    
    public class TestOpenAiClient : IDisposable
    {
        private readonly HttpClient _http;

        public TestOpenAiClient()
        {
            _http = new HttpClient();
            _http.Timeout = TimeSpan.FromSeconds(90);
            _http.DefaultRequestHeaders.UserAgent.ParseAdd("EQ12-TestConsole/1.0");
        }

        public async Task<string> SendAsync(string apiKey, string model, string instruction, string selectedCode, CancellationToken ct)
        {
            if (string.IsNullOrWhiteSpace(apiKey))
                throw new InvalidOperationException("OpenAI API key is required.");

            var payload = new
            {
                model = model,
                messages = new[]
                {
                    new { role = "system", content = instruction },
                    new { role = "user", content = selectedCode }
                },
                max_tokens = 2048,
                temperature = 0.2
            };

            var jsonContent = JsonSerializer.Serialize(payload);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

            _http.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", apiKey);

            var response = await _http.PostAsync("https://api.openai.com/v1/chat/completions", content, ct);
            var responseText = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new InvalidOperationException($"OpenAI API error ({response.StatusCode}): {responseText}");
            }

            using var jsonDoc = JsonDocument.Parse(responseText);
            var choices = jsonDoc.RootElement.GetProperty("choices");
            if (choices.GetArrayLength() > 0)
            {
                var message = choices[0].GetProperty("message").GetProperty("content").GetString();
                return TryExtractCodeFence(message ?? "");
            }

            return "No response from OpenAI.";
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

        public void Dispose()
        {
            _http?.Dispose();
        }
    }
}