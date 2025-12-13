
// EQ12 HMI Dashboard Logic - Industrial SCADA Style
class EQ12HMIController {
    constructor() {
        this.components = [
    {
        "name": "alternative_bills_chiefs_parlays",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\alternative_bills_chiefs_parlays.py",
        "config_path": "C:\\EQ12\\configs\\alternative_bills_chiefs_parlays_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_advanced_parlay_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_advanced_parlay_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_advanced_parlay_generator_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_bulletproof_parlay_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_bulletproof_parlay_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_bulletproof_parlay_generator_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_byu_texas_tech_parlay_optimizer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_byu_texas_tech_parlay_optimizer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_byu_texas_tech_parlay_optimizer_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_complete_parlay_simulation_engine",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_complete_parlay_simulation_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_complete_parlay_simulation_engine_config.json",
        "dependencies": [
            "from eq12",
            "import eq12",
            "pandas",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_extended_goalscorer_parlays",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_extended_goalscorer_parlays.py",
        "config_path": "C:\\EQ12\\configs\\eq12_extended_goalscorer_parlays_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_goalscorer_parlays",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_goalscorer_parlays.py",
        "config_path": "C:\\EQ12\\configs\\eq12_goalscorer_parlays_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_high_confidence_parlay",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_high_confidence_parlay.py",
        "config_path": "C:\\EQ12\\configs\\eq12_high_confidence_parlay_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_live_odds_parlay_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_live_odds_parlay_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_live_odds_parlay_generator_config.json",
        "dependencies": [
            "from eq12",
            "numpy",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_max_payout_parlays",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_max_payout_parlays.py",
        "config_path": "C:\\EQ12\\configs\\eq12_max_payout_parlays_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_parlay_cleanup",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_parlay_cleanup.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_parlay_cleanup_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_original_parlay_weather_analysis",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_original_parlay_weather_analysis.py",
        "config_path": "C:\\EQ12\\configs\\eq12_original_parlay_weather_analysis_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlays_webhook",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlays_webhook.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlays_webhook_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_builder.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_builder_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_conflict_detector",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_conflict_detector.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_conflict_detector_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_debug",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_debug.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_debug_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_filter_engine",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_filter_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_filter_engine_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_monetization_engine",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_monetization_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_monetization_engine_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_optimizer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_optimizer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_optimizer_config.json",
        "dependencies": [
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_professional_parlay_engine",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_professional_parlay_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_professional_parlay_engine_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_run_parlay",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_run_parlay.py",
        "config_path": "C:\\EQ12\\configs\\eq12_run_parlay_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sports_parlay_analyzer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sports_parlay_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sports_parlay_analyzer_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sports_parlay_demo",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sports_parlay_demo.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sports_parlay_demo_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_tuned_parlay_optimizer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_tuned_parlay_optimizer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_tuned_parlay_optimizer_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_weather_enhanced_parlay",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_weather_enhanced_parlay.py",
        "config_path": "C:\\EQ12\\configs\\eq12_weather_enhanced_parlay_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_winning_margin_parlay_analyzer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_winning_margin_parlay_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_winning_margin_parlay_analyzer_config.json",
        "dependencies": [
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_yolo_parlay_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_yolo_parlay_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_yolo_parlay_generator_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "financial_parlay_analysis",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\financial_parlay_analysis.py",
        "config_path": "C:\\EQ12\\configs\\financial_parlay_analysis_config.json",
        "dependencies": [
            "pandas",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "parlay_analysis_system",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\parlay_analysis_system.py",
        "config_path": "C:\\EQ12\\configs\\parlay_analysis_system_config.json",
        "dependencies": [
            "pandas",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "parlay_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\parlay_builder.py",
        "config_path": "C:\\EQ12\\configs\\parlay_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "recent_parlay_analysis",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\recent_parlay_analysis.py",
        "config_path": "C:\\EQ12\\configs\\recent_parlay_analysis_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "betting_intelligence_orchestrator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\betting_intelligence_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\betting_intelligence_orchestrator_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_betting_arbitrage_bot",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_betting_arbitrage_bot.py",
        "config_path": "C:\\EQ12\\configs\\eq12_betting_arbitrage_bot_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_betting_function_caller",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_betting_function_caller.py",
        "config_path": "C:\\EQ12\\configs\\eq12_betting_function_caller_config.json",
        "dependencies": [
            "openai"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_betting_ai",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_betting_ai.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_betting_ai_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "telegram",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_entertainment_betting_guide",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_entertainment_betting_guide.py",
        "config_path": "C:\\EQ12\\configs\\eq12_entertainment_betting_guide_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_hf_betting_demo",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_hf_betting_demo.py",
        "config_path": "C:\\EQ12\\configs\\eq12_hf_betting_demo_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_hf_betting_integration",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_hf_betting_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_hf_betting_integration_config.json",
        "dependencies": [
            "from eq12",
            "import eq12",
            "pandas",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_hf_betting_model",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_hf_betting_model.py",
        "config_path": "C:\\EQ12\\configs\\eq12_hf_betting_model_config.json",
        "dependencies": [
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_live_betting_analyzer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_live_betting_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_live_betting_analyzer_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_weather_enhanced_betting",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_weather_enhanced_betting.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_weather_enhanced_betting_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_production_betting_pipeline",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_production_betting_pipeline.py",
        "config_path": "C:\\EQ12\\configs\\eq12_production_betting_pipeline_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_quantum_betting_superposition",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_quantum_betting_superposition.py",
        "config_path": "C:\\EQ12\\configs\\eq12_quantum_betting_superposition_config.json",
        "dependencies": [
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_weather_enhanced_betting_system",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_weather_enhanced_betting_system.py",
        "config_path": "C:\\EQ12\\configs\\eq12_weather_enhanced_betting_system_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "automated_sgp_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\automated_sgp_generator.py",
        "config_path": "C:\\EQ12\\configs\\automated_sgp_generator_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "bills_chiefs_sgp_analyzer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\bills_chiefs_sgp_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\bills_chiefs_sgp_analyzer_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "chi_mil_mlb_sgp_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\chi_mil_mlb_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\chi_mil_mlb_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_best_sgp_combinations",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_best_sgp_combinations.py",
        "config_path": "C:\\EQ12\\configs\\eq12_best_sgp_combinations_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_roster_validated_sgp_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_roster_validated_sgp_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_roster_validated_sgp_generator_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_roster_validated_sgp_generator_enhanced",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_roster_validated_sgp_generator_enhanced.py",
        "config_path": "C:\\EQ12\\configs\\eq12_roster_validated_sgp_generator_enhanced_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sgp_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sgp_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sgp_generator_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "kc_jac_sgp_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\kc_jac_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\kc_jac_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "la_phi_mlb_sgp_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\la_phi_mlb_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\la_phi_mlb_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nba_sgp_player_status_verification",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\nba_sgp_player_status_verification.py",
        "config_path": "C:\\EQ12\\configs\\nba_sgp_player_status_verification_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "realistic_bills_chiefs_sgp",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\realistic_bills_chiefs_sgp.py",
        "config_path": "C:\\EQ12\\configs\\realistic_bills_chiefs_sgp_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "seahawks_commanders_sgp",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\seahawks_commanders_sgp.py",
        "config_path": "C:\\EQ12\\configs\\seahawks_commanders_sgp_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_live_odds_with_bulletproof",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_live_odds_with_bulletproof.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_live_odds_with_bulletproof_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_odds_api",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_odds_api.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_odds_api_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_live_odds_fetcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_live_odds_fetcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_live_odds_fetcher_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_live_odds_parlay_generator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_live_odds_parlay_generator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_live_odds_parlay_generator_config.json",
        "dependencies": [
            "from eq12",
            "numpy",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_odds_ingest",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_odds_ingest.py",
        "config_path": "C:\\EQ12\\configs\\eq12_odds_ingest_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_odds_stream",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_odds_stream.py",
        "config_path": "C:\\EQ12\\configs\\eq12_odds_stream_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_run_odds",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_run_odds.py",
        "config_path": "C:\\EQ12\\configs\\eq12_run_odds_config.json",
        "dependencies": [
            "telegram",
            "openai",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "odds_parser",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\odds_parser.py",
        "config_path": "C:\\EQ12\\configs\\odds_parser_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_all_sports_roster_verification",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_all_sports_roster_verification.py",
        "config_path": "C:\\EQ12\\configs\\eq12_all_sports_roster_verification_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_comprehensive_sports_fetcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_comprehensive_sports_fetcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_comprehensive_sports_fetcher_config.json",
        "dependencies": [
            "openai",
            "requests",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_corrected_sports_fetcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_corrected_sports_fetcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_corrected_sports_fetcher_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_sports_fetcher_complete",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_sports_fetcher_complete.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_sports_fetcher_complete_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_final_complete_sports_fetcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_final_complete_sports_fetcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_final_complete_sports_fetcher_config.json",
        "dependencies": [
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_multi_sports_api_client",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_multi_sports_api_client.py",
        "config_path": "C:\\EQ12\\configs\\eq12_multi_sports_api_client_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_apisports_integration",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_apisports_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_apisports_integration_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_realtime_sports_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_realtime_sports_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_realtime_sports_intelligence_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_real_sports_api_fetcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_real_sports_api_fetcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_real_sports_api_fetcher_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_specific_date_sports_pull",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_specific_date_sports_pull.py",
        "config_path": "C:\\EQ12\\configs\\eq12_specific_date_sports_pull_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sportsbooks",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sportsbooks.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sportsbooks_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sports_analysis_report",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sports_analysis_report.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sports_analysis_report_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sports_parlay_analyzer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sports_parlay_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sports_parlay_analyzer_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_sports_parlay_demo",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_sports_parlay_demo.py",
        "config_path": "C:\\EQ12\\configs\\eq12_sports_parlay_demo_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_thesportsdb_enhanced_integration",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_thesportsdb_enhanced_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_thesportsdb_enhanced_integration_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_thesportsdb_master_integration",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_thesportsdb_master_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_thesportsdb_master_integration_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_thesportsdb_pricing_analysis",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_thesportsdb_pricing_analysis.py",
        "config_path": "C:\\EQ12\\configs\\eq12_thesportsdb_pricing_analysis_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "sports",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\sports.py",
        "config_path": "C:\\EQ12\\configs\\sports_config.json",
        "dependencies": [
            "from eq12",
            "openai",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_enhanced_nfl_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_enhanced_nfl_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_enhanced_nfl_intelligence_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_bulletproof_live",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_bulletproof_live.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_bulletproof_live_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_live_api_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_live_api_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_live_api_intelligence_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_live_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_live_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_live_intelligence_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_logging_optimizer",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_logging_optimizer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_logging_optimizer_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_log_rotator",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_log_rotator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_log_rotator_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_monitor",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_monitor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_monitor_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_parlay_cleanup",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_parlay_cleanup.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_parlay_cleanup_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_stadium_weather",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_stadium_weather.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_stadium_weather_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_tonight_lv_den_special",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_tonight_lv_den_special.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_tonight_lv_den_special_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_weather_enhanced_betting",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_weather_enhanced_betting.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_weather_enhanced_betting_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_parlay_conflict_detector",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_parlay_conflict_detector.py",
        "config_path": "C:\\EQ12\\configs\\eq12_parlay_conflict_detector_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_quantum_nfl_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_quantum_nfl_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_quantum_nfl_intelligence_config.json",
        "dependencies": [
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nfl_live_roster_verification",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\nfl_live_roster_verification.py",
        "config_path": "C:\\EQ12\\configs\\nfl_live_roster_verification_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nfl_roster_fetcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\nfl_roster_fetcher.py",
        "config_path": "C:\\EQ12\\configs\\nfl_roster_fetcher_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nfl_roster_prevention_system",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\nfl_roster_prevention_system.py",
        "config_path": "C:\\EQ12\\configs\\nfl_roster_prevention_system_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_comprehensive_nba_feed_searcher",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_comprehensive_nba_feed_searcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_comprehensive_nba_feed_searcher_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_nba_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_nba_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_nba_intelligence_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_nba_monitoring",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_nba_monitoring.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_nba_monitoring_config.json",
        "dependencies": [
            "from eq12",
            "telegram",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_apisports_integration",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_apisports_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_apisports_integration_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_continuous_monitoring",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_continuous_monitoring.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_continuous_monitoring_config.json",
        "dependencies": [
            "from eq12",
            "telegram",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_live_monitoring",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_live_monitoring.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_live_monitoring_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_news_harvester",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_news_harvester.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_news_harvester_config.json",
        "dependencies": [
            "telegram",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_weather_intelligence",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_weather_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_weather_intelligence_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nba_live_roster_verification",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\nba_live_roster_verification.py",
        "config_path": "C:\\EQ12\\configs\\nba_live_roster_verification_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nba_sgp_player_status_verification",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\nba_sgp_player_status_verification.py",
        "config_path": "C:\\EQ12\\configs\\nba_sgp_player_status_verification_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "chi_mil_mlb_sgp_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\chi_mil_mlb_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\chi_mil_mlb_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "la_phi_mlb_sgp_builder",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\la_phi_mlb_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\la_phi_mlb_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "test_mlb_fixed",
        "type": "betting_engine",
        "script_path": "C:\\EQ12\\scripts\\test_mlb_fixed.py",
        "config_path": "C:\\EQ12\\configs\\test_mlb_fixed_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "badge_health_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\badge_health_monitor.py",
        "config_path": "C:\\EQ12\\configs\\badge_health_monitor_config.json",
        "dependencies": [
            "requests",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_comprehensive_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_comprehensive_monitor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_comprehensive_monitor_config.json",
        "dependencies": [
            "telegram",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_nba_monitoring",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_nba_monitoring.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_nba_monitoring_config.json",
        "dependencies": [
            "from eq12",
            "telegram",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_gitleaks_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_gitleaks_monitor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_gitleaks_monitor_config.json",
        "dependencies": [
            "openai",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_continuous_monitoring",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_continuous_monitoring.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_continuous_monitoring_config.json",
        "dependencies": [
            "from eq12",
            "telegram",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_live_monitoring",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_live_monitoring.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_live_monitoring_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_network_monitoring_dashboard",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_network_monitoring_dashboard.py",
        "config_path": "C:\\EQ12\\configs\\eq12_network_monitoring_dashboard_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_monitor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_monitor_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_performance_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_performance_monitor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_performance_monitor_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_resource_monitor_fix_test",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_resource_monitor_fix_test.py",
        "config_path": "C:\\EQ12\\configs\\eq12_resource_monitor_fix_test_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "health_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\health_monitor.py",
        "config_path": "C:\\EQ12\\configs\\health_monitor_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ngrok_tunnel_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\ngrok_tunnel_monitor.py",
        "config_path": "C:\\EQ12\\configs\\ngrok_tunnel_monitor_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "badge_health_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\badge_health_monitor.py",
        "config_path": "C:\\EQ12\\configs\\badge_health_monitor_config.json",
        "dependencies": [
            "requests",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_system_health_analyzer",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_system_health_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_system_health_analyzer_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "health_monitor",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\health_monitor.py",
        "config_path": "C:\\EQ12\\configs\\health_monitor_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_comprehensive_status_reporter",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_comprehensive_status_reporter.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_comprehensive_status_reporter_config.json",
        "dependencies": [
            "from eq12",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_player_status_checker",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_player_status_checker.py",
        "config_path": "C:\\EQ12\\configs\\eq12_player_status_checker_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_status",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_status.py",
        "config_path": "C:\\EQ12\\configs\\eq12_status_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "hardcoded_ai_status",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\hardcoded_ai_status.py",
        "config_path": "C:\\EQ12\\configs\\hardcoded_ai_status_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nba_sgp_player_status_verification",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\nba_sgp_player_status_verification.py",
        "config_path": "C:\\EQ12\\configs\\nba_sgp_player_status_verification_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_resource_monitor_fix_test",
        "type": "monitor",
        "script_path": "C:\\EQ12\\scripts\\eq12_resource_monitor_fix_test.py",
        "config_path": "C:\\EQ12\\configs\\eq12_resource_monitor_fix_test_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ai_enhanced_nfl_intelligence_20251106_194318",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\ai_enhanced_nfl_intelligence_20251106_194318.html",
        "config_path": "C:\\EQ12\\configs\\ai_enhanced_nfl_intelligence_20251106_194318_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "copilot_management",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\copilot_management.html",
        "config_path": "C:\\EQ12\\configs\\copilot_management_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "daily_coral_report_20251102_141551",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\daily_coral_report_20251102_141551.html",
        "config_path": "C:\\EQ12\\configs\\daily_coral_report_20251102_141551_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\dashboard.html",
        "config_path": "C:\\EQ12\\configs\\dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "enhanced",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\enhanced.html",
        "config_path": "C:\\EQ12\\configs\\enhanced_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "enterprise_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\enterprise_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\enterprise_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_betting_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_betting_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\eq12_betting_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_bi_execution_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_bi_execution_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\eq12_bi_execution_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_comprehensive_monitor_status",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_comprehensive_monitor_status.html",
        "config_path": "C:\\EQ12\\configs\\eq12_comprehensive_monitor_status_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_10x_acceleration_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_coral_10x_acceleration_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_10x_acceleration_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_dashboard_20251107_155103",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_dashboard_20251107_155103.html",
        "config_path": "C:\\EQ12\\configs\\eq12_dashboard_20251107_155103_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_dashboard_20251107_155213",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_dashboard_20251107_155213.html",
        "config_path": "C:\\EQ12\\configs\\eq12_dashboard_20251107_155213_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_dashboard_20251107_155413",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_dashboard_20251107_155413.html",
        "config_path": "C:\\EQ12\\configs\\eq12_dashboard_20251107_155413_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_expert_discovery_dashboard_20251107_070800",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_expert_discovery_dashboard_20251107_070800.html",
        "config_path": "C:\\EQ12\\configs\\eq12_expert_discovery_dashboard_20251107_070800_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_kernel_optimization_report_20251107_063402",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_kernel_optimization_report_20251107_063402.html",
        "config_path": "C:\\EQ12\\configs\\eq12_kernel_optimization_report_20251107_063402_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_network_monitoring_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_network_monitoring_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\eq12_network_monitoring_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_quantum_nfl_dashboard_20251107_073500",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_quantum_nfl_dashboard_20251107_073500.html",
        "config_path": "C:\\EQ12\\configs\\eq12_quantum_nfl_dashboard_20251107_073500_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_realtime_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_realtime_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\eq12_realtime_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_revenue_activation_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\eq12_revenue_activation_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\eq12_revenue_activation_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "executive_dashboard_20251107_080719",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\executive_dashboard_20251107_080719.html",
        "config_path": "C:\\EQ12\\configs\\executive_dashboard_20251107_080719_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "executive_dashboard_20251107_080912",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\executive_dashboard_20251107_080912.html",
        "config_path": "C:\\EQ12\\configs\\executive_dashboard_20251107_080912_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "index",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\index.html",
        "config_path": "C:\\EQ12\\configs\\index_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "live_betting_dashboard_25_stakes_20251102_142200",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\live_betting_dashboard_25_stakes_20251102_142200.html",
        "config_path": "C:\\EQ12\\configs\\live_betting_dashboard_25_stakes_20251102_142200_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "live_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\live_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\live_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "microsoft_partners_dashboard_20251107_215330",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\microsoft_partners_dashboard_20251107_215330.html",
        "config_path": "C:\\EQ12\\configs\\microsoft_partners_dashboard_20251107_215330_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "monitoring_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\monitoring_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\monitoring_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nfl_intelligence_report_20251106_191142",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\nfl_intelligence_report_20251106_191142.html",
        "config_path": "C:\\EQ12\\configs\\nfl_intelligence_report_20251106_191142_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nfl_tonight_special_report_20251106_193527",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\nfl_tonight_special_report_20251106_193527.html",
        "config_path": "C:\\EQ12\\configs\\nfl_tonight_special_report_20251106_193527_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ngrok_monitor_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\ngrok_monitor_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\ngrok_monitor_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "revenue_empire_dashboard_20251107_163428",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\revenue_empire_dashboard_20251107_163428.html",
        "config_path": "C:\\EQ12\\configs\\revenue_empire_dashboard_20251107_163428_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "revenue_empire_dashboard_20251107_164953",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\revenue_empire_dashboard_20251107_164953.html",
        "config_path": "C:\\EQ12\\configs\\revenue_empire_dashboard_20251107_164953_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "revenue_empire_dashboard_20251107_165403",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\revenue_empire_dashboard_20251107_165403.html",
        "config_path": "C:\\EQ12\\configs\\revenue_empire_dashboard_20251107_165403_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "revenue_empire_dashboard_latest",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\revenue_empire_dashboard_latest.html",
        "config_path": "C:\\EQ12\\configs\\revenue_empire_dashboard_latest_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "sports_betting_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\sports_betting_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\sports_betting_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "test_dashboard",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\test_dashboard.html",
        "config_path": "C:\\EQ12\\configs\\test_dashboard_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "total_system_dashboard_20251107_214818",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\total_system_dashboard_20251107_214818.html",
        "config_path": "C:\\EQ12\\configs\\total_system_dashboard_20251107_214818_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "total_system_dashboard_20251107_214925",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\total_system_dashboard_20251107_214925.html",
        "config_path": "C:\\EQ12\\configs\\total_system_dashboard_20251107_214925_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "total_system_dashboard_20251107_215336",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\total_system_dashboard_20251107_215336.html",
        "config_path": "C:\\EQ12\\configs\\total_system_dashboard_20251107_215336_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "total_system_dashboard_20251107_215513",
        "type": "dashboard",
        "script_path": "C:\\EQ12\\dashboard\\total_system_dashboard_20251107_215513.html",
        "config_path": "C:\\EQ12\\configs\\total_system_dashboard_20251107_215513_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ai_provider_config",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\ai_provider_config.py",
        "config_path": "C:\\EQ12\\configs\\ai_provider_config_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_enhanced_nfl_intelligence",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_enhanced_nfl_intelligence.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_enhanced_nfl_intelligence_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_guardrails",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_guardrails.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_guardrails_config.json",
        "dependencies": [
            "openai"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_inference_engine",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_inference_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_inference_engine_config.json",
        "dependencies": [
            "pandas",
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_model_deployer",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_model_deployer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_model_deployer_config.json",
        "dependencies": [
            "pandas",
            "numpy",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_trainer",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_trainer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_trainer_config.json",
        "dependencies": [
            "pandas",
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_container_validator",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_container_validator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_container_validator_config.json",
        "dependencies": [
            "playwright",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_betting_ai",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_betting_ai.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_betting_ai_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "telegram",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_crypto_ai",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_crypto_ai.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_crypto_ai_config.json",
        "dependencies": [
            "pandas",
            "numpy",
            "requests",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_ai",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_ai.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_ai_config.json",
        "dependencies": [
            "openai",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_security_ai_integration",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_security_ai_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_security_ai_integration_config.json",
        "dependencies": [
            "openai"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_entertainment_betting_guide",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_entertainment_betting_guide.py",
        "config_path": "C:\\EQ12\\configs\\eq12_entertainment_betting_guide_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_internet_connectivity_repair_system",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_internet_connectivity_repair_system.py",
        "config_path": "C:\\EQ12\\configs\\eq12_internet_connectivity_repair_system_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_main",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_main.py",
        "config_path": "C:\\EQ12\\configs\\eq12_main_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_network_repair_driver_manager",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_network_repair_driver_manager.py",
        "config_path": "C:\\EQ12\\configs\\eq12_network_repair_driver_manager_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_openai_key_engine",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_openai_key_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_openai_key_engine_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_player_availability",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_player_availability.py",
        "config_path": "C:\\EQ12\\configs\\eq12_player_availability_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_todays_entertainment_triggers",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_todays_entertainment_triggers.py",
        "config_path": "C:\\EQ12\\configs\\eq12_todays_entertainment_triggers_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_universal_repair_assistant",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_universal_repair_assistant.py",
        "config_path": "C:\\EQ12\\configs\\eq12_universal_repair_assistant_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "google_ai_client",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\google_ai_client.py",
        "config_path": "C:\\EQ12\\configs\\google_ai_client_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "groq_ai_client",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\groq_ai_client.py",
        "config_path": "C:\\EQ12\\configs\\groq_ai_client_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "hardcoded_ai_status",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\hardcoded_ai_status.py",
        "config_path": "C:\\EQ12\\configs\\hardcoded_ai_status_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "multi_provider_ai_router",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\multi_provider_ai_router.py",
        "config_path": "C:\\EQ12\\configs\\multi_provider_ai_router_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "openai_migration_helper",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\openai_migration_helper.py",
        "config_path": "C:\\EQ12\\configs\\openai_migration_helper_config.json",
        "dependencies": [
            "openai",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "openai_repo_scan",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\openai_repo_scan.py",
        "config_path": "C:\\EQ12\\configs\\openai_repo_scan_config.json",
        "dependencies": [
            "openai",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "repair_all_tasks",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\repair_all_tasks.py",
        "config_path": "C:\\EQ12\\configs\\repair_all_tasks_config.json",
        "dependencies": [
            "from eq12",
            "import eq12"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "chi_mil_mlb_sgp_builder",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\chi_mil_mlb_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\chi_mil_mlb_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "la_phi_mlb_sgp_builder",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\la_phi_mlb_sgp_builder.py",
        "config_path": "C:\\EQ12\\configs\\la_phi_mlb_sgp_builder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "test_mlb_fixed",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\test_mlb_fixed.py",
        "config_path": "C:\\EQ12\\configs\\test_mlb_fixed_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "aligned_model",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\aligned_model.py",
        "config_path": "C:\\EQ12\\configs\\aligned_model_config.json",
        "dependencies": [
            "openai"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_model_deployer",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_model_deployer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_model_deployer_config.json",
        "dependencies": [
            "pandas",
            "numpy",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_hf_betting_model",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_hf_betting_model.py",
        "config_path": "C:\\EQ12\\configs\\eq12_hf_betting_model_config.json",
        "dependencies": [
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_model_updater",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_model_updater.py",
        "config_path": "C:\\EQ12\\configs\\eq12_model_updater_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "github_models_client",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\github_models_client.py",
        "config_path": "C:\\EQ12\\configs\\github_models_client_config.json",
        "dependencies": [
            "openai",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "github_models_integration",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\github_models_integration.py",
        "config_path": "C:\\EQ12\\configs\\github_models_integration_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_inference_engine",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_inference_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_inference_engine_config.json",
        "dependencies": [
            "pandas",
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "coral_device_detection",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\coral_device_detection.py",
        "config_path": "C:\\EQ12\\configs\\coral_device_detection_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "coral_performance_test",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\coral_performance_test.py",
        "config_path": "C:\\EQ12\\configs\\coral_performance_test_config.json",
        "dependencies": [
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "coral_simulation_layer",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\coral_simulation_layer.py",
        "config_path": "C:\\EQ12\\configs\\coral_simulation_layer_config.json",
        "dependencies": [
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "display_coral_results",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\display_coral_results.py",
        "config_path": "C:\\EQ12\\configs\\display_coral_results_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_10x_upgrade_system",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_10x_upgrade_system.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_10x_upgrade_system_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_accelerator_manager",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_accelerator_manager.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_accelerator_manager_config.json",
        "dependencies": [
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_betting_ai",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_betting_ai.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_betting_ai_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "telegram",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_compatibility_fixer",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_compatibility_fixer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_compatibility_fixer_config.json",
        "dependencies": [
            "from eq12",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_comprehensive_status_reporter",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_comprehensive_status_reporter.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_comprehensive_status_reporter_config.json",
        "dependencies": [
            "from eq12",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_crypto_ai",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_crypto_ai.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_crypto_ai_config.json",
        "dependencies": [
            "pandas",
            "numpy",
            "requests",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_crypto_master",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_crypto_master.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_crypto_master_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_ethereum_fusion",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_ethereum_fusion.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_ethereum_fusion_config.json",
        "dependencies": [
            "numpy",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_final_summary",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_final_summary.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_final_summary_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_integration_wrapper",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_integration_wrapper.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_integration_wrapper_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_synergistic_engine",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_synergistic_engine.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_synergistic_engine_config.json",
        "dependencies": [
            "from eq12",
            "requests",
            "telegram",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_synergistic_launcher",
        "type": "ai_model",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_synergistic_launcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_synergistic_launcher_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "circuit_breaker_service",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\circuit_breaker_service.py",
        "config_path": "C:\\EQ12\\configs\\circuit_breaker_service_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_alerting_service",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_alerting_service.py",
        "config_path": "C:\\EQ12\\configs\\eq12_alerting_service_config.json",
        "dependencies": [
            "from eq12",
            "telegram",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_automation_efficiency_god_mode",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_automation_efficiency_god_mode.py",
        "config_path": "C:\\EQ12\\configs\\eq12_automation_efficiency_god_mode_config.json",
        "dependencies": [
            "from eq12",
            "openai",
            "requests",
            "telegram",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ebay_automation_toolkit",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_ebay_automation_toolkit.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ebay_automation_toolkit_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_quantum_automation_creator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_quantum_automation_creator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_quantum_automation_creator_config.json",
        "dependencies": [
            "numpy",
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_web3_freelance_automation",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_web3_freelance_automation.py",
        "config_path": "C:\\EQ12\\configs\\eq12_web3_freelance_automation_config.json",
        "dependencies": [
            "from eq12",
            "numpy",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "firefox_governance_automation",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\firefox_governance_automation.py",
        "config_path": "C:\\EQ12\\configs\\firefox_governance_automation_config.json",
        "dependencies": [
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "hardcoded_roster_automation",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\hardcoded_roster_automation.py",
        "config_path": "C:\\EQ12\\configs\\hardcoded_roster_automation_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "betting_intelligence_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\betting_intelligence_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\betting_intelligence_orchestrator_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ethereum_godmode_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_ethereum_godmode_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_ethereum_godmode_orchestrator_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_master_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_master_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_master_orchestrator_config.json",
        "dependencies": [
            "telegram",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_master_revenue_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_master_revenue_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_master_revenue_orchestrator_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_microsoft_partner_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_microsoft_partner_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_microsoft_partner_orchestrator_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_orchestrator_config.json",
        "dependencies": [
            "openai",
            "requests",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_quantum_auto_orchestrator",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_quantum_auto_orchestrator.py",
        "config_path": "C:\\EQ12\\configs\\eq12_quantum_auto_orchestrator_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_synergistic_launcher",
        "type": "service",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_synergistic_launcher.py",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_synergistic_launcher_config.json",
        "dependencies": [
            "from eq12",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_enhanced_nfl_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_enhanced_nfl_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_enhanced_nfl_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ai_enhanced_nfl_wrapper_simple",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_ai_enhanced_nfl_wrapper_simple.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_ai_enhanced_nfl_wrapper_simple_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_browser_extension_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_browser_extension_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_browser_extension_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_bsc_yield_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_bsc_yield_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_bsc_yield_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_bsc_yield_wrapper_fixed",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_bsc_yield_wrapper_fixed.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_bsc_yield_wrapper_fixed_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_bulletproof_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_bulletproof_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_bulletproof_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_chromium_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_chromium_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_chromium_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_complete_business_intelligence_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_complete_business_intelligence_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_complete_business_intelligence_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_comprehensive_monitor_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_comprehensive_monitor_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_comprehensive_monitor_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_copywriting_ascii_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_copywriting_ascii_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_copywriting_ascii_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_copywriting_empire_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_copywriting_empire_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_copywriting_empire_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_copywriting_empire_wrapper_clean",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_copywriting_empire_wrapper_clean.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_copywriting_empire_wrapper_clean_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_copywriting_simple_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_copywriting_simple_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_copywriting_simple_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_automation_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_automation_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_automation_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_crypto_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_crypto_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_crypto_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_coral_synergistic_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_coral_synergistic_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_coral_synergistic_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_dotnet_tools_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_dotnet_tools_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_dotnet_tools_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_flake8_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_flake8_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_flake8_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_groq_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_groq_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_groq_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_injury_intelligence_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_injury_intelligence_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_injury_intelligence_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_monitoring_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_monitoring_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_monitoring_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nba_news_harvester_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_nba_news_harvester_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_nba_news_harvester_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ncaa_parlay_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_ncaa_parlay_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_ncaa_parlay_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ncaa_week7_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_ncaa_week7_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_ncaa_week7_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_intelligence_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_intelligence_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_intelligence_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_intelligence_wrapper_clean",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_intelligence_wrapper_clean.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_intelligence_wrapper_clean_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_nfl_tonight_special_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_nfl_tonight_special_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_nfl_tonight_special_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_openai_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_openai_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_openai_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_premium_openweather_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_premium_openweather_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_premium_openweather_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_system_management_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_system_management_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_system_management_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_telegram_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_telegram_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_telegram_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_twitter_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_twitter_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_twitter_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_twitter_wrapper_fixed",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_twitter_wrapper_fixed.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_twitter_wrapper_fixed_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_vb_debugging_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_vb_debugging_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_vb_debugging_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_vb_debugging_wrapper_clean",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_vb_debugging_wrapper_clean.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_vb_debugging_wrapper_clean_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_wealth_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_wealth_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_wealth_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "nfl_roster_prevention_wrapper",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\nfl_roster_prevention_wrapper.ps1",
        "config_path": "C:\\EQ12\\configs\\nfl_roster_prevention_wrapper_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_github_cli_manager",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_github_cli_manager.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_github_cli_manager_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_hop_manager",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_hop_manager.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_hop_manager_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_ngrok_manager",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_ngrok_manager.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_ngrok_manager_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_unified_dashboard_manager",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_unified_dashboard_manager.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_unified_dashboard_manager_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_url_manager",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_url_manager.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_url_manager_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_vpn_manager",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_vpn_manager.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_vpn_manager_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ai_agent_deployment_oneshot",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\ai_agent_deployment_oneshot.ps1",
        "config_path": "C:\\EQ12\\configs\\ai_agent_deployment_oneshot_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ai_agent_deployment_oneshot_20251107_080503",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\ai_agent_deployment_oneshot_20251107_080503.ps1",
        "config_path": "C:\\EQ12\\configs\\ai_agent_deployment_oneshot_20251107_080503_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "ai_agent_deployment_oneshot_20251107_080907",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\ai_agent_deployment_oneshot_20251107_080907.ps1",
        "config_path": "C:\\EQ12\\configs\\ai_agent_deployment_oneshot_20251107_080907_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "Deploy-EthereumGodmode",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\Deploy-EthereumGodmode.ps1",
        "config_path": "C:\\EQ12\\configs\\Deploy-EthereumGodmode_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "deploy_github_security",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\deploy_github_security.ps1",
        "config_path": "C:\\EQ12\\configs\\deploy_github_security_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "EQ12_COMPREHENSIVE_DEPLOYMENT",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\EQ12_COMPREHENSIVE_DEPLOYMENT.ps1",
        "config_path": "C:\\EQ12\\configs\\EQ12_COMPREHENSIVE_DEPLOYMENT_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "EQ12_COMPREHENSIVE_DEPLOYMENT_FIXED",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\EQ12_COMPREHENSIVE_DEPLOYMENT_FIXED.ps1",
        "config_path": "C:\\EQ12\\configs\\EQ12_COMPREHENSIVE_DEPLOYMENT_FIXED_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_dashboard_setup",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_dashboard_setup.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_dashboard_setup_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_dashboard_simple_setup",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_dashboard_simple_setup.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_dashboard_simple_setup_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_post_vpn_setup",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_post_vpn_setup.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_post_vpn_setup_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_setup_complete",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_setup_complete.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_setup_complete_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_setup_security",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_setup_security.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_setup_security_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_url_system_setup",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\eq12_url_system_setup.ps1",
        "config_path": "C:\\EQ12\\configs\\eq12_url_system_setup_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "setup_badge_monitor",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\setup_badge_monitor.ps1",
        "config_path": "C:\\EQ12\\configs\\setup_badge_monitor_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "setup_docker_wsl",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\setup_docker_wsl.ps1",
        "config_path": "C:\\EQ12\\configs\\setup_docker_wsl_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "setup_git_gpg",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\setup_git_gpg.ps1",
        "config_path": "C:\\EQ12\\configs\\setup_git_gpg_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "setup_orchestrator_schedule",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\setup_orchestrator_schedule.ps1",
        "config_path": "C:\\EQ12\\configs\\setup_orchestrator_schedule_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "setup_rotation_reminder",
        "type": "automation",
        "script_path": "C:\\EQ12\\scripts\\setup_rotation_reminder.ps1",
        "config_path": "C:\\EQ12\\configs\\setup_rotation_reminder_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "deploy_github_security",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\deploy_github_security.py",
        "config_path": "C:\\EQ12\\configs\\deploy_github_security_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_enhanced_security_ai_integration",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_enhanced_security_ai_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_enhanced_security_ai_integration_config.json",
        "dependencies": [
            "openai"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_extension_security_auditor",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_extension_security_auditor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_extension_security_auditor_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_network_security_analyzer",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_network_security_analyzer.py",
        "config_path": "C:\\EQ12\\configs\\eq12_network_security_analyzer_config.json",
        "dependencies": [
            "pandas",
            "numpy"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_reporting_security_comms_hub",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_reporting_security_comms_hub.py",
        "config_path": "C:\\EQ12\\configs\\eq12_reporting_security_comms_hub_config.json",
        "dependencies": [
            "telegram",
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_security_intelligence_hub",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_security_intelligence_hub.py",
        "config_path": "C:\\EQ12\\configs\\eq12_security_intelligence_hub_config.json",
        "dependencies": [
            "openai",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_security_scanner",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_security_scanner.py",
        "config_path": "C:\\EQ12\\configs\\eq12_security_scanner_config.json",
        "dependencies": [
            "requests",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_snyk_security_integration",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_snyk_security_integration.py",
        "config_path": "C:\\EQ12\\configs\\eq12_snyk_security_integration_config.json",
        "dependencies": [
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_gitleaks_guardian",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_gitleaks_guardian.py",
        "config_path": "C:\\EQ12\\configs\\eq12_gitleaks_guardian_config.json",
        "dependencies": [
            "discord",
            "openai",
            "telegram"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_gitleaks_monitor",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_gitleaks_monitor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_gitleaks_monitor_config.json",
        "dependencies": [
            "openai",
            "eq12_"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "audit_imports",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\audit_imports.py",
        "config_path": "C:\\EQ12\\configs\\audit_imports_config.json",
        "dependencies": [],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    },
    {
        "name": "eq12_extension_security_auditor",
        "type": "security",
        "script_path": "C:\\EQ12\\scripts\\eq12_extension_security_auditor.py",
        "config_path": "C:\\EQ12\\configs\\eq12_extension_security_auditor_config.json",
        "dependencies": [
            "requests"
        ],
        "status": "unknown",
        "last_health_check": null,
        "performance_metrics": {}
    }
];
        this.updateInterval = 5000; // 5 seconds
        this.isConnected = true;
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.setupRealTimeUpdates();
        this.updateSystemTime();
        this.initCharts();
        this.startHealthMonitoring();
    }
    
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        const sections = document.querySelectorAll('.panel-section');
        
        navButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active classes
                navButtons.forEach(b => b.classList.remove('active'));
                sections.forEach(s => s.classList.remove('active'));
                
                // Add active class to clicked button and corresponding section
                btn.classList.add('active');
                const sectionId = btn.dataset.section + '-section';
                document.getElementById(sectionId).classList.add('active');
            });
        });
    }
    
    setupRealTimeUpdates() {
        setInterval(() => {
            this.updateComponentStatus();
            this.updateSystemMetrics();
            this.updatePerformanceChart();
        }, this.updateInterval);
    }
    
    updateSystemTime() {
        setInterval(() => {
            const now = new Date();
            document.getElementById('system-time').textContent = 
                now.toISOString().slice(0, 19).replace('T', ' ') + ' UTC';
        }, 1000);
    }
    
    updateComponentStatus() {
        this.components.forEach(component => {
            const card = document.querySelector(`[data-component="${component.name}"]`);
            if (card) {
                // Simulate real-time metrics
                const cpuUsage = Math.floor(Math.random() * 30) + 10;
                const memUsage = Math.floor(Math.random() * 200) + 50;
                
                card.querySelector('.cpu-usage').textContent = cpuUsage + '%';
                card.querySelector('.memory-usage').textContent = memUsage + 'MB';
                
                // Update status indicator based on performance
                const statusIndicator = card.querySelector('.status-indicator');
                if (cpuUsage > 80 || memUsage > 400) {
                    statusIndicator.className = 'status-indicator warning';
                } else {
                    statusIndicator.className = 'status-indicator running';
                }
            }
        });
        
        // Update active components count
        const activeCount = this.components.filter(c => Math.random() > 0.1).length;
        document.getElementById('active-components').textContent = activeCount;
    }
    
    updateSystemMetrics() {
        // Update system health percentage
        const healthPercentage = Math.floor(Math.random() * 10) + 90;
        document.getElementById('health-percentage').textContent = healthPercentage + '%';
        
        // Update system health indicator
        const healthIndicator = document.getElementById('system-health');
        if (healthPercentage > 95) {
            healthIndicator.style.color = 'var(--accent-green)';
        } else if (healthPercentage > 85) {
            healthIndicator.style.color = 'var(--accent-yellow)';
        } else {
            healthIndicator.style.color = 'var(--accent-red)';
        }
    }
    
    initCharts() {
        const ctx = document.getElementById('performance-chart');
        if (ctx) {
            this.performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array.from({length: 10}, (_, i) => `${i * 5}s`),
                    datasets: [{
                        label: 'Win Rate %',
                        data: Array.from({length: 10}, () => Math.random() * 2 + 0.5),
                        borderColor: 'var(--accent-green)',
                        backgroundColor: 'rgba(33, 191, 115, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 3,
                            ticks: {
                                color: 'var(--text-secondary)'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'var(--text-secondary)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'var(--text-primary)'
                            }
                        }
                    }
                }
            });
        }
    }
    
    updatePerformanceChart() {
        if (this.performanceChart) {
            // Shift data and add new point
            this.performanceChart.data.datasets[0].data.shift();
            this.performanceChart.data.datasets[0].data.push(Math.random() * 2 + 0.5);
            this.performanceChart.update('none');
        }
    }
    
    startHealthMonitoring() {
        // Simulate connection status
        setInterval(() => {
            this.isConnected = Math.random() > 0.05; // 95% uptime simulation
            this.updateConnectionStatus();
        }, 10000);
    }
    
    updateConnectionStatus() {
        const healthIndicator = document.getElementById('system-health');
        if (this.isConnected) {
            healthIndicator.textContent = '●';
            healthIndicator.title = 'System Online';
        } else {
            healthIndicator.textContent = '○';
            healthIndicator.title = 'System Offline';
            healthIndicator.style.color = 'var(--accent-red)';
            this.addAlert('Connection lost to system components', 'error');
        }
    }
    
    addAlert(message, type = 'info') {
        const alertsContainer = document.getElementById('alerts-list');
        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        alert.textContent = new Date().toLocaleTimeString() + ': ' + message;
        
        alertsContainer.insertBefore(alert, alertsContainer.firstChild);
        
        // Remove old alerts (keep only 5)
        while (alertsContainer.children.length > 5) {
            alertsContainer.removeChild(alertsContainer.lastChild);
        }
    }
}

// Component control functions
function controlComponent(componentName, action) {
    console.log(`${action.toUpperCase()} command sent to ${componentName}`);
    
    // Simulate API call
    fetch('/api/components/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            component: componentName,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        hmi.addAlert(`${componentName} ${action} command executed`, 'info');
    })
    .catch(error => {
        hmi.addAlert(`Failed to ${action} ${componentName}: ${error}`, 'error');
    });
}

// Initialize HMI controller when page loads
let hmi;
document.addEventListener('DOMContentLoaded', () => {
    hmi = new EQ12HMIController();
    hmi.addAlert('EQ12 HMI Dashboard initialized successfully', 'info');
});

// Export for external use
window.EQ12HMI = {
    controller: () => hmi,
    addAlert: (msg, type) => hmi.addAlert(msg, type),
    updateComponent: (name, status) => hmi.updateComponentStatus(name, status)
};
        