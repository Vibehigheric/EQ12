const out = document.getElementById("out");
const btn5 = document.getElementById("btn-5");
const btn10 = document.getElementById("btn-10");
const btnAudit = document.getElementById("btn-audit");
const btnHealth = document.getElementById("btn-health");
const openOptions = document.getElementById("open-options");
const openDashboard = document.getElementById("open-dashboard");
const apiStatus = document.getElementById("api-status");

function show(obj, isError = false) {
    const text = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
    out.textContent = text;
    out.className = isError ? "out error" : "out";
}

async function req(type, payload = {}) {
    try {
        const res = await browser.runtime.sendMessage({ type, ...payload });
        if (!res) {
            show("No response from background service", true);
            return null;
        }
        if (!res.ok) {
            show(res.error || "Unknown error", true);
            return null;
        }
        return res.data;
    } catch (error) {
        show(`Request failed: ${error.message}`, true);
        return null;
    }
}

async function updateApiStatus() {
    try {
        const data = await req("PING");
        if (data) {
            apiStatus.style.color = "#10b981"; // green
            apiStatus.title = "API Connected";
        } else {
            apiStatus.style.color = "#ef4444"; // red
            apiStatus.title = "API Disconnected";
        }
    } catch {
        apiStatus.style.color = "#ef4444";
        apiStatus.title = "API Error";
    }
}

btn5.addEventListener("click", async () => {
    show("🔄 Fetching 5-leg parlay...");
    const data = await req("GET_PARLAY", { size: 5 });
    if (data) {
        show(formatTicket(data));
    }
});

btn10.addEventListener("click", async () => {
    show("🔄 Fetching 10-leg parlay...");
    const data = await req("GET_PARLAY", { size: 10 });
    if (data) {
        show(formatTicket(data));
    }
});

btnAudit.addEventListener("click", async () => {
    show("🔄 Fetching audit report...");
    const data = await req("GET_AUDIT", { last: 5 });
    if (data) {
        show(formatAudit(data));
    }
});

btnHealth.addEventListener("click", async () => {
    show("🔄 Checking system health...");
    const data = await req("GET_HEALTH");
    if (data) {
        show(formatHealth(data));
    }
});

openOptions.addEventListener("click", () => {
    browser.runtime.openOptionsPage();
});

openDashboard.addEventListener("click", async () => {
    const settings = await req("GET_SETTINGS");
    if (settings) {
        const dashboardUrl = `${settings.apiBase}/dashboard`;
        browser.tabs.create({ url: dashboardUrl });
    }
});

function formatTicket(resp) {
    // Format EQ12 parlay response for plain text display
    if (!resp || !resp.legs) return JSON.stringify(resp, null, 2);

    const evPercent = (resp.ev * 100).toFixed(1);
    const evSymbol = resp.ev > 0 ? '+' : '';

    const header = `🎯 ${resp.name}\n${'='.repeat(40)}`;

    const legs = resp.legs.map((leg, i) => {
        const oddsText = leg.price > 0 ? `+${leg.price}` : `${leg.price}`;
        const confPercent = (leg.confidence * 100).toFixed(0);
        return `${i + 1}. ${leg.selection} (${oddsText})\n   📍 ${leg.game}\n   📖 ${leg.book} • 🎯 ${confPercent}% confidence`;
    }).join('\n\n');

    const summary = `\n${'='.repeat(40)}\n💰 Combined Odds: ${resp.combined_odds.toFixed(1)}x\n� Expected Value: ${evSymbol}${evPercent}%\n🎲 Est. Win Probability: ${(resp.est_true_prob * 100).toFixed(1)}%\n⚡ Risk Level: ${resp.risk_level.toUpperCase()}\n\n💡 ${resp.rationale}`;

    return `${header}\n\n${legs}${summary}`;
}

function formatAudit(resp) {
    if (!resp || !resp.recent_bets) {
        return `📊 Audit Report\n${'='.repeat(30)}\nNo recent betting data available.`;
    }

    const header = `📊 Audit Report (Last ${resp.recent_bets.length} bets)\n${'='.repeat(30)}`;
    const summary = `💵 Total Wagered: $${resp.total_wagered || 0}\n💰 Total Won: $${resp.total_won || 0}\n📈 Win Rate: ${resp.win_rate || 0}%\n📊 ROI: ${resp.roi || 0}%`;

    return `${header}\n\n${summary}`;
}

function formatHealth(resp) {
    const header = `❤️ System Health\n${'='.repeat(30)}`;
    const status = `🟢 Status: ${resp.status || 'Unknown'}\n🔌 Port: ${resp.port || 'N/A'}\n⏰ Uptime: ${resp.uptime || 'N/A'}\n💾 Database: ${resp.database_status || 'Unknown'}`;

    return `${header}\n\n${status}`;
}

// Initialize
updateApiStatus();
setInterval(updateApiStatus, 30000); // Update status every 30 seconds
