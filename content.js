(async () => {
  let { latestParlay } = await browser.storage.local.get("latestParlay");
  if (!latestParlay) return;
  for (let leg of latestParlay.legs) {
    let selector = `button[data-outcome-label="${leg.label}"]`;
    let el = document.querySelector(selector);
    if (el) { el.click(); }
  }
  let stakeInput = document.querySelector("input[name='stake']");
  if (stakeInput) {
    stakeInput.value = latestParlay.stake;
    stakeInput.dispatchEvent(new Event("input", { bubbles: true }));
  }
})();