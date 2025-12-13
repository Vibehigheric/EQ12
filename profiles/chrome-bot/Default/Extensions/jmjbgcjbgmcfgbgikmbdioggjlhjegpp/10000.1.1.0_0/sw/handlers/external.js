import { setState } from '../state.js';
import { broadcastUserdata } from '../auth.js';

// external handlers

const setCurrentUser = async (data, sendResponse) => {
  chrome.cookies.get({
    url: data.senderOrigin,
    name: "__session"
  }, async (cookie) => {
    console.log("auth:cookie", cookie)
    if (cookie) {
      console.log("Set current user", data)
      const session = cookie.value;
      // if logout
      if (Object.keys(data).length === 0) {
        session = '';
      }
      data.uid = data?.userId;

      setState({ session, user: data });
      await chrome.storage.local.set({'USERDATA': data});

      chrome.runtime.sendMessage({'action': 'BG__POPUP__USERDATA', data});
    } else {
      console.log("no cookies", cookie)
      setState({ session: '', user: {}});
      chrome.runtime.sendMessage({'action': 'BG__POPUP__USERDATA', data: {}});
    }
    sendResponse(true);
  });
  return;
};

const is_installed = async (data, sendResponse) => {
  let version = chrome.runtime.getManifest().version;
  const res = {
    msg: true,
    version: version
  };
  sendResponse(res)
}

const update_userdata = async (data, sendResponse) => {
  console.log("website update userdata", data.data)
  const user = (await chrome.storage.local.get('USERDATA')).USERDATA;
  if (typeof(user) === 'undefined') user = {};
  const userdata = {
    ...user,
    ...data,
    serverUser: {
      ...(user.serverUser || {}),
      ...data
    }
  }
  await chrome.storage.local.set({'USERDATA': userdata});
  // broadcast message that there were changes
  broadcastUserdata(userdata);
}

const run_editor = async (data, sendResponse, tabId) => {
  console.log("editor image data", data)
  chrome.tabs.sendMessage(tabId, {
    action: "BG__CONTENT__WEBSITE_RUN_EDITOR",
    tab: tabId,
    data: {
      imageDataUrl: data.imageDataUrl,
      imageWidth: data.imageWidth,
      imageHeight: data.imageHeight
    }
  });
}

const stop_editor = async (data, sendResponse, tabId) => {
  console.log("stop-editor")
  chrome.tabs.sendMessage(tabid, {
    action: "BG__CONTENT__WEBSITE_STOP_EDITOR",
    tab: tabid
  });
}

const save_editor = async (data, sendResponse, tabId) => {
  console.log("save-editor")
  chrome.tabs.sendMessage(tabid, {
    action: "BG__CONTENT__EMBED_SAVE_EDITOR",
    tab: tabid
  });
}

export const externalHandlers = {
  setCurrentUser,
  stop_editor,
  save_editor,
  run_editor,
  update_userdata,
  is_installed,
};