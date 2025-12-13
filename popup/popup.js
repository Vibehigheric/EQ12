document.addEventListener("DOMContentLoaded", async () => {
  let { latestParlay } = await browser.storage.local.get("latestParlay");
  let div = document.getElementById("parlay");
  if (!latestParlay) {
    div.textContent = "No parlay available.";
    return;
  }
  div.textContent = JSON.stringify(latestParlay, null, 2);
  document.getElementById("apply").onclick = () => {
    browser.scripting.executeScript({
      target: { tabId: browser.tabs.TAB_ID_CURRENT },
      files: ["content.js"]
    });
  };
});
