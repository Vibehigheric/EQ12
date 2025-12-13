import { DEFAULT_AUTH_CHECKING_TIMEOUT, SITEHOST } from './constants.js';

export const broadcastUserdata = (userdata) => {
  chrome.runtime.sendMessage({action:"BG__ALL__USERDATA", data: userdata});
  chrome.windows.getAll({
    populate: true
  }).then(windows => {
    let i = 0, w = windows.length, currentWindow;
    for (; i < w; i++) {
      currentWindow = windows[i];
      let j = 0, t = currentWindow.tabs.length, currentTab;
      for (; j < t; j++) {
        currentTab = currentWindow.tabs[j];
        if (!currentTab.url.match(/(chrome):\/\//gi)) {
          chrome.tabs.sendMessage(currentTab, { action: "BG__ALL__USERDATA", data: userdata });
        }
      }
    }
  });
};

function authRoutines(timeout = DEFAULT_AUTH_CHECKING_TIMEOUT) {
  // get cookies for domain from chrome
  chrome.cookies.get({
    url: SITEHOST, // Domain where the session cookie is set
    name: '__session' // The name of the session cookie
  }, async function(cookie) {

    // initial, empty userdata
    let userdata = {};
    // old value of stored session
    const oldSession = (await chrome.storage.local.get('SESSION')).SESSION;
    // if cookie value recieved
    if (cookie && cookie.value) {
      console.log('Auth: Session: Check');
      // get session cookie
      const session = cookie.value;
      if (oldSession !== session) {
        console.log('Auth: Session: Check, session changed from: ', oldSession, ' to:', session);
        await chrome.storage.local.set({'SESSION': session});
        // uid
        const uid = session.split('*')[1];
        await chrome.storage.local.set({'UID': uid});
        // userdata
        userdata = await fetch(SITEHOST + '/api/users/' + uid, {
          method: 'GET',
          headers: {
            Cookie: `__session=${session}`
          },
        }).then(data => data.json());
        userdata.uid = userdata.userId;
        userdata.userphoto = userdata.photoUrl;
        userdata.username = userdata.displayName;
        userdata.isPlus = userdata.accountType === 'plus';
        userdata.serverUser = JSON.parse(JSON.stringify(userdata));
        // save updated userdata
        await chrome.storage.local.set({'USERDATA': userdata});
        // broadcast message that there were changes
        broadcastUserdata(userdata);
      }
    } else {
      // if old session not empty, then make it empty and all userdata empty
      if (oldSession !== '') {
        await chrome.storage.local.set({'SESSION': ''});
        await chrome.storage.local.set({'UID': ''});
        await chrome.storage.local.set({'USERDATA': {}});
        console.log('Auth: Session: Check: cleared')
        chrome.runtime.sendMessage({
          action: 'BROADCAST_USERDATA',
          data: userdata,
        });
        // broadcast everywhere
        broadcastUserdata(userdata)
      } else {
        console.log('Auth: Session: Check: stay cleared')
      }
      // const isAuthorized = (await chrome.storage.local.set('UID')).UID !== '';
      // const isPlus = (await chrome.storage.local.set('USERDATA'))?.accountType === 'plus';
    }
    setTimeout(authRoutines, timeout); // Periodic checks
  });
}

// Function to periodically check session cookie every DEFAULT_AUTH_CHECKING_TIMEOUT seconds
export function startAuthLoop(timeout = DEFAULT_AUTH_CHECKING_TIMEOUT) {
  console.log("Auth: Loop: Started")
  authRoutines(timeout); // Initial check
}