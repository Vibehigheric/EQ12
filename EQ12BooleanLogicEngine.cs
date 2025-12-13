using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace EQ12.BooleanLogic
{
    /// <summary>
    /// EQ12 BOOLEAN LOGIC ENGINE - C# IMPLEMENTATION
    /// Advanced Boolean logic for sports betting automation and parlay validation
    /// Integrates with EQ12 NCAA Week 7 conference system
    /// </summary>
    public class EQ12BooleanLogicEngine
    {
        // System condition properties
        public bool UserLoggedIn { get; set; } = false;
        public bool HasAdminRights { get; set; } = false;
        public bool HasVipAccess { get; set; } = false;
        public bool BettingWindowOpen { get; set; } = false;
        public bool MaintenanceMode { get; set; } = false;
        public bool SufficientBankroll { get; set; } = false;
        public bool GameStarted { get; set; } = false;
        public bool LiveOddsAvailable { get; set; } = false;
        public bool EmergencyOverride { get; set; } = false;
        public bool ApiKeysValid { get; set; } = false;

        // EQ12 specific conditions
        public bool NCAAWeek7Active { get; set; } = false;
        public bool ParlayGenerationEnabled { get; set; } = false;
        public bool ConferenceDataLoaded { get; set; } = false;
        public bool SentimentAnalysisReady { get; set; } = false;

        private string EQ12Root { get; set; }
        private List<string> LogEntries { get; set; }

        public EQ12BooleanLogicEngine(string eq12Root = @"C:\EQ12")
        {
            EQ12Root = eq12Root;
            LogEntries = new List<string>();
            Console.WriteLine("🔧 EQ12 Boolean Logic Engine (C#) initialized");
            LogEntry("Boolean Logic Engine startup complete");
        }

        private void LogEntry(string message)
        {
            string logMessage = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} - {message}";
            LogEntries.Add(logMessage);
        }

        /// <summary>
        /// Demonstrate AND operator - ALL conditions must be True
        /// Critical for security and risk management in betting systems
        /// </summary>
        public Dictionary<string, bool> DemonstrateAndOperator()
        {
            Console.WriteLine("\n🔒 AND OPERATOR DEMONSTRATION (C#)");
            Console.WriteLine(new string('=', 50));

            var results = new Dictionary<string, bool>();

            // 1. Admin betting access (requires login AND admin rights)
            bool adminBetting = UserLoggedIn && HasAdminRights;
            results["admin_betting"] = adminBetting;

            string status = adminBetting ? "✅ GRANTED" : "❌ DENIED";
            Console.WriteLine($"Admin Betting Access: {status}");

            if (!adminBetting)
            {
                var missing = new List<string>();
                if (!UserLoggedIn) missing.Add("Login");
                if (!HasAdminRights) missing.Add("Admin Rights");
                Console.WriteLine($"   Missing: {string.Join(", ", missing)}");
            }

            // 2. Standard parlay placement (multiple AND conditions)
            bool parlayPlacement = UserLoggedIn &&
                                  BettingWindowOpen &&
                                  SufficientBankroll &&
                                  !MaintenanceMode &&
                                  ApiKeysValid;

            results["parlay_placement"] = parlayPlacement;
            status = parlayPlacement ? "✅ AUTHORIZED" : "❌ BLOCKED";
            Console.WriteLine($"Parlay Placement: {status}");

            // 3. NCAA Week 7 system ready (EQ12 specific)
            bool ncaaSystemReady = NCAAWeek7Active &&
                                  ConferenceDataLoaded &&
                                  SentimentAnalysisReady &&
                                  LiveOddsAvailable;

            results["ncaa_system_ready"] = ncaaSystemReady;
            status = ncaaSystemReady ? "✅ READY" : "❌ NOT READY";
            Console.WriteLine($"NCAA Week 7 System: {status}");

            LogEntry($"AND operator results: {JsonSerializer.Serialize(results)}");
            return results;
        }

        /// <summary>
        /// Demonstrate OR operator - ANY condition can grant access
        /// Used for flexible access control and emergency overrides
        /// </summary>
        public Dictionary<string, bool> DemonstrateOrOperator()
        {
            Console.WriteLine("\n🚪 OR OPERATOR DEMONSTRATION (C#)");
            Console.WriteLine(new string('=', 50));

            var results = new Dictionary<string, bool>();

            // 1. Betting access (window open OR admin override OR VIP access)
            bool bettingAccess = BettingWindowOpen ||
                                HasAdminRights ||
                                HasVipAccess ||
                                EmergencyOverride;

            results["betting_access"] = bettingAccess;
            string status = bettingAccess ? "✅ ALLOWED" : "❌ DENIED";
            Console.WriteLine($"Betting Access: {status}");

            if (bettingAccess)
            {
                var reasons = new List<string>();
                if (BettingWindowOpen) reasons.Add("Window Open");
                if (HasAdminRights) reasons.Add("Admin Override");
                if (HasVipAccess) reasons.Add("VIP Access");
                if (EmergencyOverride) reasons.Add("Emergency Override");
                Console.WriteLine($"   Granted via: {string.Join(", ", reasons)}");
            }

            // 2. Live betting availability
            bool liveBetting = GameStarted ||
                              LiveOddsAvailable ||
                              HasAdminRights;

            results["live_betting"] = liveBetting;
            status = liveBetting ? "✅ AVAILABLE" : "❌ UNAVAILABLE";
            Console.WriteLine($"Live Betting: {status}");

            // 3. Data source availability (backup systems)
            bool dataAvailable = LiveOddsAvailable ||
                                ConferenceDataLoaded ||
                                SentimentAnalysisReady;

            results["data_available"] = dataAvailable;
            status = dataAvailable ? "✅ OPERATIONAL" : "❌ NO DATA";
            Console.WriteLine($"Data Sources: {status}");

            LogEntry($"OR operator results: {JsonSerializer.Serialize(results)}");
            return results;
        }

        /// <summary>
        /// Demonstrate NOT operator - Logical inversion
        /// Critical for safety checks and inverse conditions
        /// </summary>
        public Dictionary<string, bool> DemonstrateNotOperator()
        {
            Console.WriteLine("\n🔄 NOT OPERATOR DEMONSTRATION (C#)");
            Console.WriteLine(new string('=', 50));

            var results = new Dictionary<string, bool>();

            // 1. System operational (NOT in maintenance)
            bool systemOperational = !MaintenanceMode;
            results["system_operational"] = systemOperational;

            string status = systemOperational ? "✅ OPERATIONAL" : "⚠️ MAINTENANCE";
            Console.WriteLine($"System Status: {status}");

            // 2. Betting window status
            bool windowOpen = BettingWindowOpen; // Direct for clarity
            results["window_status"] = windowOpen;

            status = windowOpen ? "✅ OPEN" : "❌ CLOSED";
            Console.WriteLine($"Betting Window: {status}");

            // 3. Security check (NOT admin attempting admin functions)
            bool securityViolation = UserLoggedIn &&
                                    !HasAdminRights &&
                                    HasVipAccess; // VIP trying admin functions

            results["security_check"] = !securityViolation;
            status = !securityViolation ? "✅ SECURE" : "⚠️ VIOLATION";
            Console.WriteLine($"Security Status: {status}");

            // 4. Risk management (NOT exceeding limits)
            bool withinLimits = !(SufficientBankroll &&
                                 !HasVipAccess &&
                                 BettingWindowOpen); // High risk scenario

            results["risk_managed"] = withinLimits;
            status = withinLimits ? "✅ SAFE" : "⚠️ HIGH RISK";
            Console.WriteLine($"Risk Level: {status}");

            LogEntry($"NOT operator results: {JsonSerializer.Serialize(results)}");
            return results;
        }

        /// <summary>
        /// Demonstrate XOR operator - Exactly ONE condition must be True
        /// Used for exclusive states and security validation
        /// </summary>
        public Dictionary<string, bool> DemonstrateXorOperator()
        {
            Console.WriteLine("\n⚖️ XOR OPERATOR DEMONSTRATION (C#)");
            Console.WriteLine(new string('=', 50));

            var results = new Dictionary<string, bool>();

            // 1. Exclusive access control (Admin XOR VIP, not both for security)
            bool exclusiveAccess = HasAdminRights ^ HasVipAccess;
            results["exclusive_access"] = exclusiveAccess;

            if (HasAdminRights && HasVipAccess)
            {
                Console.WriteLine("⚠️ SECURITY ALERT: Both Admin and VIP active");
            }
            else if (exclusiveAccess)
            {
                string accessType = HasAdminRights ? "Admin" : "VIP";
                Console.WriteLine($"✅ Exclusive Access: {accessType} only");
            }
            else
            {
                Console.WriteLine("❌ No special access granted");
            }

            // 2. System state validation (Maintenance XOR Normal operation)
            bool validState = MaintenanceMode ^ (BettingWindowOpen && ParlayGenerationEnabled);
            results["valid_system_state"] = validState;

            string status = validState ? "✅ VALID" : "⚠️ CONFLICTED";
            Console.WriteLine($"System State: {status}");

            // 3. Data source priority (Live odds XOR Historical data)
            bool dataPriority = LiveOddsAvailable ^ ConferenceDataLoaded;
            results["data_priority"] = dataPriority;

            if (dataPriority)
            {
                string source = LiveOddsAvailable ? "Live Odds" : "Historical Data";
                Console.WriteLine($"✅ Data Source: {source} (exclusive)");
            }
            else
            {
                Console.WriteLine("⚠️ Data Source: Conflict or neither available");
            }

            LogEntry($"XOR operator results: {JsonSerializer.Serialize(results)}");
            return results;
        }

        /// <summary>
        /// Complex Boolean logic for EQ12 parlay validation and placement
        /// Combines multiple operators for sophisticated decision making
        /// </summary>
        public Dictionary<string, object> ComplexParlayValidation()
        {
            Console.WriteLine("\n🎯 COMPLEX PARLAY VALIDATION LOGIC (C#)");
            Console.WriteLine(new string('=', 50));

            var results = new Dictionary<string, object>();

            // 1. Parlay Authorization Matrix
            bool parlayAuthorized = ((UserLoggedIn &&
                                     SufficientBankroll &&
                                     BettingWindowOpen) &&
                                    !MaintenanceMode &&
                                    (LiveOddsAvailable ||
                                     HasAdminRights));

            results["parlay_authorized"] = parlayAuthorized;
            string status = parlayAuthorized ? "✅ AUTHORIZED" : "❌ BLOCKED";
            Console.WriteLine($"Parlay Authorization: {status}");

            // 2. Risk Assessment Logic
            bool highRisk = ((!HasVipAccess && SufficientBankroll) ||
                            (HasAdminRights &&
                             BettingWindowOpen &&
                             !MaintenanceMode));

            results["high_risk_detected"] = highRisk;
            if (highRisk)
            {
                Console.WriteLine("⚠️ High Risk Betting: Enhanced monitoring enabled");
            }

            // 3. NCAA Week 7 Conference Logic
            bool ncaaReady = (NCAAWeek7Active &&
                             ConferenceDataLoaded &&
                             SentimentAnalysisReady &&
                             (LiveOddsAvailable || HasAdminRights) &&
                             !(MaintenanceMode && !EmergencyOverride));

            results["ncaa_week7_ready"] = ncaaReady;
            status = ncaaReady ? "✅ READY" : "❌ NOT READY";
            Console.WriteLine($"NCAA Week 7 System: {status}");

            // 4. Emergency Access Protocol
            bool emergencyAccess = (HasAdminRights &&
                                   (MaintenanceMode || !BettingWindowOpen) &&
                                   ApiKeysValid);

            results["emergency_access"] = emergencyAccess;
            if (emergencyAccess)
            {
                Console.WriteLine("🚨 Emergency Access: Admin override protocols active");
            }

            // 5. Automated Decision Score
            bool[] decisionFactors = {
                parlayAuthorized,
                !highRisk,
                ncaaReady,
                ApiKeysValid,
                !MaintenanceMode
            };

            double decisionScore = 0;
            foreach (bool factor in decisionFactors)
            {
                if (factor) decisionScore++;
            }
            decisionScore /= decisionFactors.Length;

            results["decision_score"] = decisionScore;

            string decision;
            if (decisionScore >= 0.8)
                decision = "✅ PROCEED WITH CONFIDENCE";
            else if (decisionScore >= 0.6)
                decision = "⚠️ PROCEED WITH CAUTION";
            else if (decisionScore >= 0.4)
                decision = "🔍 MANUAL REVIEW REQUIRED";
            else
                decision = "❌ SYSTEM HOLD - DO NOT PROCEED";

            Console.WriteLine($"Automated Decision: {decision} (Score: {decisionScore:P0})");
            results["final_decision"] = decision;

            LogEntry($"Complex validation results: {JsonSerializer.Serialize(results)}");
            return results;
        }

        /// <summary>
        /// Update system conditions for Boolean evaluation
        /// </summary>
        public void UpdateSystemState(
            bool? userLoggedIn = null,
            bool? hasAdminRights = null,
            bool? hasVipAccess = null,
            bool? bettingWindowOpen = null,
            bool? maintenanceMode = null,
            bool? sufficientBankroll = null,
            bool? gameStarted = null,
            bool? liveOddsAvailable = null,
            bool? emergencyOverride = null,
            bool? apiKeysValid = null,
            bool? ncaaWeek7Active = null,
            bool? parlayGenerationEnabled = null,
            bool? conferenceDataLoaded = null,
            bool? sentimentAnalysisReady = null)
        {
            if (userLoggedIn.HasValue) { UserLoggedIn = userLoggedIn.Value; LogEntry($"Updated: UserLoggedIn = {userLoggedIn.Value}"); }
            if (hasAdminRights.HasValue) { HasAdminRights = hasAdminRights.Value; LogEntry($"Updated: HasAdminRights = {hasAdminRights.Value}"); }
            if (hasVipAccess.HasValue) { HasVipAccess = hasVipAccess.Value; LogEntry($"Updated: HasVipAccess = {hasVipAccess.Value}"); }
            if (bettingWindowOpen.HasValue) { BettingWindowOpen = bettingWindowOpen.Value; LogEntry($"Updated: BettingWindowOpen = {bettingWindowOpen.Value}"); }
            if (maintenanceMode.HasValue) { MaintenanceMode = maintenanceMode.Value; LogEntry($"Updated: MaintenanceMode = {maintenanceMode.Value}"); }
            if (sufficientBankroll.HasValue) { SufficientBankroll = sufficientBankroll.Value; LogEntry($"Updated: SufficientBankroll = {sufficientBankroll.Value}"); }
            if (gameStarted.HasValue) { GameStarted = gameStarted.Value; LogEntry($"Updated: GameStarted = {gameStarted.Value}"); }
            if (liveOddsAvailable.HasValue) { LiveOddsAvailable = liveOddsAvailable.Value; LogEntry($"Updated: LiveOddsAvailable = {liveOddsAvailable.Value}"); }
            if (emergencyOverride.HasValue) { EmergencyOverride = emergencyOverride.Value; LogEntry($"Updated: EmergencyOverride = {emergencyOverride.Value}"); }
            if (apiKeysValid.HasValue) { ApiKeysValid = apiKeysValid.Value; LogEntry($"Updated: ApiKeysValid = {apiKeysValid.Value}"); }
            if (ncaaWeek7Active.HasValue) { NCAAWeek7Active = ncaaWeek7Active.Value; LogEntry($"Updated: NCAAWeek7Active = {ncaaWeek7Active.Value}"); }
            if (parlayGenerationEnabled.HasValue) { ParlayGenerationEnabled = parlayGenerationEnabled.Value; LogEntry($"Updated: ParlayGenerationEnabled = {parlayGenerationEnabled.Value}"); }
            if (conferenceDataLoaded.HasValue) { ConferenceDataLoaded = conferenceDataLoaded.Value; LogEntry($"Updated: ConferenceDataLoaded = {conferenceDataLoaded.Value}"); }
            if (sentimentAnalysisReady.HasValue) { SentimentAnalysisReady = sentimentAnalysisReady.Value; LogEntry($"Updated: SentimentAnalysisReady = {sentimentAnalysisReady.Value}"); }
        }

        /// <summary>
        /// Run comprehensive Boolean logic demonstration for EQ12 system
        /// </summary>
        public Dictionary<string, object> RunComprehensiveDemo()
        {
            Console.WriteLine("🏈 EQ12 BOOLEAN LOGIC ENGINE - C# COMPREHENSIVE DEMONSTRATION");
            Console.WriteLine(new string('=', 70));

            // Set example conditions
            UpdateSystemState(
                userLoggedIn: true,
                hasAdminRights: false,
                hasVipAccess: false,
                bettingWindowOpen: true,
                maintenanceMode: false,
                sufficientBankroll: true,
                gameStarted: false,
                liveOddsAvailable: true,
                emergencyOverride: false,
                apiKeysValid: true,
                ncaaWeek7Active: true,
                parlayGenerationEnabled: true,
                conferenceDataLoaded: true,
                sentimentAnalysisReady: true
            );

            Console.WriteLine("\n📊 Current System State:");
            Console.WriteLine($"   {(UserLoggedIn ? "✅" : "❌")} User Logged In: {UserLoggedIn}");
            Console.WriteLine($"   {(HasAdminRights ? "✅" : "❌")} Admin Rights: {HasAdminRights}");
            Console.WriteLine($"   {(HasVipAccess ? "✅" : "❌")} VIP Access: {HasVipAccess}");
            Console.WriteLine($"   {(BettingWindowOpen ? "✅" : "❌")} Betting Window: {BettingWindowOpen}");
            Console.WriteLine($"   {(MaintenanceMode ? "✅" : "❌")} Maintenance Mode: {MaintenanceMode}");
            Console.WriteLine($"   {(SufficientBankroll ? "✅" : "❌")} Sufficient Bankroll: {SufficientBankroll}");
            Console.WriteLine($"   {(GameStarted ? "✅" : "❌")} Game Started: {GameStarted}");
            Console.WriteLine($"   {(LiveOddsAvailable ? "✅" : "❌")} Live Odds Available: {LiveOddsAvailable}");
            Console.WriteLine($"   {(EmergencyOverride ? "✅" : "❌")} Emergency Override: {EmergencyOverride}");
            Console.WriteLine($"   {(ApiKeysValid ? "✅" : "❌")} API Keys Valid: {ApiKeysValid}");
            Console.WriteLine($"   {(NCAAWeek7Active ? "✅" : "❌")} NCAA Week 7 Active: {NCAAWeek7Active}");
            Console.WriteLine($"   {(ParlayGenerationEnabled ? "✅" : "❌")} Parlay Generation: {ParlayGenerationEnabled}");
            Console.WriteLine($"   {(ConferenceDataLoaded ? "✅" : "❌")} Conference Data: {ConferenceDataLoaded}");
            Console.WriteLine($"   {(SentimentAnalysisReady ? "✅" : "❌")} Sentiment Analysis: {SentimentAnalysisReady}");

            // Run all demonstrations
            var andResults = DemonstrateAndOperator();
            var orResults = DemonstrateOrOperator();
            var notResults = DemonstrateNotOperator();
            var xorResults = DemonstrateXorOperator();
            var complexResults = ComplexParlayValidation();

            // Summary
            Console.WriteLine("\n🏆 C# DEMONSTRATION COMPLETE");
            Console.WriteLine(new string('=', 50));
            Console.WriteLine("💡 Boolean Logic Applications in EQ12 (C#):");
            Console.WriteLine("   • Type-safe Boolean operations with C# strong typing");
            Console.WriteLine("   • Nullable parameter handling for flexible updates");
            Console.WriteLine("   • JSON serialization for interoperability with Python");
            Console.WriteLine("   • Professional logging and error handling");
            Console.WriteLine("   • Integration with .NET ecosystem");
            Console.WriteLine("   • Cross-platform compatibility via .NET Core");

            // Compile comprehensive results
            var comprehensiveResults = new Dictionary<string, object>
            {
                ["timestamp"] = DateTime.Now.ToString("O"),
                ["language"] = "C#",
                ["system_conditions"] = new
                {
                    UserLoggedIn,
                    HasAdminRights,
                    HasVipAccess,
                    BettingWindowOpen,
                    MaintenanceMode,
                    SufficientBankroll,
                    GameStarted,
                    LiveOddsAvailable,
                    EmergencyOverride,
                    ApiKeysValid,
                    NCAAWeek7Active,
                    ParlayGenerationEnabled,
                    ConferenceDataLoaded,
                    SentimentAnalysisReady
                },
                ["and_operations"] = andResults,
                ["or_operations"] = orResults,
                ["not_operations"] = notResults,
                ["xor_operations"] = xorResults,
                ["complex_validation"] = complexResults,
                ["log_entries"] = LogEntries
            };

            // Save results to JSON
            try
            {
                string resultsPath = Path.Combine(EQ12Root, "outputs",
                    $"boolean_logic_demo_csharp_{DateTime.Now:yyyyMMdd_HHmmss}.json");

                Directory.CreateDirectory(Path.GetDirectoryName(resultsPath));

                string jsonString = JsonSerializer.Serialize(comprehensiveResults,
                    new JsonSerializerOptions { WriteIndented = true });

                File.WriteAllText(resultsPath, jsonString);
                Console.WriteLine($"\n💾 C# Results saved to: {resultsPath}");
            }
            catch (Exception e)
            {
                LogEntry($"Failed to save results: {e.Message}");
                Console.WriteLine($"❌ Error saving results: {e.Message}");
            }

            return comprehensiveResults;
        }
    }

    /// <summary>
    /// Main program class for Boolean Logic Demo
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Initialize Boolean Logic Engine
                var engine = new EQ12BooleanLogicEngine();

                // Run comprehensive demonstration
                var results = engine.RunComprehensiveDemo();

                Console.WriteLine("\n✨ EQ12 Boolean Logic Engine (C#) demonstration completed successfully!");
                Console.WriteLine($"📈 Total operations evaluated: {results.Count - 3}"); // Exclude metadata

                Console.WriteLine("\nPress any key to exit...");
                Console.ReadKey();
            }
            catch (Exception e)
            {
                Console.WriteLine($"❌ Error: {e.Message}");
                Console.WriteLine("\nPress any key to exit...");
                Console.ReadKey();
            }
        }
    }
}
