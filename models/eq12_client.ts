/**
 * EQ12 Production Model Client - Node.js/TypeScript
 * Expert-level wrapper for GPT-4o/o1 with EQ12-specific optimizations
 */

import OpenAI from 'openai';
import { z } from 'zod';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';

// EQ12 Configuration Schema
const EQ12ConfigSchema = z.object({
  // Model selection
  extractionModel: z.string().default('gpt-4o-mini-2024-07-18'),
  reasoningModel: z.string().default('gpt-4o-2024-11-20'),
  planningModel: z.string().default('o1-2024-12-17'),
  
  // Temperature settings
  extractionTemp: z.number().min(0).max(2).default(0.0),
  reasoningTemp: z.number().min(0).max(2).default(0.1),
  planningTemp: z.number().min(0).max(2).default(0.1),
  
  // EQ12 constraints
  allowedBooks: z.array(z.string()).default(['draftkings', 'fanduel', 'betmgm']),
  maxLegsPerParlay: z.number().int().min(2).max(8).default(8),
  minEvThreshold: z.number().min(0).default(0.02),
  kellyCapPerLeg: z.number().min(0).max(0.05).default(0.025),
});

type EQ12Config = z.infer<typeof EQ12ConfigSchema>;

// Response schemas for validation
const OddsExtractSchema = z.object({
  rows: z.array(z.object({
    game_id: z.string().regex(/^nfl_\d{8}_[a-z]+_[a-z]+$/),
    book: z.enum(['draftkings', 'fanduel', 'betmgm']),
    market: z.enum(['moneyline', 'spread', 'total']),
    selection: z.string().min(1),
    point: z.number().nullable(),
    american_odds: z.number().int().min(-999).max(999),
    last_update_utc: z.string().datetime(),
    hook_flag: z.boolean().optional(),
  })),
  extracted_at_utc: z.string().datetime(),
  books_found: z.array(z.enum(['draftkings', 'fanduel', 'betmgm'])),
  stale_warning: z.boolean().optional(),
  total_rows: z.number().int().min(0),
});

const ParlayBuildSchema = z.object({
  parlays: z.array(z.object({
    parlay_id: z.string(),
    book: z.enum(['draftkings', 'fanduel', 'betmgm']),
    strategy: z.enum(['hook_spread', 'value_hunt', 'steam_chase', 'low_correlation', 'total_hooks', 'moneyline_dog']),
    legs: z.array(z.object({
      game_id: z.string().regex(/^nfl_\d{8}_[a-z]+_[a-z]+$/),
      market: z.enum(['moneyline', 'spread', 'total']),
      selection: z.string(),
      american_odds: z.number().int(),
      model_prob: z.number().min(0).max(1),
      ev_percent: z.number(),
      kelly_fraction: z.number().min(0).max(0.025),
      why: z.string().max(100),
    })).min(2).max(8),
    combined_odds: z.number().int(),
    stake_recommendation: z.number().min(0),
    risk_assessment: z.object({
      overall_risk: z.enum(['LOW', 'MEDIUM', 'HIGH']),
      correlation_risk: z.number().min(0).max(1),
      stale_data_risk: z.boolean(),
    }),
  })),
  generation_time_utc: z.string().datetime(),
  notes: z.string().max(500).optional(),
});

type OddsExtract = z.infer<typeof OddsExtractSchema>;
type ParlayBuild = z.infer<typeof ParlayBuildSchema>;

interface EQ12Response<T> {
  success: boolean;
  data?: T;
  error?: string;
  model_used: string;
  tokens?: number;
  fallback_reason?: string;
}

export class EQ12ModelClient {
  private client: OpenAI;
  private config: EQ12Config;
  private requestCount = 0;

  constructor(config: Partial<EQ12Config> = {}) {
    this.config = EQ12ConfigSchema.parse(config);
    this.client = new OpenAI();
  }

  private generateIdempotencyKey(content: string): string {
    this.requestCount += 1;
    const contentHash = crypto.createHash('md5').update(content).digest('hex').slice(0, 8);
    return `eq12_${Math.floor(Date.now() / 1000)}_${this.requestCount}_${contentHash}`;
  }

  /**
   * Extract and normalize odds to EQ12 JSON format
   * Fast path using gpt-4o-mini with strict schema
   */
  async extractOdds(
    rawOdds: string,
    markets: string[] = ['moneyline', 'spread', 'total'],
    timeout: number = 30000
  ): Promise<EQ12Response<OddsExtract>> {
    
    const instructions = `Extract ONLY ${this.config.allowedBooks.join(', ')} odds. ` +
                        `Markets: ${markets.join(', ')}. ` +
                        `Emit UTC RFC3339 timestamps. Drop other books. No prose.`;

    const oddsExtractSchema = {
      name: 'OddsRows',
      schema: {
        type: 'object',
        properties: {
          rows: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                game_id: { type: 'string' },
                book: { enum: this.config.allowedBooks },
                market: { enum: ['moneyline', 'spread', 'total'] },
                selection: { type: 'string' },
                point: { type: ['number', 'null'] },
                american_odds: { type: 'integer' },
                last_update_utc: { type: 'string', format: 'date-time' },
                hook_flag: { type: 'boolean' }
              },
              required: ['game_id', 'book', 'market', 'selection', 'american_odds', 'last_update_utc']
            }
          },
          extracted_at_utc: { type: 'string', format: 'date-time' },
          books_found: { type: 'array', items: { enum: this.config.allowedBooks } },
          stale_warning: { type: 'boolean' },
          total_rows: { type: 'integer' }
        },
        required: ['rows', 'extracted_at_utc', 'books_found', 'total_rows'],
        additionalProperties: false
      }
    };

    const idempotencyKey = this.generateIdempotencyKey(rawOdds);

    try {
      const response = await this.client.chat.completions.create({
        model: this.config.extractionModel,
        temperature: this.config.extractionTemp,
        messages: [
          { role: 'system', content: instructions },
          { role: 'developer', content: 'Return strictly valid JSON per schema.' },
          { role: 'user', content: rawOdds }
        ],
        response_format: { type: 'json_schema', json_schema: oddsExtractSchema },
        timeout,
      }, {
        headers: { 'Idempotency-Key': idempotencyKey }
      });

      const result = JSON.parse(response.choices[0].message.content!);
      
      // Validate with Zod schema
      const validatedResult = OddsExtractSchema.parse(result);

      return {
        success: true,
        data: validatedResult,
        model_used: this.config.extractionModel,
        tokens: response.usage?.total_tokens || 0
      };

    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
        model_used: this.config.extractionModel
      };
    }
  }

  /**
   * Build parlays with EQ12 constraints using reasoning model
   * Uses gpt-4o with structured output for constraint satisfaction
   */
  async buildParlays(
    oddsData: OddsExtract['rows'],
    bankroll: number,
    minEv: number = this.config.minEvThreshold,
    maxLegs: number = this.config.maxLegsPerParlay,
    strategy: string = 'value_hunt'
  ): Promise<EQ12Response<ParlayBuild>> {

    const instructions = `You are EQ12 Parlay Assistant. ` +
                        `Rules: one leg per game; books ∈ {${this.config.allowedBooks.join(',')}}; ` +
                        `UTC times; min EV ≥ ${minEv}; max ${maxLegs} legs per parlay. ` +
                        `If no valid legs, return empty parlays array with explanation in notes.`;

    const inputData = {
      bankroll,
      min_ev: minEv,
      max_legs: maxLegs,
      strategy,
      kelly_cap: this.config.kellyCapPerLeg,
      odds: oddsData
    };

    const parlaySchema = {
      name: 'ParlayConstruction',
      schema: {
        type: 'object',
        properties: {
          parlays: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                parlay_id: { type: 'string' },
                book: { enum: this.config.allowedBooks },
                strategy: { enum: ['hook_spread', 'value_hunt', 'steam_chase', 'low_correlation'] },
                legs: {
                  type: 'array',
                  minItems: 2,
                  maxItems: maxLegs,
                  items: {
                    type: 'object',
                    properties: {
                      game_id: { type: 'string' },
                      market: { enum: ['moneyline', 'spread', 'total'] },
                      selection: { type: 'string' },
                      american_odds: { type: 'integer' },
                      model_prob: { type: 'number', minimum: 0, maximum: 1 },
                      ev_percent: { type: 'number' },
                      kelly_fraction: { type: 'number', minimum: 0, maximum: this.config.kellyCapPerLeg },
                      why: { type: 'string', maxLength: 100 }
                    },
                    required: ['game_id', 'market', 'selection', 'american_odds', 'model_prob', 'ev_percent', 'kelly_fraction']
                  }
                },
                combined_odds: { type: 'integer' },
                stake_recommendation: { type: 'number', minimum: 0 },
                risk_assessment: {
                  type: 'object',
                  properties: {
                    overall_risk: { enum: ['LOW', 'MEDIUM', 'HIGH'] },
                    correlation_risk: { type: 'number', minimum: 0, maximum: 1 },
                    stale_data_risk: { type: 'boolean' }
                  },
                  required: ['overall_risk', 'correlation_risk', 'stale_data_risk']
                }
              },
              required: ['parlay_id', 'book', 'legs', 'combined_odds', 'stake_recommendation', 'risk_assessment']
            }
          },
          generation_time_utc: { type: 'string', format: 'date-time' },
          notes: { type: 'string', maxLength: 500 }
        },
        required: ['parlays', 'generation_time_utc'],
        additionalProperties: false
      }
    };

    const idempotencyKey = this.generateIdempotencyKey(JSON.stringify(inputData));

    try {
      const response = await this.client.chat.completions.create({
        model: this.config.reasoningModel,
        temperature: this.config.reasoningTemp,
        messages: [
          { role: 'system', content: instructions },
          { role: 'developer', content: 'Return ONLY JSON. Validate unique games and book constraints.' },
          { role: 'user', content: JSON.stringify(inputData) }
        ],
        response_format: { type: 'json_schema', json_schema: parlaySchema },
      }, {
        headers: { 'Idempotency-Key': idempotencyKey }
      });

      const result = JSON.parse(response.choices[0].message.content!);
      
      // Post-process validation
      const validatedResult = this.validateParlays(result);
      const finalResult = ParlayBuildSchema.parse(validatedResult);

      return {
        success: true,
        data: finalResult,
        model_used: this.config.reasoningModel,
        tokens: response.usage?.total_tokens || 0
      };

    } catch (error) {
      // Fallback to simpler model
      return this.fallbackParlayBuild(oddsData, bankroll, minEv, maxLegs, error instanceof Error ? error.message : String(error));
    }
  }

  /**
   * Post-process parlay validation and filtering
   */
  private validateParlays(result: any): any {
    if (!result.parlays) return result;

    const validatedParlays = [];

    for (const parlay of result.parlays) {
      if (!parlay.legs) continue;

      const booksUsed = new Set<string>();
      const validLegs = [];
      const gameIdsSeen = new Set<string>();

      for (const leg of parlay.legs) {
        // Enforce allowed books
        if (!this.config.allowedBooks.includes(leg.book)) continue;
        
        // Enforce one leg per game
        if (gameIdsSeen.has(leg.game_id)) continue;
        
        booksUsed.add(leg.book);
        validLegs.push(leg);
        gameIdsSeen.add(leg.game_id);
      }

      // Single book per parlay
      if (booksUsed.size === 1 && validLegs.length >= 2) {
        parlay.legs = validLegs;
        parlay.book = Array.from(booksUsed)[0];
        validatedParlays.push(parlay);
      }
    }

    result.parlays = validatedParlays;
    return result;
  }

  /**
   * Fallback to simpler model if reasoning model fails
   */
  private async fallbackParlayBuild(
    oddsData: OddsExtract['rows'],
    bankroll: number,
    minEv: number,
    maxLegs: number,
    errorMsg: string
  ): Promise<EQ12Response<ParlayBuild>> {
    try {
      const response = await this.client.chat.completions.create({
        model: this.config.extractionModel,
        temperature: 0.2,
        messages: [
          { role: 'system', content: `Build simple parlays. Books: ${this.config.allowedBooks.join(', ')} only.` },
          { role: 'user', content: JSON.stringify({ bankroll, odds: oddsData.slice(0, 10) })} // Limit complexity
        ],
        response_format: { type: 'json_object' }
      });

      const result = JSON.parse(response.choices[0].message.content!);

      return {
        success: true,
        data: result as ParlayBuild,
        model_used: `${this.config.extractionModel} (fallback)`,
        fallback_reason: errorMsg,
        tokens: response.usage?.total_tokens || 0
      };

    } catch (fallbackError) {
      return {
        success: false,
        error: `Primary: ${errorMsg}, Fallback: ${fallbackError instanceof Error ? fallbackError.message : String(fallbackError)}`,
        model_used: 'fallback_failed'
      };
    }
  }

  /**
   * Generate human-readable parlay explanation
   * Fast summary using gpt-4o-mini
   */
  async explainParlay(parlayJson: ParlayBuild['parlays'][0], maxWords: number = 80): Promise<string> {
    const instructions = `Explain this parlay in exactly 5 bullet points, ≤${maxWords} words total. ` +
                        `Format: Strategy, Risk Level, Best Edge, Stake, Timing. Be concise and factual.`;

    try {
      const response = await this.client.chat.completions.create({
        model: this.config.extractionModel,
        temperature: 0.3, // Slight creativity for readability
        messages: [
          { role: 'system', content: instructions },
          { role: 'user', content: JSON.stringify(parlayJson) }
        ]
      });

      return response.choices[0].message.content?.trim() || 'Error generating explanation';

    } catch (error) {
      return `Error generating explanation: ${error instanceof Error ? error.message : String(error)}`;
    }
  }

  /**
   * Validate and repair malformed JSON
   */
  async validateAndRepair(invalidJson: string, targetSchema: string = 'parlay_build'): Promise<EQ12Response<any>> {
    const instructions = `Fix this JSON to match ${targetSchema} schema. ` +
                        `Correct syntax errors, add missing fields, remove invalid fields. ` +
                        `Return only valid JSON, no explanations.`;

    try {
      const response = await this.client.chat.completions.create({
        model: this.config.reasoningModel,
        temperature: 0.0, // Deterministic repair
        messages: [
          { role: 'system', content: instructions },
          { role: 'user', content: invalidJson }
        ],
        response_format: { type: 'json_object' }
      });

      const repaired = JSON.parse(response.choices[0].message.content!);

      return {
        success: true,
        data: repaired,
        model_used: this.config.reasoningModel
      };

    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
        model_used: this.config.reasoningModel
      };
    }
  }
}

// Usage Example
async function example() {
  const client = new EQ12ModelClient({
    allowedBooks: ['draftkings', 'fanduel', 'betmgm'],
    minEvThreshold: 0.03,
    kellyCapPerLeg: 0.02
  });

  // Extract odds
  const rawOdds = `
    DraftKings: Chiefs -3 (-110), Bills +3 (-110), O/U 45.5
    FanDuel: Chiefs -2.5 (-105), Bills +2.5 (-115), O/U 46
    BetMGM: Chiefs -3 (-108), Bills +3 (-112), O/U 45
  `;

  const oddsResult = await client.extractOdds(rawOdds);
  console.log('Odds extraction:', oddsResult.success);

  if (oddsResult.success && oddsResult.data) {
    // Build parlays
    const parlayResult = await client.buildParlays(
      oddsResult.data.rows,
      1000, // bankroll
      0.025, // min EV
      4 // max legs
    );
    
    console.log('Parlay construction:', parlayResult.success);
    
    if (parlayResult.success && parlayResult.data?.parlays.length > 0) {
      // Generate explanation
      const explanation = await client.explainParlay(parlayResult.data.parlays[0]);
      console.log('Explanation:', explanation);
    }
  }
}

export default EQ12ModelClient;