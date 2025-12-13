document.addEventListener("DOMContentLoaded", async () => {
  const { backendWsUrl, backendHttpUrl, bridgeToken } = await browser.storage.local.get(["backendWsUrl","backendHttpUrl","bridgeToken"]);
  document.getElementById("wsUrl").value = backendWsUrl || "ws://localhost:8765/ws";
  document.getElementById("httpUrl").value = backendHttpUrl || "http://localhost:8000/parlays/latest.json";
  document.getElementById("token").value = bridgeToken || "";
  document.getElementById("save").onclick = async () => {
    await browser.storage.local.set({
      backendWsUrl: document.getElementById("wsUrl").value,
      backendHttpUrl: document.getElementById("httpUrl").value,
      bridgeToken: document.getElementById("token").value
    });
    alert("Saved!");
  };
});