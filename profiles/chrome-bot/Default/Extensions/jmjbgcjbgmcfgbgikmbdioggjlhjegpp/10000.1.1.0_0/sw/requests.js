import { SITEHOST, APIHOST } from './constants.js'

// ADD CLIP
export async function fetchAddClip(data) {
  const session = (await chrome.storage.local.get('SESSION')).SESSION;
  const url = `${SITEHOST}/api/clips`;
  let options = {
    method: 'POST',
    headers: {
      Cookie: `__session=${session}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    
  };
  console.log("Channel: Saving Clip with options:", options.data);

  return fetch(url, options).then(resp => {
    if (resp.ok) return resp.json();
    else {
      throw resp;
    }
  })
}

// GET CLIPS REQUEST
export async function fetchClips(count = 20) {
  const session = (await chrome.storage.local.get('SESSION')).SESSION;
  if (!session) {
    console.log("Error: fetchClips: unauthorized")
    return [];
  }
  const query = `?sortField=creationTime&sortDirection=descending&amount=${count}`;
  const url = `${SITEHOST}/api/clips${query}`;
  const options = {
    method: 'GET',
    headers: {
      Cookie: `__session=${session}`
    },
  };

  let clips = [];
  try {
    clips = await fetch(url, options).then(res => {
      return res.json();
    });
    console.log("FETCH_CLIPS, BG", clips)
  } catch(e) {
    console.log("Error: GetClips: ", err);
  }
  return clips.length ? clips : [];
};

const emptyRenameResponse = {
  clipId: "",
  url: ""
};

// RENAME CLIP REQUEST
export async function fetchRenameClip(data) {
  const session = (await chrome.storage.local.get('SESSION')).SESSION;
  return new Promise(async (resolve, reject) => {
    if (!session) {
      console.error("Error: FetchRenameclips: unauthorized")
      resolve(emptyRenameResponse);
      return;
    }
    const user = (await chrome.storage.local.get('USERDATA')).USERDATA || {};
    if (!user.hasOwnProperty("uid") || !navigator.onLine) {
      resolve(emptyRenameResponse);
      return;
    }
    const options = {
      method: 'PATCH',
      body: JSON.stringify({
        title: data.title,
      }),
      headers: {
        Cookie: `__session=${session}`,
        'Content-Type': 'application/json',
      }
    };
    console.log("Channel: Updating Clip with options:", options.body);
    try {
      const res = await fetch(`${SITEHOST}/api/clips/${data.clipId}`, options)
      const result = res.json();
      console.log("rename resp", result)
      resolve(result);
    } catch(e) {
      console.error("Error: RenameClip: ", e);
      resolve();
    }
  });
}

// REMOVE CLIP
export async function removeClip(clipId) {
  console.log("Channel: Removing Clip:", clipId);
  const session = (await chrome.storage.local.get('SESSION')).SESSION;
   // base64
  let options = {
    method: 'delete',
    headers: {
      Cookie: `__session=${session}`,
    }
  };
  try {
    await fetch(`${SITEHOST}/api/clips/${clipId}`, options);
    return true;
  } catch(e) {}
  return false;
}