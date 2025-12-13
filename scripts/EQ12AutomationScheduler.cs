using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Quartz;
using Quartz.Impl;

namespace EQ12.AutomationScheduler
{
    /// <summary>
    /// EQ12 Parlay Builder Job - Professional Sports Betting Automation
    /// Runs every 5-10 minutes to build parlays using reusable OpenAI prompts.
    /// </summary>
    [DisallowConcurrentExecution]
    public class EQ12ParlayBuilderJob : IJob
    {
        private readonly ILogger<EQ12ParlayBuilderJob> _logger;
        private readonly EQ12ResponsesClient _responsesClient;
        private readonly EQ12AlertingService _alertingService;
        
        // Expert betting configuration
        private const double MIN_EV_THRESHOLD = 0.05; // 5% minimum EV
        private const double MIN_KELLY_THRESHOLD = 0.02; // 2% Kelly minimum
        private const int MAX_PARLAY_LEGS = 4; // Professional limit
        private const int MIN_PARLAY_LEGS = 2;
        private const string LOGS_DIR = @"C:\EQ12\logs";

        public EQ12ParlayBuilderJob(
            ILogger<EQ12ParlayBuilderJob> logger,
            EQ12ResponsesClient responsesClient,
            EQ12AlertingService alertingService)
        {
            _logger = logger;
            _responsesClient = responsesClient;
            _alertingService = alertingService;
        }

        public async Task Execute(IJobExecutionContext context)
        {
            var jobStart = DateTime.UtcNow;
            _logger.LogInformation("🔄 EQ12 Parlay Builder Job Starting at {JobStart:yyyy-MM-dd HH:mm:ss} UTC", jobStart);

            try
            {
                // 1. Load latest odds legs
                var legsData = await LoadLatestOddsLegs();
                if (legsData?.Legs == null || !legsData.Legs.Any())
                {
                    _logger.LogWarning("⚠️ No odds legs available - skipping parlay building");
                    return;
                }

                _logger.LogInformation("📥 Loaded {LegCount} odds legs from ingest pipeline", legsData.Legs.Count);

                // 2. Filter to high-quality legs (expert criteria)
                var qualityLegs = FilterQualityLegs(legsData.Legs);
                if (qualityLegs.Count < MIN_PARLAY_LEGS)
                {
                    _logger.LogInformation("📊 Only {QualityCount} quality legs found - need at least {MinLegs} for parlays",
                        qualityLegs.Count, MIN_PARLAY_LEGS);
                    return;
                }

                _logger.LogInformation("✨ Found {QualityCount} quality legs meeting EV/Kelly thresholds", qualityLegs.Count);

                // 3. Build balanced parlays using reusable prompt
                var balancedParlays = await BuildBalancedParlays(qualityLegs);

                // 4. Build hooks-focused parlays using specialist prompt
                var hooksLegs = qualityLegs.Where(leg => leg.HookFlag).ToList();
                var hooksParlays = new List<ParlayResult>();
                
                if (hooksLegs.Count >= MIN_PARLAY_LEGS)
                {
                    hooksParlays = await BuildHooksParlays(hooksLegs);
                }

                // 5. Combine and rank all parlays
                var allParlays = balancedParlays.Concat(hooksParlays).ToList();
                var rankedParlays = RankParlaysByExpectedValue(allParlays);

                // 6. Alert on top parlays
                await ProcessParlayAlerts(rankedParlays);

                // 7. Persist results
                await PersistParlayResults(rankedParlays);

                var jobDuration = DateTime.UtcNow - jobStart;
                _logger.LogInformation("✅ Parlay Builder Job completed in {Duration:mm\\:ss}", jobDuration);
                _logger.LogInformation("📊 Generated {ParlayCount} parlays ({BalancedCount} balanced, {HooksCount} hooks)",
                    rankedParlays.Count, balancedParlays.Count, hooksParlays.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Parlay Builder Job failed");
                
                // Send failure alert
                await _alertingService.SendErrorAlert(
                    "EQ12 Parlay Builder Failed", 
                    $"Job execution failed at {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC\n\nError: {ex.Message}");
            }
        }

        private async Task<OddsLegsData> LoadLatestOddsLegs()
        {
            try
            {
                var latestFile = Path.Combine(LOGS_DIR, "latest_odds_legs.json");
                if (!File.Exists(latestFile))
                {
                    return null;
                }

                var json = await File.ReadAllTextAsync(latestFile);
                return JsonConvert.DeserializeObject<OddsLegsData>(json);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load latest odds legs");
                return null;
            }
        }

        private List<OddsLeg> FilterQualityLegs(List<OddsLeg> allLegs)
        {
            return allLegs.Where(leg => 
                leg.EV >= MIN_EV_THRESHOLD &&
                leg.Kelly >= MIN_KELLY_THRESHOLD &&
                leg.ModelProb > 0 &&
                IsUpcomingGame(leg.CommenceTimeUtc)
            ).ToList();
        }

        private bool IsUpcomingGame(string commenceTimeUtc)
        {
            try
            {
                var gameTime = DateTime.Parse(commenceTimeUtc).ToUniversalTime();
                var now = DateTime.UtcNow;
                var minutesToKickoff = (gameTime - now).TotalMinutes;
                
                // Games 30 minutes to 48 hours from now
                return minutesToKickoff >= 30 && minutesToKickoff <= 2880;
            }
            catch
            {
                return false;
            }
        }

        private async Task<List<ParlayResult>> BuildBalancedParlays(List<OddsLeg> legs)
        {
            try
            {
                _logger.LogInformation("🎯 Building balanced parlays using pmpt_eq12_build_parlay_v1");

                var parlayData = new
                {
                    legs = legs.Select(leg => new
                    {
                        book = leg.Book,
                        game_id = leg.GameId,
                        market = leg.Market,
                        selection = leg.Selection,
                        odds = leg.Odds,
                        point = leg.Point,
                        ev = leg.EV,
                        kelly = leg.Kelly,
                        hook_flag = leg.HookFlag
                    }).ToList(),
                    strategy = "balanced",
                    max_legs = MAX_PARLAY_LEGS,
                    min_total_ev = 0.12, // 12% minimum total EV
                    max_correlation_penalty = 0.05
                };

                // Use reusable prompt for balanced parlays
                var response = await _responsesClient.BuildParlayWithPromptId(
                    promptId: "pmpt_eq12_build_parlay_v1",
                    variables: new Dictionary<string, object>
                    {
                        { "parlay_data", JsonConvert.SerializeObject(parlayData, Formatting.None) }
                    },
                    reasoningEffort: "medium"
                );

                return ParseParlayResponse(response, "balanced");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to build balanced parlays");
                return new List<ParlayResult>();
            }
        }

        private async Task<List<ParlayResult>> BuildHooksParlays(List<OddsLeg> hooksLegs)
        {
            try
            {
                _logger.LogInformation("🎣 Building hooks-focused parlays using pmpt_eq12_spread_hooks_v1");

                var hooksData = new
                {
                    legs = hooksLegs.Select(leg => new
                    {
                        book = leg.Book,
                        game_id = leg.GameId,
                        market = leg.Market,
                        selection = leg.Selection,
                        odds = leg.Odds,
                        point = leg.Point,
                        hook_advantage = CalculateHookAdvantage(leg.Point ?? 0)
                    }).ToList(),
                    focus = "hooks_specialist",
                    key_numbers = new[] { 3, 7, 10, 14 }, // NFL key numbers
                    hook_bonus_multiplier = 1.15
                };

                // Use hooks specialist prompt
                var response = await _responsesClient.BuildHooksWithPromptId(
                    promptId: "pmpt_eq12_spread_hooks_v1",
                    variables: new Dictionary<string, object>
                    {
                        { "hooks_data", JsonConvert.SerializeObject(hooksData, Formatting.None) }
                    },
                    reasoningEffort: "medium"
                );

                return ParseParlayResponse(response, "hooks_specialist");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to build hooks parlays");
                return new List<ParlayResult>();
            }
        }

        private double CalculateHookAdvantage(double point)
        {
            var keyNumbers = new[] { 3, 7, 10, 14 };
            var distanceToKey = keyNumbers.Min(kn => Math.Abs(Math.Abs(point) - kn));
            
            if (Math.Abs(point % 1) == 0.5) // Is a hook
            {
                if (distanceToKey == 0.5) return 0.08; // Perfect hook
                if (distanceToKey <= 1) return 0.04;   // Near key number
            }
            
            return 0.0;
        }

        private List<ParlayResult> ParseParlayResponse(object response, string strategy)
        {
            try
            {
                // Parse OpenAI response into ParlayResult objects
                // Implementation depends on your response structure
                var parlays = new List<ParlayResult>();
                
                // This would parse the structured JSON response from the reusable prompts
                // For now, return empty list - implement based on your prompt output format
                
                return parlays;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to parse parlay response for strategy {Strategy}", strategy);
                return new List<ParlayResult>();
            }
        }

        private List<ParlayResult> RankParlaysByExpectedValue(List<ParlayResult> parlays)
        {
            return parlays
                .OrderByDescending(p => p.TotalEV)
                .ThenByDescending(p => p.TotalKelly)
                .ThenBy(p => p.Legs.Count)
                .ToList();
        }

        private async Task ProcessParlayAlerts(List<ParlayResult> rankedParlays)
        {
            var alertThreshold = 0.15; // 15% EV threshold for alerts
            var highEvParlays = rankedParlays.Where(p => p.TotalEV >= alertThreshold).Take(3).ToList();

            foreach (var parlay in highEvParlays)
            {
                await _alertingService.SendParlayAlert(parlay);
            }

            if (highEvParlays.Any())
            {
                _logger.LogInformation("🚨 Sent alerts for {AlertCount} high-EV parlays", highEvParlays.Count);
            }
        }

        private async Task PersistParlayResults(List<ParlayResult> parlays)
        {
            try
            {
                var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
                var resultFile = Path.Combine(LOGS_DIR, $"parlay_results_{timestamp}.json");

                var result = new
                {
                    timestamp_utc = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                    parlays_count = parlays.Count,
                    high_ev_count = parlays.Count(p => p.TotalEV >= 0.15),
                    parlays = parlays
                };

                var json = JsonConvert.SerializeObject(result, Formatting.Indented);
                await File.WriteAllTextAsync(resultFile, json);

                // Also update latest snapshot
                var latestFile = Path.Combine(LOGS_DIR, "latest_parlay_results.json");
                await File.WriteAllTextAsync(latestFile, json);

                _logger.LogInformation("💾 Persisted parlay results to {FileName}", Path.GetFileName(resultFile));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to persist parlay results");
            }
        }
    }

    /// <summary>
    /// EQ12 Automation Scheduler Service - Quartz.NET Host
    /// </summary>
    public class EQ12AutomationSchedulerService : BackgroundService
    {
        private readonly ILogger<EQ12AutomationSchedulerService> _logger;
        private readonly IServiceProvider _serviceProvider;
        private IScheduler _scheduler;

        public EQ12AutomationSchedulerService(
            ILogger<EQ12AutomationSchedulerService> logger,
            IServiceProvider serviceProvider)
        {
            _logger = logger;
            _serviceProvider = serviceProvider;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("🚀 EQ12 Automation Scheduler starting");

            try
            {
                // Create Quartz scheduler
                var factory = new StdSchedulerFactory();
                _scheduler = await factory.GetScheduler();
                
                // Configure DI for Quartz jobs
                _scheduler.JobFactory = new ServiceProviderJobFactory(_serviceProvider);

                // Schedule Parlay Builder Job - every 7 minutes (expert frequency)
                var parlayJobDetail = JobBuilder.Create<EQ12ParlayBuilderJob>()
                    .WithIdentity("EQ12ParlayBuilder", "EQ12Automation")
                    .Build();

                var parlayTrigger = TriggerBuilder.Create()
                    .WithIdentity("ParlayBuilderTrigger", "EQ12Automation")
                    .StartNow()
                    .WithSimpleSchedule(x => x
                        .WithIntervalInMinutes(7) // 7 minutes = professional frequency
                        .RepeatForever())
                    .Build();

                await _scheduler.ScheduleJob(parlayJobDetail, parlayTrigger);

                // Start the scheduler
                await _scheduler.Start();
                _logger.LogInformation("✅ EQ12 Automation Scheduler started - Parlay Builder every 7 minutes");

                // Keep running until cancellation
                while (!stoppingToken.IsCancellationRequested)
                {
                    await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ EQ12 Automation Scheduler failed");
            }
            finally
            {
                if (_scheduler != null)
                {
                    await _scheduler.Shutdown();
                    _logger.LogInformation("👋 EQ12 Automation Scheduler stopped");
                }
            }
        }
    }

    // Supporting classes for dependency injection and job execution
    public class ServiceProviderJobFactory : IJobFactory
    {
        private readonly IServiceProvider _serviceProvider;

        public ServiceProviderJobFactory(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider;
        }

        public IJob NewJob(TriggerFiredBundle bundle, IScheduler scheduler)
        {
            var jobType = bundle.JobDetail.JobType;
            return (IJob)_serviceProvider.GetRequiredService(jobType);
        }

        public void ReturnJob(IJob job)
        {
            // No-op for DI container managed instances
        }
    }

    // Data models for parlay processing
    public class OddsLegsData
    {
        public string TimestampUtc { get; set; }
        public int LegsCount { get; set; }
        public List<string> Books { get; set; }
        public List<OddsLeg> Legs { get; set; }
    }

    public class OddsLeg
    {
        public string Book { get; set; }
        public string GameId { get; set; }
        public string Market { get; set; }
        public string Selection { get; set; }
        public int Odds { get; set; }
        public double? Point { get; set; }
        public double ModelProb { get; set; }
        public double EV { get; set; }
        public double Kelly { get; set; }
        public bool HookFlag { get; set; }
        public string CommenceTimeUtc { get; set; }
        public string LastUpdateUtc { get; set; }
    }

    public class ParlayResult
    {
        public string Strategy { get; set; }
        public List<OddsLeg> Legs { get; set; }
        public double TotalEV { get; set; }
        public double TotalKelly { get; set; }
        public int TotalOdds { get; set; }
        public double CorrelationPenalty { get; set; }
        public string ReasoningTrace { get; set; }
    }
}