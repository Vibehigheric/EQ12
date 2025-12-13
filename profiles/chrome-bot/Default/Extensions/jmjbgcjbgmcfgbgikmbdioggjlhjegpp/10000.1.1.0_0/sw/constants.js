export const SETTINGS = {
  OBTURATION_SOUND: 'OBTURATION_SOUND',
  ALTALT: 'ALTALT',
  AUTO_UPLOAD: 'AUTO_UPLOAD',
  AUTO_SNAP: 'AUTO_SNAP',
  NOT_SAVED_WARNING: 'NOT_SAVED_WARNING',
  CLIPSLOADING: 'CLIPSLOADING',
  USERDATA: 'USERDATA',
  CLIPS: 'CLIPS',
  HOTKEY_TAB: 'HOTKEY_TAB',
  HOTKEY_PAGE: 'HOTKEY_PAGE',
  HOTKEY_AREA: 'HOTKEY_AREA',
};

export const isDev = false;
export const isTest = false;


let apihost = 'https://us-central1-screenclip-website-test.cloudfunctions.net/application';
let sitehost = 'https://app.screenclip.com';

// test api host = https://us-central1-screenclip-website-test.cloudfunctions.net/application
// test
if (isTest) {
  apihost = 'https://us-central1-screenclip-website.cloudfunctions.net/application';
  sitehost = 'https://screen-link-test.web.app';
}

if (isDev) { // is dev?
  apihost = 'https://us-central1-screenclip-website.cloudfunctions.net/application';
  sitehost = 'http://localhost:5005';
}

export const APIHOST = apihost;
export const SITEHOST = sitehost;

export const DEFAULT_AUTH_CHECKING_TIMEOUT = 2000;

export const POPUP = 'popup/dist/index.html';
export const POPUP_RESTRICTED = 'popup/dist/index.html?restricted';

export const currentTabQuery = { active: true, currentWindow: true };