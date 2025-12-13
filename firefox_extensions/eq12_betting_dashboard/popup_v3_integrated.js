// EQ12 Enhanced Popup Script - Integrated with Backend API
const out = document.getElementById("out");
const btn5 = document.getElementById("btn-5");
const btn10 = document.getElementById("btn-10");
const btnAudit = document.getElementById("btn-audit");
const btnPrivacy = document.getElementById("btn-privacy");
const btnDevTools = document.getElementById("btn-dev-tools");
const btnVpn = document.getElementById("btn-vpn");
const openOptions = document.getElementById("open-options");
const openDashboard = document.getElementById("open-dashboard");
const copyResult = document.getElementById("copy-result");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const lastUpdate = document.getElementById("last-update");

let currentResult = null;

function show(obj, type = 'info') {
    out.className = `out ${type}`;
    out.style.display = 'block';

    if (typeof obj === "string") {
        out.textContent = obj;
    } else {
        out.textContent = JSON.stringify(obj, null, 2);
    }

    currentResult = obj;
    copyResult.style.display = currentResult ? 'inline' : 'none';

    // Update last update time
    lastUpdate.textContent = new Date().toLocaleTimeString();
}

function showLoading(message = "Loading...") {
    show(message, 'loading');
    copyResult.style.display = 'none';
}

function showError(error) {
    show(error, 'error');
    updateStatus(false, 'API Error');
}

function updateStatus(connected, message = '') {
    statusDot.className = `status-dot ${connected ? 'connected' : ''}`;
    statusText.textContent = connected ? 'Connected' : (message || 'Disconnected');
}

async function req(type, payload = {}) {
    try {
        updateStatus(false, 'Requesting...');
        const res = await browser.runtime.sendMessage({ type, ...payload });

        if (!res) {
            updateStatus(false, 'No Response');
            return show("No response from background service");
        }

        if (!res.ok) {
            updateStatus(false, 'API Error');
            return showError(res.error || "Unknown error occurred");
        }

        updateStatus(true);
        return res.data;
    } catch (err) {
        updateStatus(false, 'Request Failed');
        showError(`Request failed: ${err.message}`);
        return null;
    }
}

// Parlay Generation Functions
btn5.addEventListener("click", async () => {
    showLoading("🎯 Generating 5-leg parlay...");
    const data = await req("GET_PARLAY", { size: 5 });
    if (data) show(formatTicket(data));
});

btn10.addEventListener("click", async () => {
    showLoading("🎯 Generating 10-leg parlay...");
    const data = await req("GET_PARLAY", { size: 10 });
    if (data) show(formatTicket(data));
});

btnAudit.addEventListener("click", async () => {
    showLoading("📊 Fetching audit report...");
    const data = await req("GET_AUDIT", { last: 10 });
    if (data) show(formatAudit(data));
});

// Enhanced Feature Functions
btnPrivacy.addEventListener("click", async () => {
    showLoading("🛡️ Checking privacy protection...");
    const data = await req("GET_PRIVACY_STATUS");
    if (data) show(formatPrivacyStatus(data));
});

btnDevTools.addEventListener("click", async () => {
    showLoading("🔧 Getting developer tools status...");
    const data = await req("GET_DEV_TOOLS_STATUS");
    if (data) show(formatDevToolsStatus(data));
});

btnVpn.addEventListener("click", async () => {
    showLoading("🔐 Checking VPN connection...");
    const data = await req("GET_VPN_STATUS");
    if (data) show(formatVpnStatus(data));
});

// Navigation Functions
openOptions.addEventListener("click", (e) => {
    e.preventDefault();
    browser.runtime.openOptionsPage();
});

openDashboard.addEventListener("click", async (e) => {
    e.preventDefault();
    const settings = await req("GET_SETTINGS");
    if (settings && settings.apiBase) {
        const dashboardUrl = `${settings.apiBase}/dashboard`;
        browser.tabs.create({ url: dashboardUrl });
    } else {
        showError("Dashboard URL not configured. Please check Settings.");
    }
});

copyResult.addEventListener("click", async (e) => {
    e.preventDefault();
    if (currentResult) {
        try {
            const text = typeof currentResult === 'string' ? currentResult : JSON.stringify(currentResult, null, 2);
            await navigator.clipboard.writeText(text);

            // Show copied feedback
            const originalText = copyResult.textContent;
            copyResult.textContent = "✅ Copied!";
            copyResult.style.color = "#10b981";

            setTimeout(() => {
                copyResult.textContent = originalText;
                copyResult.style.color = "";
            }, 2000);
        } catch (err) {
            showError(`Failed to copy: ${err.message}`);
        }
    }
});

// Formatting Functions
function formatTicket(resp) {
    // Format parlay ticket response
    if (!resp || !resp.legs) return resp;

    const header = `🎟️ ${resp.name || "EQ12 Parlay"}\n${"=".repeat(30)}`;
    const legs = resp.legs.map((l, i) =>
        `${i + 1}. ${l.selection} (${formatOdds(l.price)})`
    ).join("\n");

    const odds = `\n📊 Combined Odds: ${formatOdds(resp.combined_odds)}`;
    const probability = resp.est_true_prob ?
        `🎯 Win Probability: ${(resp.est_true_prob * 100).toFixed(1)}%` : '';
    const ev = resp.ev ?
        `💰 Expected Value: ${resp.ev > 0 ? '+' : ''}$${resp.ev.toFixed(2)}` : '';
    const confidence = resp.confidence ?
        `⭐ Confidence: ${resp.confidence}/10` : '';

    const analysis = resp.rationale ?
        `\n📈 Analysis:\n${resp.rationale}` : '';

    const recommendation = resp.ev && resp.ev > 0 ?
        `\n✅ RECOMMENDED BET` :
        resp.ev && resp.ev < -0.5 ? `\n❌ AVOID - Negative EV` : `\n⚠️ NEUTRAL`;

    return [header, legs, odds, probability, ev, confidence, recommendation, analysis]
        .filter(Boolean).join("\n");
}

function formatAudit(resp) {
    if (!resp || !resp.items) return resp;

    const header = `📊 EQ12 Audit Report\n${"=".repeat(25)}`;
    const summary = `Total Bets: ${resp.total_bets || 0} | Win Rate: ${resp.win_rate || 0}%`;
    const profit = resp.total_profit ?
        `💰 Total P&L: ${resp.total_profit > 0 ? '+' : ''}$${resp.total_profit.toFixed(2)}` : '';

    const recent = resp.items.slice(0, 5).map(item =>
        `• ${item.date}: ${item.result} - $${item.amount} (${item.odds})`
    ).join("\n");

    return [header, summary, profit, "\nRecent Activity:", recent].filter(Boolean).join("\n");
}

function formatPrivacyStatus(resp) {
    const header = `🛡️ Privacy Protection Status\n${"=".repeat(30)}`;
    const blocked = `🚫 Trackers Blocked: ${resp.trackers_blocked || 0}`;
    const fingerprint = `🔒 Fingerprinting: ${resp.fingerprint_protection ? 'Protected' : 'Vulnerable'}`;
    const webrtc = `🌐 WebRTC Leaks: ${resp.webrtc_protected ? 'Blocked' : 'Exposed'}`;
    const dns = `🔍 DNS Leaks: ${resp.dns_protected ? 'Protected' : 'Vulnerable'}`;

    return [header, blocked, fingerprint, webrtc, dns].join("\n");
}

function formatDevToolsStatus(resp) {
    const header = `🔧 Developer Tools Status\n${"=".repeat(27)}`;
    const console = `📝 Debug Console: ${resp.console_active ? 'Active' : 'Inactive'}`;
    const performance = `⚡ Performance Monitor: ${resp.performance_active ? 'Running' : 'Stopped'}`;
    const network = `🌐 Network Monitor: ${resp.network_active ? 'Intercepting' : 'Passive'}`;

    return [header, console, performance, network].join("\n");
}

function formatVpnStatus(resp) {
    const header = `🔐 VPN Connection Status\n${"=".repeat(26)}`;
    const status = `📡 Status: ${resp.connected ? '✅ Connected' : '❌ Disconnected'}`;
    const location = resp.location ? `🌍 Location: ${resp.location}` : '';
    const ip = resp.public_ip ? `🆔 Public IP: ${resp.public_ip}` : '';
    const leak = resp.leak_detected ?
        `⚠️ LEAK DETECTED: ${resp.leak_type}` :
        `🔒 No Leaks Detected`;

    return [header, status, location, ip, leak].filter(Boolean).join("\n");
}

function formatOdds(odds) {
    if (!odds) return 'N/A';
    return typeof odds === 'number' ?
        (odds > 0 ? `+${odds}` : `${odds}`) :
        odds.toString();
}

// Initialize popup
async function initialize() {
    showLoading("🔄 Connecting to EQ12 backend...");

    // Test connection
    const pingResult = await req("PING");
    if (pingResult) {
        show("🎯 EQ12 Dashboard Ready!\nClick buttons above to get started.", 'info');
    }

    // Load any cached data
    try {
        const cached = await browser.storage.local.get(['lastParlay', 'lastAudit']);
        if (!pingResult && cached.lastParlay) {
            show("📱 Offline Mode - Showing cached data:\n" + formatTicket(cached.lastParlay));
        }
    } catch (err) {
        console.warn('Failed to load cached data:', err);
    }
}

// Start initialization
initialize();
