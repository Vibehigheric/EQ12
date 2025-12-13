import { POPUP } from '../constants.js';
import { setInjectTimeout, clearInjectTimeout, } from '../utils.js';

const pingTab = (tabid) => {
  console.log("ping:", tabid)
  chrome.tabs.sendMessage(tabid, {
    action: "BG__CONTENT__PING",
    tab: tabid
  });
}

const injectOrRestricted = (tabid, ok) => {
  if (!ok) {
    ok = () => {};
  }
  chrome.action.setPopup({ popup: POPUP });
  console.log(tabid)
  clearInjectTimeout();

  pingTab(tabid);

  setInjectTimeout(() => {
    injectContentsIntoTab(tabid, ok, error => injectionError(error) );
  });
}

function shareIdToWindow(id) {
  localStorage.setItem("screenclipExtensionId", id);
}

const injectContentsIntoTab = (tabid, canInject, cantInject) => {
  const everythingFine = () => {
    chrome.action.setPopup({ popup: POPUP });
    chrome.scripting.executeScript({
      target: { tabId: tabid },
      func: shareIdToWindow,
      args: [chrome.runtime.id]
    });
    canInject();
  };

  const attemptToInject = (msg) => {
    msg = msg || {};
    console.log("Is Injected message", msg)
    if (msg.status !== 'yes') {
      let scripts = [
        "insides/permanent/browser-polyfill.min.js",
        "insides/content/content.js"
      ];
      let styles = [
        "insides/permanent/outside.css"
      ];
      let sp = [];

      scripts.forEach(script => {
        sp.push(
          chrome.scripting.executeScript({
            target : {tabId: tabid, allFrames : true},
            files : [ script ],
          })//.catch(err => console.log(script, err))
        )
      });
  
      styles.forEach(style => {
        // console.log("Style:", style);
        sp.push(
          chrome.scripting.insertCSS({
            target: { tabId: tabid },
            files: [style],
          })
        );
      });
  
      Promise.all(sp).then(everythingFine).catch(error => {
        cantInject(error)
      });
    } else {
      everythingFine();
    }
  };

  chrome.tabs.sendMessage(tabid, {text: "is_screenclip_there?"}).then(
    attemptToInject
  ).catch((e) => {
    console.log("Error with manual injection", e);
    attemptToInject()
  });
};

const injectionError = (err) => {
  console.error("inject error:", err);
  chrome.action.setPopup({ popup: POPUP + "?restricted" });
}

const restoreTabStateCreate = (tabId) => {
  return async () => {
    const userdata = (await chrome.storage.local.get('USERDATA')).USERDATA;
    const toolsSettings = (await chrome.storage.local.get('TOOLS_SETTINGS')).TOOLS_SETTINGS;
    console.log("userdata sent to current tab:", tabId, userdata);
    chrome.tabs.sendMessage(tabId, { action: "BG__ALL__USERDATA", tabid: tabId, data: userdata})
    chrome.tabs.sendMessage(tabId, { action: "BG__CONTENT__TOOLS_SETTINGS", tabid: tabId, data: toolsSettings })
  }
};

// system handlers
export const systemHandlers = {
  onInstalled: () => {
    const url = 'https://screenclip.com/browser-extension-installed';
    chrome.tabs.create({ url, });
  },
  onUpdated: (changeInfo, tabid) => {
    console.log("Extension onUpdated handler was called")
  },
  tabOnUpdated: (tabId) => {
    injectOrRestricted(tabId, restoreTabStateCreate(tabId));
  },
  tabOnActivated: (tab) => {
    injectOrRestricted(tab.tabId, restoreTabStateCreate(tab.tabId));
  },
  tabOnCreated: (tab) => {
    injectOrRestricted(tab.tabId, restoreTabStateCreate(tab.tabId));
  }
};