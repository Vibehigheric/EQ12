using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace EQ12.PlaygroundIntegration
{
    /// <summary>
    /// EQ12 C# Integration Example for Visual Studio
    /// Demonstrates how to use OpenAI Responses API with reusable prompt IDs
    /// for EQ12 parlay building workflows.
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            // Create host for dependency injection
            var host = CreateHostBuilder(args).Build();
            
            // Get the parlay service
            var parlayService = host.Services.GetRequiredService<EQ12ParlayService>();
            
            Console.WriteLine("🚀 EQ12 Visual Studio Integration Demo");
            Console.WriteLine("=".PadRight(50, '='));
            
            try
            {
                // Run demo scenarios
                await RunParlayArchitectDemo(parlayService);
                await RunHooksSpecialistDemo(parlayService);
                await RunAlertCopyDemo(parlayService);
                await RunWhatIfScenariosDemo(parlayService);
                
                Console.WriteLine("\n✅ All demos completed successfully!");
                Console.WriteLine("💡 Integrate these patterns into your EQ12 application");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("💡 Make sure OPENAI_API_KEY is set in user secrets or appsettings.json");
            }
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureServices((context, services) =>
                {
                    services.AddHttpClient();
                    services.AddSingleton<EQ12ParlayService>();
                });

        private static async Task RunParlayArchitectDemo(EQ12ParlayService service)
        {
            Console.WriteLine("\n1️⃣ Testing Parlay Architect (pmpt_eq12_build_parlay_v1)");
            
            // Sample candidate legs
            var candidateLegs = new[]
            {
                new
                {
                    book = "DraftKings",
                    game_id = "nfl_20251005_chiefs_bills",
                    market = "moneyline",
                    selection = "Kansas City Chiefs",
                    odds = -110,
                    model_prob = 0.55,
                    ev = 0.089
                },
                new
                {
                    book = "FanDuel",
                    game_id = "nfl_20251005_packers_bears",
                    market = "spread",
                    selection = "Green Bay Packers -6.5",
                    odds = -108,
                    point = -6.5,
                    model_prob = 0.58,
                    ev = 0.092,
                    hook_flag = true
                }
            };

            var result = await service.BuildParlayWithArchitect(
                candidateLegs: candidateLegs,
                maxLegs: 8,
                minEv: 0.08m,
                correlation: 0.08m,
                bankroll: 1000m
            );

            if (result.Success)
            {
                Console.WriteLine($"   ✅ Built parlay with {result.Data?.GetProperty("legs").GetArrayLength()} legs");
                Console.WriteLine($"   💰 Stake: ${result.Data?.GetProperty("stake").GetDecimal():F0}");
            }
            else
            {
                Console.WriteLine($"   ❌ Failed: {result.Error}");
            }
        }

        private static async Task RunHooksSpecialistDemo(EQ12ParlayService service)
        {
            Console.WriteLine("\n2️⃣ Testing Hooks Specialist (pmpt_eq12_spread_hooks_v1)");
            
            // Sample hook legs only
            var hookLegs = new[]
            {
                new
                {
                    book = "DraftKings",
                    game_id = "nfl_20251005_chiefs_bills",
                    market = "spread",
                    selection = "Kansas City Chiefs -3.5",
                    odds = -110,
                    point = -3.5,
                    model_prob = 0.55,
                    ev = 0.089,
                    hook_flag = true
                },
                new
                {
                    book = "FanDuel",
                    game_id = "nfl_20251005_packers_bears",
                    market = "total",
                    selection = "Over 47.5",
                    odds = 102,
                    point = 47.5,
                    model_prob = 0.52,
                    ev = 0.076,
                    hook_flag = true
                }
            };

            var result = await service.BuildHooksSpecialist(
                candidateLegs: hookLegs,
                maxLegs: 6,
                minEv: 0.08m,
                correlation: 0.08m,
                bankroll: 1000m
            );

            if (result.Success)
            {
                Console.WriteLine($"   ✅ Built hooks parlay with {result.Data?.GetProperty("legs").GetArrayLength()} legs");
                Console.WriteLine($"   ⚡ Hooks count: {result.Data?.GetProperty("hook_count").GetInt32()}");
            }
            else
            {
                Console.WriteLine($"   ❌ Failed: {result.Error}");
            }
        }

        private static async Task RunAlertCopyDemo(EQ12ParlayService service)
        {
            Console.WriteLine("\n3️⃣ Testing Alert Copy Generation (pmpt_eq12_alert_copy_v1)");

            var alertResult = await service.GenerateAlertCopy(
                book: "DraftKings",
                teamOrMarket: "Chiefs vs Bills", 
                selection: "Chiefs -3.5",
                odds: -110,
                evPercent: "8.2%",
                kelly: "45",
                kickoffLocal: "4:25p EST",
                why: "model loves hook"
            );

            if (alertResult.Success)
            {
                var alertText = alertResult.Data?.GetProperty("text").GetString();
                Console.WriteLine($"   ✅ Generated alert: {alertText}");
            }
            else
            {
                Console.WriteLine($"   ❌ Failed: {alertResult.Error}");
            }
        }

        private static async Task RunWhatIfScenariosDemo(EQ12ParlayService service)
        {
            Console.WriteLine("\n4️⃣ Running What-If Scenarios");

            var scenarios = new[]
            {
                new { Name = "Tight Correlation", Corr = 0.12m, MinEv = 0.08m },
                new { Name = "Raise EV Floor", Corr = 0.08m, MinEv = 0.12m },
                new { Name = "Aggressive", Corr = 0.05m, MinEv = 0.06m }
            };

            // Sample mixed legs for correlation testing
            var mixedLegs = new[]
            {
                new
                {
                    book = "DraftKings",
                    game_id = "nfl_20251005_chiefs_bills",
                    market = "moneyline",
                    selection = "Kansas City Chiefs",
                    odds = -165,
                    model_prob = 0.62,
                    ev = 0.081
                },
                new
                {
                    book = "FanDuel",
                    game_id = "nfl_20251005_chiefs_bills",
                    market = "total",
                    selection = "Over 51.5",
                    odds = -110,
                    point = 51.5,
                    model_prob = 0.57,
                    ev = 0.073,
                    hook_flag = true
                },
                new
                {
                    book = "BetMGM",
                    game_id = "nfl_20251005_packers_bears",
                    market = "spread", 
                    selection = "Chicago Bears +7.0",
                    odds = 110,
                    point = 7.0,
                    model_prob = 0.51,
                    ev = 0.067
                }
            };

            foreach (var scenario in scenarios)
            {
                Console.WriteLine($"   Testing: {scenario.Name}");

                var result = await service.BuildParlayWithArchitect(
                    candidateLegs: mixedLegs,
                    maxLegs: 8,
                    minEv: scenario.MinEv,
                    correlation: scenario.Corr,
                    bankroll: 1000m
                );

                if (result.Success)
                {
                    var legsCount = result.Data?.GetProperty("legs").GetArrayLength() ?? 0;
                    var stake = result.Data?.GetProperty("stake").GetDecimal() ?? 0;
                    Console.WriteLine($"     ✅ {legsCount} legs, ${stake:F0} stake");
                }
                else
                {
                    Console.WriteLine($"     ❌ Failed");
                }
            }
        }
    }

    /// <summary>
    /// Service class for EQ12 parlay operations using OpenAI Responses API
    /// </summary>
    public class EQ12ParlayService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<EQ12ParlayService> _logger;
        private readonly string _apiKey;
        private readonly string _baseUrl = "https://api.openai.com/v1";

        public EQ12ParlayService(
            HttpClient httpClient, 
            IConfiguration configuration,
            ILogger<EQ12ParlayService> logger)
        {
            _httpClient = httpClient;
            _configuration = configuration;
            _logger = logger;
            
            // Get API key from user secrets or appsettings
            _apiKey = _configuration["OpenAI:ApiKey"] ?? 
                      Environment.GetEnvironmentVariable("OPENAI_API_KEY") ??
                      throw new InvalidOperationException("OpenAI API key not found");

            // Configure HTTP client
            _httpClient.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Bearer", _apiKey);
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-CSharp/1.0");
        }

        /// <summary>
        /// Build parlay using the main architect prompt (pmpt_eq12_build_parlay_v1)
        /// </summary>
        public async Task<ApiResult> BuildParlayWithArchitect(
            object candidateLegs,
            int maxLegs = 8,
            decimal minEv = 0.08m,
            decimal correlation = 0.08m,
            decimal bankroll = 1000m,
            string reasoningEffort = "low")
        {
            var variables = new Dictionary<string, string>
            {
                ["allowed_books"] = "DraftKings,FanDuel,BetMGM",
                ["max_legs"] = maxLegs.ToString(),
                ["corr"] = correlation.ToString("F2"),
                ["min_ev"] = minEv.ToString("F2"),
                ["bankroll"] = bankroll.ToString("F0"),
                ["legs_json"] = JsonSerializer.Serialize(candidateLegs)
            };

            return await CallResponsesApi("pmpt_eq12_build_parlay_v1", variables, reasoningEffort);
        }

        /// <summary>
        /// Build hooks-focused parlay (pmpt_eq12_spread_hooks_v1)
        /// </summary>
        public async Task<ApiResult> BuildHooksSpecialist(
            object candidateLegs,
            int maxLegs = 6,
            decimal minEv = 0.08m,
            decimal correlation = 0.08m,
            decimal bankroll = 1000m,
            string reasoningEffort = "medium")
        {
            var variables = new Dictionary<string, string>
            {
                ["allowed_books"] = "DraftKings,FanDuel,BetMGM",
                ["max_legs"] = maxLegs.ToString(),
                ["corr"] = correlation.ToString("F2"),
                ["min_ev"] = minEv.ToString("F2"),
                ["bankroll"] = bankroll.ToString("F0"),
                ["legs_json"] = JsonSerializer.Serialize(candidateLegs)
            };

            return await CallResponsesApi("pmpt_eq12_spread_hooks_v1", variables, reasoningEffort);
        }

        /// <summary>
        /// Generate alert copy (pmpt_eq12_alert_copy_v1)
        /// </summary>
        public async Task<ApiResult> GenerateAlertCopy(
            string book,
            string teamOrMarket,
            string selection,
            int odds,
            string evPercent,
            string kelly,
            string kickoffLocal,
            string why)
        {
            var variables = new Dictionary<string, string>
            {
                ["book"] = book,
                ["team_or_market"] = teamOrMarket,
                ["selection"] = selection,
                ["odds"] = odds.ToString(),
                ["ev_pct"] = evPercent,
                ["kelly"] = kelly,
                ["kickoff_local"] = kickoffLocal,
                ["why"] = why
            };

            return await CallResponsesApi("pmpt_eq12_alert_copy_v1", variables, "low");
        }

        /// <summary>
        /// Core method to call OpenAI Responses API with prompt ID
        /// </summary>
        private async Task<ApiResult> CallResponsesApi(
            string promptId, 
            Dictionary<string, string> variables,
            string reasoningEffort = "low")
        {
            try
            {
                var requestBody = new
                {
                    model = "gpt-5", // Use gpt-4o until gpt-5 available
                    temperature = 0.2,
                    reasoning = new { effort = reasoningEffort },
                    prompt = new
                    {
                        id = promptId,
                        version = "current",
                        variables = variables
                    }
                };

                var json = JsonSerializer.Serialize(requestBody, new JsonSerializerOptions 
                { 
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase 
                });

                var content = new StringContent(json, Encoding.UTF8, "application/json");

                _logger.LogInformation($"Calling Responses API with prompt: {promptId}");

                var response = await _httpClient.PostAsync($"{_baseUrl}/responses", content);
                var responseText = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError($"API call failed: {response.StatusCode} - {responseText}");
                    return new ApiResult 
                    { 
                        Success = false, 
                        Error = $"API error: {response.StatusCode}" 
                    };
                }

                var responseData = JsonSerializer.Deserialize<JsonElement>(responseText);
                
                // Extract output based on response structure
                if (responseData.TryGetProperty("output_json", out var outputJson))
                {
                    return new ApiResult 
                    { 
                        Success = true, 
                        Data = outputJson,
                        TokensUsed = GetTokenUsage(responseData)
                    };
                }
                else if (responseData.TryGetProperty("output_text", out var outputText))
                {
                    var textData = JsonSerializer.Deserialize<JsonElement>($$"""{"text": "{{outputText.GetString()}}"}""");
                    return new ApiResult 
                    { 
                        Success = true, 
                        Data = textData,
                        TokensUsed = GetTokenUsage(responseData)
                    };
                }

                return new ApiResult 
                { 
                    Success = false, 
                    Error = "Unexpected response format" 
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error calling Responses API with prompt: {promptId}");
                return new ApiResult 
                { 
                    Success = false, 
                    Error = ex.Message 
                };
            }
        }

        private static int GetTokenUsage(JsonElement response)
        {
            return response.TryGetProperty("usage", out var usage) && 
                   usage.TryGetProperty("total_tokens", out var tokens) 
                   ? tokens.GetInt32() 
                   : 0;
        }
    }

    /// <summary>
    /// Result wrapper for API calls
    /// </summary>
    public class ApiResult
    {
        public bool Success { get; set; }
        public JsonElement? Data { get; set; }
        public string? Error { get; set; }
        public int TokensUsed { get; set; }
    }
}