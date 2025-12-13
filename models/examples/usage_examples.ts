/**
 * EQ12 Production Model Client - TypeScript/Node.js Usage Examples
 * Expert-level integration patterns for OpenAI models with EQ12 constraints.
 * 
 * This demonstrates the complete workflow from raw odds → normalized data → parlays
 * using the task-specific model selection from your expert guide.
 */

import EQ12ModelClient, { EQ12Config } from '../eq12_client';

async function main(): Promise<void> {
    console.log('🎰 EQ12 Production Model Client - Node.js Examples');
    console.log('='.repeat(60));
    
    // ✅ Initialize with EQ12-specific constraints
    const config: EQ12Config = {
        allowedBooks: ['draftkings', 'fanduel', 'betmgm'],
        minEvThreshold: 0.03,  // 3% minimum edge
        kellyCapPerLeg: 0.025,  // 2.5% Kelly cap per leg
        maxCorrelationRisk: 0.15,  // Low correlation tolerance
        staleDataThresholdMinutes: 15  // Fresh data only
    };
    
    const client = new EQ12ModelClient(config);
    
    // ✅ Example 1: Extract odds from raw sportsbook data
    console.log('\n📊 STEP 1: Extract & normalize odds (gpt-4o-mini)');
    const rawOddsData = `
    DraftKings NFL Week 5:
    Kansas City Chiefs -3.0 (-110) vs Buffalo Bills +3.0 (-110)
    Total: Over 47.5 (-110), Under 47.5 (-110)
    Last updated: 2025-10-05 7:30 PM ET
    
    FanDuel NFL:
    Chiefs -2.5 (-105) vs Bills +2.5 (-115)  
    Total: O47.5 (-108), U47.5 (-112)
    Updated: Oct 5, 2025 7:35 PM
    
    BetMGM:
    KC Chiefs -3 (-108) vs BUF Bills +3 (-112)
    Over/Under: 47.5 O(-110)/U(-110)
    `;
    
    const oddsResult = await client.extractOdds(rawOddsData);
    
    if (oddsResult.success && oddsResult.data) {
        console.log(`✅ Extracted ${oddsResult.data.rows.length} odds entries`);
        console.log(`   Books found: ${oddsResult.data.booksFound.join(', ')}`);
        console.log(`   Model used: ${oddsResult.modelUsed} (${oddsResult.tokens} tokens)`);
        
        // Show sample extracted data
        oddsResult.data.rows.slice(0, 3).forEach(row => {
            console.log(`   • ${row.book}: ${row.selection} @ ${row.americanOdds}`);
        });
    } else {
        console.log(`❌ Odds extraction failed: ${oddsResult.error}`);
        return;
    }
    
    // ✅ Example 2: Build parlays with constraints (gpt-4o)
    console.log('\n🎯 STEP 2: Build parlays with reasoning (gpt-4o)');
    const parlayResult = await client.buildParlays(
        oddsResult.data!.rows,
        1000,  // $1000 bankroll
        0.025, // 2.5% minimum edge
        4      // Maximum 4-leg parlays
    );
    
    if (parlayResult.success && parlayResult.data) {
        const parlays = parlayResult.data.parlays;
        console.log(`✅ Generated ${parlays.length} profitable parlays`);
        console.log(`   Model used: ${parlayResult.modelUsed} (${parlayResult.tokens} tokens)`);
        
        parlays.slice(0, 2).forEach((parlay, i) => {  // Show first 2 parlays
            console.log(`\n   💰 Parlay #${i + 1} (${parlay.book}):`);
            console.log(`      Combined odds: ${parlay.combinedOdds}`);
            console.log(`      Stake: $${parlay.stakeRecommendation.toFixed(2)}`);
            console.log(`      Risk level: ${parlay.riskAssessment.overallRisk}`);
            
            parlay.legs.forEach(leg => {
                console.log(`      • ${leg.selection} @ ${leg.odds}`);
            });
        });
    } else {
        console.log(`❌ Parlay building failed: ${parlayResult.error}`);
        return;
    }
    
    // ✅ Example 3: Generate human explanations (gpt-4o-mini)  
    console.log('\n📝 STEP 3: Generate explanations (gpt-4o-mini)');
    
    if (parlayResult.data && parlayResult.data.parlays.length > 0) {
        const bestParlay = parlayResult.data.parlays[0];  // Take the first parlay
        const explanationResult = await client.explainParlay(bestParlay);
        
        if (explanationResult.success) {
            console.log('✅ Generated human explanation:');
            console.log(`   Model used: ${explanationResult.modelUsed} (${explanationResult.tokens} tokens)`);
            console.log(`\n📋 ${explanationResult.explanation}`);
        } else {
            console.log(`❌ Explanation failed: ${explanationResult.error}`);
        }
    }
    
    // ✅ Example 4: Validate and repair if needed (gpt-4o)
    console.log('\n🔧 STEP 4: Validate & repair (gpt-4o)');
    
    // Simulate corrupted data for repair example
    const corruptedParlay = {
        parlayId: 'invalid_test',
        book: 'unknown_book',  // Invalid book
        legs: [
            { gameId: 'same_game', selection: 'Team A', odds: 'invalid' as any },
            { gameId: 'same_game', selection: 'Team B', odds: '+150' }  // Correlation violation
        ],
        combinedOdds: 'not_a_number' as any,
        stakeRecommendation: 0,
        riskAssessment: { overallRisk: 'HIGH' as const, correlationRisk: 0, staleDataRisk: false }
    };
    
    const repairResult = await client.validateAndRepair(corruptedParlay);
    
    if (repairResult.success && repairResult.data) {
        console.log('✅ Validation and repair completed:');
        console.log(`   Model used: ${repairResult.modelUsed} (${repairResult.tokens} tokens)`);
        console.log(`   Violations found: ${repairResult.data.violationsFound.length}`);
        console.log(`   Repair successful: ${repairResult.data.repairSuccessful}`);
        
        if (repairResult.data.violationsFound.length > 0) {
            console.log('   Issues detected:');
            repairResult.data.violationsFound.forEach(violation => {
                console.log(`   • ${violation}`);
            });
        }
    } else {
        console.log(`❌ Validation failed: ${repairResult.error}`);
    }
    
    // ✅ Performance summary
    console.log('\n📊 PERFORMANCE SUMMARY');
    console.log('='.repeat(40));
    
    const totalTokens = (oddsResult.tokens || 0) + 
                       (parlayResult.tokens || 0) + 
                       0 + // explanation tokens would go here
                       (repairResult.tokens || 0);
    
    const totalTime = (oddsResult.executionTime || 0) + 
                     (parlayResult.executionTime || 0) + 
                     0 + // explanation time would go here 
                     (repairResult.executionTime || 0);
    
    console.log(`Total tokens used: ${totalTokens.toLocaleString()}`);
    console.log(`Total execution time: ${totalTime.toFixed(2)}s`);
    console.log(`Models used: gpt-4o-mini (extract/explain) + gpt-4o (build/repair)`);
    console.log('\n✅ EQ12 Expert Model Integration - Complete! 🎰');
}

async function advancedExamples(): Promise<void> {
    console.log('\n🚀 ADVANCED USAGE PATTERNS');
    console.log('='.repeat(50));
    
    const config: EQ12Config = {
        allowedBooks: ['draftkings', 'fanduel', 'betmgm'],
        minEvThreshold: 0.04,  // Higher threshold for selectivity
        kellyCapPerLeg: 0.02,  // Conservative Kelly
        maxCorrelationRisk: 0.1,  // Very low correlation
        staleDataThresholdMinutes: 10  // Very fresh data only
    };
    
    const client = new EQ12ModelClient(config);
    
    // ✅ Pattern 1: Batch processing with error handling
    console.log('\n📦 Batch Processing Example:');
    
    const multipleSources = [
        'DraftKings: Patriots -7 (-110) vs Jets +7 (-110)',
        'FanDuel: Lakers +5.5 (-108) vs Warriors -5.5 (-112)', 
        'BetMGM: Over 225.5 (-110) Under 225.5 (-110) Lakers vs Warriors'
    ];
    
    const batchResults = [];
    for (let i = 0; i < multipleSources.length; i++) {
        const source = multipleSources[i];
        console.log(`   Processing source ${i + 1}...`);
        const result = await client.extractOdds(source);
        batchResults.push(result);
        
        if (result.success && result.data) {
            console.log(`   ✅ Extracted ${result.data.rows.length} entries`);
        } else {
            console.log(`   ❌ Failed: ${result.error}`);
        }
    }
    
    const successfulExtractions = batchResults.filter(r => r.success);
    console.log(`\n   📊 Batch complete: ${successfulExtractions.length}/${multipleSources.length} successful`);
    
    // ✅ Pattern 2: Custom configuration for different risk profiles
    console.log('\n⚙️  Custom Risk Profile Example:');
    
    // Conservative profile
    const conservativeConfig: EQ12Config = {
        allowedBooks: ['draftkings'],  // Single book only
        minEvThreshold: 0.05,  // 5% minimum edge
        kellyCapPerLeg: 0.015,  // 1.5% Kelly cap
        maxCorrelationRisk: 0.05  // Very low correlation
    };
    
    // Aggressive profile  
    const aggressiveConfig: EQ12Config = {
        allowedBooks: ['draftkings', 'fanduel', 'betmgm'],
        minEvThreshold: 0.02,  // 2% minimum edge
        kellyCapPerLeg: 0.03,  // 3% Kelly cap
        maxCorrelationRisk: 0.2  // Higher correlation tolerance
    };
    
    console.log('   Conservative config: Single book, 5% min EV, 1.5% Kelly cap');
    console.log('   Aggressive config: All books, 2% min EV, 3% Kelly cap');
    console.log('   → Easily switch between risk profiles!');
}

// Run examples if called directly
if (require.main === module) {
    (async () => {
        try {
            // Run basic examples
            await main();
            
            // Run advanced patterns
            await advancedExamples();
            
            console.log('\n🎯 Examples complete! Check the integration guide for production deployment.');
            console.log('📁 Next: Integrate with your EQ12 scheduler workflow.');
        } catch (error) {
            console.error('❌ Example execution failed:', error);
        }
    })();
}

export { main as runBasicExamples, advancedExamples as runAdvancedExamples };