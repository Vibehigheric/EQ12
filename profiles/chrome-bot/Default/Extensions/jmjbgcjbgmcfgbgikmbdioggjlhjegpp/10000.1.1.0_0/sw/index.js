import { handlers, externalHandlers, systemHandlers, } from './handlers/index.js';
import { currentTabQuery } from './constants.js';
import { isRestricted } from './utils.js';
import { startAuthLoop } from './auth.js';

// on installed event
chrome.runtime.onInstalled.addListener((details) => {
  console.log("ID:", chrome.runtime.id)
  chrome.storage.local.set({ "CLIPSLOADING": false });
  if (details.reason === chrome.runtime.OnInstalledReason.INSTALL) {
    systemHandlers.onInstalled(details);
  } else if (details.reason === chrome.runtime.OnInstalledReason.UPDATE) {
    systemHandlers.onUpdated(details);
  }
});

// tabs
chrome.tabs.onUpdated.addListener(systemHandlers.tabOnUpdated);
chrome.tabs.onActivated.addListener(systemHandlers.tabOnActivated);
chrome.tabs.onCreated.addListener(systemHandlers.tabOnCreated);

// message listeners

// internal
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const handler = handlers[message.action];
  const data = message.data;
  if (handler) {
    console.log("Message:", message.action);
    console.log("Message sender:", sender)
    handler(data, sendResponse, sender?.tab?.id);
  } else {
    console.log("Message: Missed Handler", message.action);
  }
  return true;
});

// external
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  const handler = externalHandlers[message.action];
  console.log("external message", message, sender.origin)
  if (handler) {
    console.log("ExternalMessage:", message.action);
    const data = {...message.data, senderOrigin: sender.origin};
    handler(data, sendResponse, sender?.tab?.id);
  }
  return true;
});

// commands
chrome.commands.onCommand.addListener(handleCommand);

async function handleCommand(command) {
  console.log("command:", command);
  if (await isRestricted()) {
    showRestrictedNotification();
    return;
  }
  if (command === 'capture-area-command' && (await chrome.storage.local.get('HOTKEY_AREA')).HOTKEY_AREA) {
    chrome.tabs.query(currentTabQuery, ([{id}]) => chrome.tabs.sendMessage(id, { action: "BG__CONTENT__CAPTURE_START" }));
  } else if (command === 'capture-tab-command' && (await chrome.storage.local.get('HOTKEY_TAB')).HOTKEY_TAB) {
    handlers['POPUP__BG__CAPTURE_TAB']();
  } else if (command === 'capture-page-command' && (await chrome.storage.local.get('HOTKEY_PAGE')).HOTKEY_PAGE) {
    chrome.tabs.query(currentTabQuery, ([{id}]) => chrome.tabs.sendMessage(id, { action: "BG__CONTENT__CAPTURE_FULLPAGE_START" }));
  }
}

startAuthLoop();

console.log("screenclip sw started")