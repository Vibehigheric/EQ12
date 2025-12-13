import { getState, setState } from '../state.js';
import { fetchClips, fetchRenameClip, removeClip, } from '../requests.js';
import { currentTabQuery, POPUP } from '../constants.js'
import { handlersFromContent, postClip } from './internal-content.js';
import { clearInjectTimeout } from '../utils.js';

// import { storage } from '../storage.js';

// handlers
export const handlers = {
  CONTENT__BG__PING: async (data, sendMessage, tabid) => {
    clearInjectTimeout();
    chrome.action.setPopup({ popup: POPUP });
    sendMessage(true);
  },
  POST_CLIP: async (data, sendResponse) => {
    await postClip(data);
    chrome.runtime.sendMessage({ action: 'REFRESH_POPUP_CLIPS', })
    sendResponse(true);
  },
  POPUP__BG__REMOVE_LOCAL_CLIP: async (clipId, sendResponse) => {
    const id = clipId;
    const localClips = await chrome.storage.local.get('CLIPS').then(({ CLIPS }) => CLIPS || []);
    const newLocalClips = localClips.filter(({clipId}) => clipId !== id);
    await chrome.storage.local.set({'CLIPS': newLocalClips});
    chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
    sendResponse(true);
  },
  POPUP__BG__REMOVE_CLIP: async (data, sendResponse) => {
    const id = data.clipId;
    if (!data.downloadUrl.includes("data:")) {
      await removeClip(data.clipId);
      setState({
        popupClips: getState().popupClips.filter(({clipId}) => clipId !== id),
      });
      chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
    } else {
      const localClips = await chrome.storage.local.get('CLIPS').then(({ CLIPS }) => CLIPS || []);
      const newLocalClips = localClips.filter(({clipId}) => clipId !== id);
      await chrome.storage.local.set({'CLIPS': newLocalClips});
      setState({
        popupClips: getState().popupClips.filter(({clipId}) => clipId !== id),
      });
      chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
    }
    sendResponse(true)
  },
  REFRESH_POPUP_CLIPS: async (data, sendResponse) => {
    const connectedClips = await fetchClips();
    const localClips = await chrome.storage.local.get('CLIPS').then(({ CLIPS }) => CLIPS || []);
    const popupClips = [...connectedClips, ...localClips];
    popupClips.sort((a, b) => a.creationTime._seconds < b.creationTime._seconds ? 1 : -1);
    console.log("setPopupClips", popupClips)
    setState({ popupClips });
    await chrome.storage.local.set({CLIPSLOADING: false});
    // chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
    sendResponse(true);
  },
  GET_POPUP_CLIPS: async (data, sendResponse) => {
    const { popupClips } = getState();
    console.log("getPopupClips", popupClips)
    sendResponse(popupClips || []);
  },
  // capturing
  POPUP__BG__RENAME_CLIP: async (data, sendResponse) => {
    let userdata = (await chrome.storage.local.get('USERDATA')).USERDATA;
    if (!data.downloadUrl.includes("data:") && userdata.uid) {
      await fetchRenameClip(data);
    } else {
      const clips = (await chrome.storage.local.get('CLIPS')).CLIPS || [];
      let newClips = clips.map(
        clip => data.clipId === clip.clipId
          ? { ...clip, title: data.title, sourceTitle: data.title }
          : clip
      );
      await chrome.storage.local.set({'CLIPS': newClips});
      
      const popupClips = getState().popupClips.map(clip => {
        if (clip.clipId === id) {
          clip.title = data.title
          clip.sourceTitle = data.title
        }
        return clip;
      });
      setState({ popupClips, });
      chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
    }
    sendResponse(true)
  },
  /// AUTO UPLOAD
  POPUP__BG__AUTO_SNAP_ON: async (data, sendResponse) => {
    chrome.storage.local.set({AUTO_SNAP: true});
    sendResponse(true)
  },
  POPUP__BG__AUTO_SNAP_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({AUTO_SNAP: false});
    sendResponse(true)
  },
  /// AUTO UPLOAD
  POPUP__BG__AUTO_UPLOAD_ON: async (data, sendResponse) => {
    chrome.storage.local.set({AUTO_UPLOAD: true});
    sendResponse(true)
  },
  POPUP__BG__AUTO_UPLOAD_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({AUTO_UPLOAD: false});
    sendResponse(true)
  },
  /// OBTURATION SOUND
  POPUP__BG__OBTURATION_SOUND_ON: async (data, sendResponse) => {
    chrome.storage.local.set({OBTURATION_SOUND: true});
    sendResponse(true)
  },
  POPUP__BG__OBTURATION_SOUND_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({OBTURATION_SOUND: false});
    sendResponse(true)
  },
  /// OBTURATION SOUND
  POPUP__BG__ALTALT_ON: async (data, sendResponse) => {
    chrome.storage.local.set({ALTALT: true});
    sendResponse(true)
  },
  POPUP__BG__ALTALT_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({ALTALT: false});
    sendResponse(true)
  },
  /// HOTKEYS
  POPUP__BG__HOTKEY_AREA_ON: async (data, sendResponse) => {
    chrome.storage.local.set({HOTKEY_AREA: true})
    sendResponse(true)
  },
  POPUP__BG__HOTKEY_AREA_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({HOTKEY_AREA: false})
    sendResponse(true)
  },
  POPUP__BG__HOTKEY_TAB_ON: async (data, sendResponse) => {
    chrome.storage.local.set({HOTKEY_TAB: true})
    sendResponse(true)
  },
  POPUP__BG__HOTKEY_TAB_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({HOTKEY_TAB: false})
    sendResponse(true)
  },
  POPUP__BG__HOTKEY_PAGE_ON: async (data, sendResponse) => {
    chrome.storage.local.set({HOTKEY_PAGE: true})
    sendResponse(true)
  },
  POPUP__BG__HOTKEY_PAGE_OFF: async (data, sendResponse) => {
    chrome.storage.local.set({HOTKEY_PAGE: false})
    sendResponse(true)
  },
  //
  CONTENT__BG__PLAY_OBTURATION_SOUND_IF_NEEDED: async (data, sendResponse) => {
    const play = (await chrome.storage.local.get('OBTURATION_SOUND')).OBTURATION_SOUND;

    if (typeof(play) === 'undefined' || Boolean(play)) {
      chrome.storage.local.set({ OBTURATION_SOUND: true })
      chrome.tabs.query(currentTabQuery, ([{id}]) =>
        chrome.tabs.sendMessage(id, {
          action: "BG__CONTENT__PLAY_OBTURATION_SOUND",
        })
      );
    }
  },
  POPUP__BG__ANONYMOUS_IMG: (req, data) => {
    let url = data.url;
    let img = data.img;
    let dpxr = data.dpxr;
    chrome.tabs.create({ 'url': url }).then(tab => {
      chrome.tabs.executeScript({
        target: { tabId: tab.id },
        code: `;(()=>{
          let s = document.createElement('script');
          let img = "${img}";
          sessionStorage.setItem('anonClip', img);
          sessionStorage.setItem('anonClipDpxr', ${dpxr});
          document.appendChild(s);
        })();`,
        runAt: 'document_start'
      });
    });
  },
  // getters
  getStorage: async (data, sendResponse) => {
    sendResponse(storage.getField(data.field));
  },
  getClips: async (data, sendResponse) => {
    const clips = await fetchClips();
    sendResponse(clips);
  },
  getCurrentUser: async (data, sendResponse) => {
    sendResponse();
  },
  ...handlersFromContent
};