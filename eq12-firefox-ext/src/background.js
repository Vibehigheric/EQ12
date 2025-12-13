// background.js - Firefox compatible version
const DEFAULTS = {
    apiBase: "http://localhost:8000", // EQ12 FastAPI backend
    apiKey: "eq12-test-key-2025"     // Default API key for EQ12
};

// Use chrome API with Firefox compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

async function getSettings() {
    const s = await browserAPI.storage.local.get(["apiBase", "apiKey"]);
    return {
        apiBase: s.apiBase || DEFAULTS.apiBase,
        apiKey: s.apiKey || DEFAULTS.apiKey
    };
}

async function callEq12(path, params = {}) {
    const { apiBase, apiKey } = await getSettings();
    const url = new URL(path, apiBase);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

    const headers = {
        "Content-Type": "application/json",
        "X-API-Key": apiKey
    }; try {
        const res = await fetch(url.toString(), {
            headers,
            mode: 'cors'
        });

        if (!res.ok) {
            throw new Error(`EQ12 ${res.status}: ${await res.text()}`);
        }

        return res.json();
    } catch (error) {
        console.error('EQ12 API Error:', error);
        throw error;
    }
}

// Runtime message router from popup/content
browserAPI.runtime.onMessage.addListener(async (msg) => {
    try {
        if (msg.type === "GET_PARLAY") {
            const data = await callEq12("/api/parlay", {
                size: String(msg.size || 5)
            });
            return { ok: true, data };
        }

        if (msg.type === "GET_AUDIT") {
            const data = await callEq12("/api/audit", {
                last: String(msg.last || 5)
            });
            return { ok: true, data };
        }

        if (msg.type === "GET_SETTINGS") {
            const settings = await getSettings();
            return { ok: true, settings };
        }

        if (msg.type === "SET_SETTINGS") {
            await browserAPI.storage.local.set({
                apiBase: msg.apiBase,
                apiKey: msg.apiKey
            });
            return { ok: true };
        }

        if (msg.type === "PING") {
            const data = await callEq12("/api/ping");
            return { ok: true, data };
        }

        if (msg.type === "GET_HEALTH") {
            const data = await callEq12("/api/health");
            return { ok: true, data };
        }

        if (msg.type === "CHECK_EV") {
            const data = await callEq12("/api/check-ev", {
                selection: msg.selection,
                odds: msg.odds
            });
            return { ok: true, data };
        }

    } catch (err) {
        console.error('Background script error:', err);
        return { ok: false, error: String(err) };
    }
});

// Show notification when extension is installed
browserAPI.runtime.onInstalled.addListener(() => {
    browserAPI.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon-48.png',
        title: 'EQ12 Extension Installed',
        message: 'Ready to generate parlays and audit reports!'
    });
});
