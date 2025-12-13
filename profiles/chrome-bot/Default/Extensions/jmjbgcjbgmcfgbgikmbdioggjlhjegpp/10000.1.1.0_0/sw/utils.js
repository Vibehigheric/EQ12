import { Timestamp } from './libs/firestore.js';
import { currentTabQuery } from './constants.js';

let injectCountdown;
export const clearInjectTimeout = () => clearTimeout(injectCountdown);
export const setInjectTimeout = (fn) => setTimeout(fn, 500);

export const extendClipData = (data) => {
  delete data.blob;
  let pageUrl = data.pageUrl
  let title = (data.sourceTitle || data.title);
  let downloadUrl = (data.clipUrl || data.downloadUrl);
  let markers = data.markers;

  const ts = Timestamp.now()
  // post clip
  return {
    ...data,
    creationTime: {
      _seconds: ts.seconds,
      _nanoseconds: ts.nanoseconds
    },
    privacy: 'public',
    sourceTitle: title,
    title: title,
    clipUrl: downloadUrl,
    downloadUrl: downloadUrl,
    markers: markers,
    pageUrl: pageUrl
  };
}

export const showNotification = (data = {}) => {
  chrome.notifications.create({
    message: "Unexpected error",
    type: "basic",
    title: "Error",
    iconUrl: "../badges/normal/Icon128.png",
    ...data,
  });
}

export const isRestricted = async () => {
  try {
    const tab = await chrome.tabs.query(currentTabQuery);
    const [{ id }] = tab;
    return (
      await chrome.action.getPopup({ tabId: id })
    ).includes("?restricted")
  } catch(e) {
    return true;
  }
}

export const showRestrictedNotification = () => {
  chrome.notifications.create({
    message: "Sorry, this page does not allow screenshots to be made",
    type: "basic",
    title: "Error",
    iconUrl: "../badges/inactive/Icon128.png"
  });
}

export const addClipIntoStorage = async (clip) => {
  const clips = (await chrome.storage.local.get('CLIPS')).CLIPS || [];
  const id = '_' + Math.random().toString(36).substr(2, 9);
  const newClip = {...clip, clipId: id}
  clips.unshift(newClip);
  // if (clips.length > 9) clips = clips.slice(0, 9);
  await chrome.storage.local.set({'CLIPS': clips});
  return newClip;
}

export function copyTextToClipboard(text) {
  navigator.clipboard.writeText(text).then(
    () => {
      console.log("Text copied to clipboard");
    },
    (err) => {
      console.error("Failed to copy text: ", err);
    }
  );
}

export function copyImageToClipboard(imgUrl) {
  function dataURLtoBlob(dataurl) {
    let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
      bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) u8arr[n] = bstr.charCodeAt(n);
    return new Blob([u8arr], { type: mime });
  };

  const blob = dataURLtoBlob(imgUrl);
  try {
    navigator.clipboard.write([
      new ClipboardItem({
        'image/png': blob
      })
    ]);
  } catch (error) {
    console.log("scerror");
    console.error(error);
  }
}

export function slugify(string) {
  const a = 'àáâäæãåāăąçćčđďèéêëēėęěğǵḧîïíīįìłḿñńǹňôöòóœøōõőṕŕřßśšşșťțûüùúūǘůűųẃẍÿýžźż·/_,:;'
  const b = 'aaaaaaaaaacccddeeeeeeeegghiiiiiilmnnnnoooooooooprrsssssttuuuuuuuuuwxyyzzz------'
  const p = new RegExp(a.split('').join('|'), 'g')

  return rus2lat(string.toString()).toLowerCase()
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(p, c => b.charAt(a.indexOf(c))) // Replace special characters
    .replace(/&/g, '-and-') // Replace & with 'and'
    .replace(/[^\w\-]+/g, '') // Remove all non-word characters
    .replace(/\-\-+/g, '-') // Replace multiple - with single -
    .replace(/^-+/, '') // Trim - from start of text
    .replace(/-+$/, '') // Trim - from end of text
}

export function rus2lat(str) {
  const ru = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'е': 'e', 'ё': 'e', 'ж': 'j', 'з': 'z', 'и': 'i',
    'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh',
    'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'u', 'я': 'ya'
  }, n_str = [];
  str = str.replace(/[ъь]+/g, '').replace(/й/g, 'i');
  for (var i = 0; i < str.length; ++i) {
    n_str.push(
      ru[str[i]]
      || ru[str[i].toLowerCase()] == undefined && str[i]
      || ru[str[i].toLowerCase()].toUpperCase()
    );
  }
  return n_str.join('');
}

export const dataURLtoBlob = (dataurl) => {
  let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
    bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
  while (n--) u8arr[n] = bstr.charCodeAt(n);
  return new Blob([u8arr], { type: mime });
};