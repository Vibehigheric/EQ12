const apiBaseEl = document.getElementById("apiBase");
const apiKeyEl = document.getElementById("apiKey");
const statusEl = document.getElementById("status");
const saveBtn = document.getElementById("save");
const testBtn = document.getElementById("test");
const backToPopup = document.getElementById("back-to-popup");

async function load() {
    try {
        const res = await browser.runtime.sendMessage({ type: "GET_SETTINGS" });
        if (res?.ok) {
            apiBaseEl.value = res.settings.apiBase || "";
            apiKeyEl.value = res.settings.apiKey || "";
            statusEl.textContent = "✅ Settings loaded successfully";
        } else {
            statusEl.textContent = "❌ Failed to load settings";
        }
    } catch (error) {
        statusEl.textContent = `❌ Error loading settings: ${error.message}`;
    }
}

async function testConnection() {
    statusEl.textContent = "🔄 Testing connection...";

    try {
        // Test with current form values (don't save yet)
        const testApiBase = apiBaseEl.value.trim();
        const testApiKey = apiKeyEl.value.trim();

        if (!testApiBase) {
            statusEl.textContent = "❌ Please enter an API base URL";
            return;
        }

        // Test ping endpoint
        const pingUrl = new URL("/api/ping", testApiBase);
        const headers = {
            "Content-Type": "application/json"
        };

        if (testApiKey) {
            headers["Authorization"] = `Bearer ${testApiKey}`;
        }

        const response = await fetch(pingUrl.toString(), {
            headers,
            mode: 'cors'
        });

        if (response.ok) {
            const data = await response.json();
            statusEl.textContent = `✅ Connection successful!\nPing: ${data.message || 'OK'}\nReady to save settings.`;
            statusEl.className = "out success";
        } else {
            statusEl.textContent = `❌ Connection failed: ${response.status} ${response.statusText}`;
            statusEl.className = "out error";
        }

    } catch (error) {
        statusEl.textContent = `❌ Connection error: ${error.message}`;
        statusEl.className = "out error";
    }
}

async function saveSettings() {
    const apiBase = apiBaseEl.value.trim();
    const apiKey = apiKeyEl.value.trim();

    if (!apiBase) {
        statusEl.textContent = "❌ API Base URL is required";
        statusEl.className = "out error";
        return;
    }

    try {
        const res = await browser.runtime.sendMessage({
            type: "SET_SETTINGS",
            apiBase,
            apiKey
        });

        if (res.ok) {
            statusEl.textContent = "✅ Settings saved successfully!";
            statusEl.className = "out success";

            // Show success notification
            browser.notifications.create({
                type: 'basic',
                iconUrl: '../icons/icon-48.png',
                title: 'EQ12 Settings Saved',
                message: 'API configuration updated successfully!'
            });

        } else {
            statusEl.textContent = "❌ Failed to save settings";
            statusEl.className = "out error";
        }
    } catch (error) {
        statusEl.textContent = `❌ Save error: ${error.message}`;
        statusEl.className = "out error";
    }
}

// Event listeners
saveBtn.addEventListener("click", saveSettings);
testBtn.addEventListener("click", testConnection);

backToPopup.addEventListener("click", (e) => {
    e.preventDefault();
    window.close(); // Close options tab
});

// Auto-test connection when URL changes
apiBaseEl.addEventListener("input", () => {
    statusEl.textContent = "💡 Click 'Test Connection' to verify the new URL";
    statusEl.className = "out";
});

// Load settings on page load
load();
