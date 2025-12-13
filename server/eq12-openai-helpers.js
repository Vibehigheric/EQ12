// Node.js OpenAI client wrapper with fallback behavior
// Mirrors the Python eq12_helpers.py functionality

const { EventEmitter } = require('events');

class RateBudget {
    constructor(rpm = 400, tpm = 800000) {
        this.rpm = rpm;
        this.tpm = tpm;
        this._r_calls = 0;
        this._r_tokens = 0;
        this._window_start = Date.now();
    }

    _resetIfNeeded() {
        if (Date.now() - this._window_start >= 60000) {
            this._window_start = Date.now();
            this._r_calls = 0;
            this._r_tokens = 0;
        }
    }

    admit(estTokens = 0) {
        this._resetIfNeeded();
        if (this._r_calls + 1 > this.rpm || this._r_tokens + estTokens > this.tpm) {
            const sleepFor = 60000 - (Date.now() - this._window_start);
            if (sleepFor > 0) {
                return new Promise(resolve => setTimeout(resolve, Math.max(50, sleepFor)));
            }
            this._resetIfNeeded();
        }
        this._r_calls += 1;
        this._r_tokens += Math.max(0, estTokens);
        return Promise.resolve();
    }
}

class CircuitBreaker extends EventEmitter {
    constructor() {
        super();
        this.state = {
            offline: false,
            until: null,
            reason: null
        };
    }

    isOpen() {
        if (!this.state.offline) return false;
        if (this.state.until && Date.now() >= this.state.until) {
            // auto reset
            this.state = { offline: false, until: null, reason: null };
            this.emit('reset');
            return false;
        }
        return true;
    }

    trip(seconds, reason) {
        this.state = {
            offline: true,
            until: Date.now() + (seconds * 1000),
            reason
        };
        this.emit('trip', reason);
    }
}

function parseRetryAfter(headers = {}) {
    const candidates = ['retry-after', 'Retry-After', 'x-ratelimit-reset-requests'];
    for (const key of candidates) {
        if (headers[key]) {
            const val = parseFloat(headers[key]);
            if (!isNaN(val)) return val * 1000; // convert to ms
        }
    }
    return null;
}

function* backoffSequence() {
    const raw = process.env.EQ12_RETRY_BACKOFF_MS || "500,1000,2000,4000,8000,12000";
    for (const part of raw.split(',')) {
        const ms = parseInt(part.trim(), 10);
        if (!isNaN(ms)) yield ms;
    }
}

function chooseModel(task = '') {
    const t = task.toLowerCase();

    if (['boolean', 'validator', 'parlay', 'risk', 'refactor', 'root-cause'].some(k => t.includes(k))) {
        return process.env.OPENAI_MODEL_PRIMARY || 'gpt-4o';
    }

    if (['ui', 'summary', 'props', 'news', 'delta', 'explain', 'dashboard'].some(k => t.includes(k))) {
        return process.env.OPENAI_MODEL_FAST || 'gpt-4o-mini';
    }

    return process.env.OPENAI_MODEL_BULK || 'gpt-3.5-turbo';
}

function buildJsonPayload(model, messages, maxTokens = 1500, extra = {}) {
    return {
        model,
        messages,
        response_format: { type: "json_object" },
        temperature: parseFloat(process.env.EQ12_TEMPERATURE || "0.2"),
        max_tokens: maxTokens,
        ...extra
    };
}

async function callWithFallbacks(createClient, payloadBuilder, taskLabel, onResult = null) {
    const logger = console; // or use your preferred logger

    if (globalBreaker.isOpen()) {
        throw new Error(`LLM breaker open: ${globalBreaker.state.reason}`);
    }

    // Build model queue
    const models = [];
    if (process.env.OPENAI_MODEL_SNAPSHOT) {
        models.push(process.env.OPENAI_MODEL_SNAPSHOT);
    }
    models.push(chooseModel(taskLabel));

    const fallbacks = (process.env.OPENAI_FALLBACK_MODELS || "")
        .split(',')
        .map(m => m.trim())
        .filter(m => m);
    models.push(...fallbacks);

    // De-duplicate
    const modelQueue = [...new Set(models.filter(m => m))];

    const client = createClient();
    const budget = new RateBudget(
        parseInt(process.env.EQ12_RPM_BUDGET || "400", 10),
        parseInt(process.env.EQ12_TPM_BUDGET || "800000", 10)
    );

    let lastErr = null;

    for (const model of modelQueue) {
        const payload = payloadBuilder(model);

        // Rough token estimate
        const estTokens = Math.floor(JSON.stringify(payload.messages || []).length / 4) +
            (payload.max_tokens || 0);

        await budget.admit(estTokens);

        const delays = [0, ...backoffSequence()];

        for (const delay of delays) {
            if (delay > 0) {
                await new Promise(resolve => setTimeout(resolve, delay));
            }

            try {
                const response = await client.chat.completions.create(payload);
                return onResult ? onResult(response) : response;
            } catch (error) {
                const msg = error.message || '';

                // Check for quota issues
                if (msg.includes('insufficient_quota') || msg.includes('quota')) {
                    globalBreaker.trip(15 * 60, 'insufficient_quota'); // 15 minutes
                    logger.warn('Quota exhausted; breaker tripped for 15m');
                    throw error;
                }

                // Rate limit
                if (msg.includes('429') || msg.toLowerCase().includes('rate limit')) {
                    const retryAfter = parseRetryAfter(error.headers);
                    if (retryAfter) {
                        await new Promise(resolve => setTimeout(resolve, retryAfter));
                    }
                    lastErr = error;
                    continue;
                }

                // 5xx transient errors
                if (['502', '503', '504'].some(code => msg.includes(code)) ||
                    msg.toLowerCase().includes('temporar')) {
                    lastErr = error;
                    continue;
                }

                // Non-retryable error
                throw error;
            }
        }

        logger.warn(`Model failed after retries: ${model}`);
    }

    if (lastErr) throw lastErr;
    throw new Error('All models unavailable');
}

function offlineStub(task, messages = []) {
    return {
        mode: "offline",
        task,
        summary: "Operating in offline mode — using local heuristics.",
        messages_seen: messages.length,
        timestamp: Date.now()
    };
}

function startLlmHealthProbe(createClient, intervalSec = 900) {
    const logger = console;

    function probe() {
        setTimeout(probe, intervalSec * 1000);

        if (!globalBreaker.isOpen()) return;

        createClient().models.list()
            .then(() => {
                globalBreaker.state = { offline: false, until: null, reason: null };
                logger.info('LLM breaker cleared by health probe');
            })
            .catch(err => {
                logger.info(`Probe still failing: ${err.message}`);
            });
    }

    probe();
}

// Global breaker instance
const globalBreaker = new CircuitBreaker();

module.exports = {
    RateBudget,
    CircuitBreaker,
    chooseModel,
    buildJsonPayload,
    callWithFallbacks,
    offlineStub,
    startLlmHealthProbe,
    parseRetryAfter,
    backoffSequence,
    globalBreaker
};
