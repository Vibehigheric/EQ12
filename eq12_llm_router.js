// EQ12 LLM Model Router for Node.js
// Provides model fallback and failover capabilities

const FALLBACK_MODELS = (process.env.OPENAI_FALLBACK_MODELS || 'gpt-4o-mini,gpt-4-turbo,gpt-4,gpt-3.5-turbo')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);

function* modelPriority(primaryModel = null) {
    const primary = primaryModel || process.env.OPENAI_MODEL || 'gpt-4o';
    const seen = new Set();

    // Always try primary first
    if (!seen.has(primary)) {
        seen.add(primary);
        yield primary;
    }

    // Then try fallbacks in order
    for (const model of FALLBACK_MODELS) {
        if (!seen.has(model)) {
            seen.add(model);
            yield model;
        }
    }
}

async function callWithFallback(callFn, primaryModel = null) {
    const errors = [];

    for (const model of modelPriority(primaryModel)) {
        try {
            console.log(`[EQ12Router] Trying model: ${model}`);
            return await callFn(model);
        } catch (error) {
            const errorInfo = {
                model,
                status: error.status || error.code || 'unknown',
                message: String(error.message || error)
            };

            errors.push(errorInfo);
            console.warn(`[EQ12Router] Model ${model} failed:`, errorInfo);

            // Stop on quota/billing issues (don't waste calls)
            if (/insufficient.quota|billing|account/i.test(errorInfo.message)) {
                console.error(`[EQ12Router] Quota/billing issue detected, stopping fallback chain`);
                break;
            }

            // Continue on rate limits, timeouts, temporary issues
            if (/429|rate.limit|timeout|temporar|unavailable|5xx/i.test(String(errorInfo.status) + errorInfo.message)) {
                continue; // Try next model
            }

            // For other errors, also try next model
            continue;
        }
    }

    // All models failed
    const lastError = errors[errors.length - 1] || { model: 'unknown', status: 'unknown', message: 'No models available' };
    const error = new Error(`All models failed. Last: ${lastError.model} → ${lastError.status} ${lastError.message}`);
    error.attempts = errors;
    throw error;
}

// Example OpenAI API wrapper
async function chatCompletion(messages, options = {}) {
    const { model, ...otherOptions } = options;

    return await callWithFallback(async (modelToUse) => {
        // Replace this with your actual OpenAI API call
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: modelToUse,
                messages,
                ...otherOptions
            })
        });

        if (!response.ok) {
            const error = new Error(`HTTP ${response.status}`);
            error.status = response.status;
            error.response = response;
            throw error;
        }

        return response.json();
    }, model);
}

// Health check function
async function checkModelHealth(model = null) {
    try {
        const result = await chatCompletion(
            [{ role: 'user', content: 'ping' }],
            { model, max_tokens: 5 }
        );
        return { success: true, model: result.model, usage: result.usage };
    } catch (error) {
        return {
            success: false,
            model: model || 'unknown',
            error: error.message,
            status: error.status
        };
    }
}

module.exports = {
    modelPriority,
    callWithFallback,
    chatCompletion,
    checkModelHealth
};
