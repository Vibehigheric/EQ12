import {
  slugify,
  extendClipData, showNotification, addClipIntoStorage, copyTextToClipboard,
  copyImageToClipboard,
} from '../utils.js';
import { currentTabQuery, SITEHOST } from './../constants.js';
import { fetchAddClip, fetchClips } from '../requests.js';
import { setState } from '../state.js';

const createNewClip = (data) => {
  return new Promise(async (resolve, reject) => {
    // user
    let user = (await chrome.storage.local.get('USERDATA')).USERDATA;
    if (!user.hasOwnProperty("uid") || !navigator.onLine) {
      resolve({
        clipId: "",
        url: ""
      });
      return;
    }
    // base64
    const base64 = data.clipUrl.split(',')[1];
    const base64background = (data.background || data.clipUrl).split(',')[1];
    let sourceTitle = data.sourceTitle || "clip";
    const postData = {
      annotations: JSON.stringify(data.annotations),
      background: base64background,
      image: base64,
      sourceUrl: data.sourceUrl,
      sourceTitle: sourceTitle,
      mimeType: (data.mimeType || 'image/png'),
      markers: data.markers,
      dpxr: data.dpxr,
      pageUrl: data.pageUrl,
      parentFolderId: 'root'
    }
    const postDataLength = (
      encodeURI(JSON.stringify(postData)).split(/%..|./).length - 1
    ) / 1024 / 1024
    if (postDataLength <= 10) {
      fetchAddClip(postData).then(res => {
        console.log("Channel: api resp: image sent", res);
        resolve(res);
      }).catch(err => {
        console.error("Channel: error Add Clip: ", err);
        reject(err);
      });
    } else {
      const message = 'Channel: error Add Clip: clip is to big:' + postDataLength + 'MB'
      console.error(message)
      reject(message)
    }
  });
}

export const postClip = async (newClip, tabid) => {
  const clip = await createNewClip(newClip).catch(async (e) => {
    chrome.storage.local.set({'CLIPSLOADING': false});
    const errorStatus = e.status;
    const errorRespJson = await e.json();
    if (errorRespJson?.message.indexOf('Storage limit reached') !== -1 || errorStatus === 422) {
      chrome.scripting.executeScript({
        target: { tabId: tabid },
        func: copyImageToClipboard,
        args: [newClip.clipUrl]
      });
      showNotification({
        message: "Your cloud storage is full. Image was copied to clipboard. Please consider upgrading your account.",
      });
    } else if (errorStatus === 500 && errorRespJson?.data === 'invalid_grant') {
      showNotification({
        message: "Seems like you manually disconnect ScreenClip from your Google Drive account.",
      });
    } else {
      showNotification({
        message: "Failed to upload. The page is huge, try to screenshot it with Entire tab - one by one",
      });
    }
    chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
    return;
  });
  console.log("JUST POSTED CLIP", clip);
  if (clip.clipId === '') {
    clip = {
      ...clip,
      ...newClip
    };
    clip.downloadUrl = clip.downloadUrl || clip.clipUrl
  };
  clip.title = clip.sourceTitle;
  clip.shortUrl = clip.dynamicLink && clip.dynamicLink.shortLink;
  clip.markers = clip.markers;

  chrome.storage.local.set({'CLIPSLOADING': false});
  return clip;
}

// handlers

const CONTENT__BG__ADDCLIP = async (data, sendResponse, tabid) => {
  console.log("Add Clip Started:", data);

  chrome.storage.local.set({'CLIPSLOADING': true});
  let notificationMessage = "Link copied.";

  let clip = extendClipData(data);
  let clips = [];
  const user = (await chrome.storage.local.get('USERDATA')).USERDATA || {};

  const rawAutouploadValue = (await chrome.storage.local.get('AUTO_UPLOAD')).AUTO_UPLOAD;
  if (rawAutouploadValue === undefined) {
    await chrome.storage.local.set({'AUTO_UPLOAD': true});
  }
  const autoUploadOption = rawAutouploadValue === undefined ? true : Boolean(rawAutouploadValue);
  const isUser = typeof (user.uid) !== 'undefined';
  
  console.log("posting clip:", clip.clipUrl);
  
  try {
    if (isUser && navigator.onLine) {
      if (data.upload || autoUploadOption) {
        const postedClip = await postClip(clip, tabid);
        clip.clipId = postedClip.clipId
        clip.url = postedClip.url
        clip.downloadUrl = postedClip.downloadUrl
        chrome.storage.local.set({CLIPSLOADING: true});
        notificationMessage += typeof(postedClip.clipsInfo) !== 'undefined'
          ? ` You have ${postedClip.clipsInfo} slots left.`
          : '';
      } else {
        clip = await addClipIntoStorage(clip);
      }

    } else {
      clip = await addClipIntoStorage(clip);
    }
    const connectedClips = await fetchClips();
    const localClips = await chrome.storage.local.get('CLIPS').then(({ CLIPS }) => CLIPS || []);
    const popupClips = [...connectedClips, ...localClips];
    popupClips.sort((a, b) => a.creationTime._seconds < b.creationTime._seconds ? 1 : -1);
    setState({ popupClips });
  } catch(e) {
    console.log(e)
    showNotification({
      message: "Failed to upload. The page is huge, try to screenshot it with Entire tab - one by one"
    });
    sendResponse(true)
    return;
  } finally {
    chrome.storage.local.set({CLIPSLOADING: false});
    chrome.runtime.sendMessage({ action: 'BG__POPUP__CLIPS', })
  }

  // send message for share dialog and others
  let m = {}
  m.action = 'BG__CONTENT__CLIPADDED';
  m.data = {};
  m.data.url = SITEHOST + "/" + clip.url + "/" + slugify(clip.title);
  m.data.shortUrl = clip.shortUrl;
  m.data.title = clip.title;
  chrome.tabs.sendMessage(tabid, m);

  if (isUser && navigator.onLine  && (
    data.upload || autoUploadOption
  )) {
    chrome.runtime.sendMessage({
      action: 'BG__POPUP__COPYTEXT',
      data: m.data.url
    });
    try {
      chrome.scripting.executeScript({
        target: { tabId: tabid },
        func: copyTextToClipboard,
        args: [m.data.url]
      });
    } catch(e) {}

    showNotification({
      message: notificationMessage,
      title: 'ScreenClip',
    });
  } else {
    // const ext = data.mimeType.split("/")[1];
    // const filename = [slugify(data.sourceTitle), ext].join('.');
    // chrome.scripting.executeScript({
    //   target: { tabId: tabid },
    //   func: showSaveAs,
    //   args: [data.clipUrl, filename],
    // });
    chrome.scripting.executeScript({
      target: { tabId: tabid },
      func: copyImageToClipboard,
      args: [data.clipUrl]
    });
    showNotification({
      message: "Image was copied to clipboard",
      title: 'ScreenClip',
    });
  }
  sendResponse(true);
};

const showSaveAs = async (clipUrl, filename) => {
  let arr = clipUrl.split(','), mime = arr[0].match(/:(.*?);/)[1],
    bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
  while (n--) u8arr[n] = bstr.charCodeAt(n);
  const blob = new Blob([u8arr], { type: mime });
  const handle = await showSaveFilePicker({
    suggestedName: filename,
  });
  const writable = await handle.createWritable();
  await writable.write(blob);
  writable.close();
}

const CONTENT__BG__CAPTURE_SHOT = async (data, sendResponse, tabid) => {
  const imageWithAnnotations = await chrome.tabs.captureVisibleTab(null, {
    format: "png"
  });
  
  let obj = {
    action: (data.action ? data.action : "BG__CONTENT__CAPTURE_SHOT"),
    tab: tabid,
    download: data.download,
    markers: data.markers,
    image: imageWithAnnotations,
    upload: data.upload,
  };
  if (data.clip) obj.clip = data.clip;
  if (data.annotations) obj.annotations = data.annotations;
  if (data.background) obj.background = data.background;

  chrome.tabs.sendMessage(tabid, obj);
  sendResponse(true)
};

const CONTENT__BG__CAPTURE_SAVESHOT = async (data, sendResponse, tabid) => {
  const remessage = {
    action: "BG__CONTENT__CAPTURE_SAVESHOT",
    download: data.download,
    clip: data.clip,
    markers: data.markers,
    background: data.background,
    annotations: data.annotations,
  };
  CONTENT__BG__CAPTURE_SHOT(remessage, ()=>{}, tabid);
  sendResponse(true)
};

const CONTENT__BG__CAPTURE_STARTSHOT = async (data, sendResponse, tabid) => {
  const imageWithAnnotations = await chrome.tabs.captureVisibleTab(null, {
    format: "png"
  });
  let obj = {
    action: "BG__CONTENT__CAPTURE_STARTSHOT",
    image: imageWithAnnotations,
    download: data.download,
  };
  chrome.tabs.sendMessage(tabid, obj);
  sendResponse(true)
};

const sleep = async(n) => {
  return new Promise(function (resolve) {
    setTimeout(resolve, n);
  })
};

const CONTENT__BG__CAPTURE_FULLPAGE_PART = async (data, sendResponse, tabid) => {
  await sleep(500)
  return chrome.tabs.query(currentTabQuery, ([{id: tabid}]) => {
    CONTENT__BG__CAPTURE_SHOT({ "action": "BG__CONTENT__CAPTURE_FULLPAGE_PART"}, ()=>{}, tabid);
    sendResponse(true);
  });
}

const POPUP__BG__CAPTURE_TAB = async (data, sendResponse, tabid) => {
  const remessage = {
    action: "BG__CONTENT__CAPTURE_TAB",
  };
  return chrome.tabs.query(currentTabQuery, ([{id: tabid}]) => {
    CONTENT__BG__CAPTURE_SHOT(remessage, ()=>{}, tabid);
    sendResponse(true);
  });
}

const CONTENT__BG__SHOW_SAVE_WARNING_IF_NEEDED = async (data, sendResponse, tabid) => {
  let show = (await chrome.storage.local.get('NOT_SAVED_WARNING')).NOT_SAVED_WARNING ?? true;
  if (show) {
    chrome.tabs.sendMessage(tabid, {
      action: "BG__CONTENT__SHOW_SAVE_WARNING",
      tab: tabid
    });
  } else {
    chrome.tabs.sendMessage(tabid, {
      action: "BG__CONTENT__EXIT_WITHOUT_DIALOG",
      tab: tabid
    });
  }
  sendResponse(true);
}

export const handlersFromContent = {
  POPUP__BG__CAPTURE_TAB,
  CONTENT__BG__CAPTURE_FULLPAGE_PART,
  CONTENT__BG__CAPTURE_SAVESHOT,
  CONTENT__BG__CAPTURE_STARTSHOT,
  CONTENT__BG__ADDCLIP,
  CONTENT__BG__SHOW_SAVE_WARNING_IF_NEEDED,
}