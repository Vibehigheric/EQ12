importScripts("polyfill/browser-polyfill.min.js");

async function checkNewParlays() {
  try {
    let response = await fetch("http://localhost:5000/parlays/latest.json");
    if (!response.ok) return;
    let slip = await response.json();
    browser.notifications.create({
      "type": "basic",
      "iconUrl": "icons/icon48.png",
      "title": "New EV+ Parlay",
      "message": `Best ${slip.sport.toUpperCase()} parlay | EV ${slip.ev}`
    });
    await browser.storage.local.set({ latestParlay: slip });
  } catch (e) {
    console.error("Error fetching parlays", e);
  }
}
setInterval(checkNewParlays, 60000);
