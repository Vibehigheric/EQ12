class Storage {

  constructor () {
    this.handleStoreChanged = this.handleStoreChanged.bind(this);

    this.store = {}; // FLAT STORE
    /*
    <STORE STRUCTURE>
    OBTURATION_SOUND: BOOLEAN,
    ALTALT: BOOLEAN,
    AUTO_UPLOAD: BOOLEAN,
    AUTO_SNAP: BOOLEAN,
    NOT_SAVED_WARNING: BOOLEAN,
    CLIPSLOADING: BOOLEAN,
    USERDATA: OBJECT,
    CLIPS: ARRAY,
    TABID_AUTOSNAP: BOOLEAN,
    TABID_CAPTUREAREA: BOOLEAN,
    TABID_INJECTED: BOOLEAN,
    TABID_POPUP: BOOLEAN,
    TABID_CAPTUREVIDEO: BOOLEAN,
    TABID_CAPTUREVIDEOTAB: BOOLEAN
    HOTKEY_[ACTION]: BOOLEAN
    ...
    */
    this.events();
  }

  handleStoreChanged(changes) {
    this.store = {
      ...this.store,
      ...changes
    };
  };
  addStoreChangedListener(listener) {
    chrome.storage.onChanged.addListener(listener);
  };
  events () {
    this.addStoreChangedListener(this.handleStoreChanged);
  }

  getField (field) {
    return new Promise((resolve, reject) => {
      chrome.storage.local.get(field).then(data => {
        let ret = {}
        if (data[field]) ret = data[field];
        else ret = false;
        resolve(ret);
        return;
      });
    });
  }

  getFieldRaw (field) {
    return new Promise(resolve => {
      chrome.storage.local.get(field).then(data => {
        resolve(data[field]);
        return;
      });
    });
  }

  async isClipsLoading () {
    let is = await this.getField("CLIPSLOADING");
    return is;
  }

  startClipsLoading () {
    let set = {};
    set["CLIPSLOADING"] = true;
    return chrome.storage.local.set(set);
  }

  stopClipsLoading () {
    let set = {};
    set["CLIPSLOADING"] = false;
    return chrome.storage.local.set(set);
  }

  getFieldSet (set) {
    return new Promise((resolve, reject) => {
      chrome.storage.local.get(set).then(data => {
        let ret = {};
        set.forEach(item => {
          ret[item.split("_")[1].toLowerCase()] = data[item];
        });
        resolve(ret);
        return;
      });
    });
  }

  // clips
  getClips () {
    let field = "CLIPS";
    return new Promise((resolve, reject) => {
      chrome.storage.local.get(field).then(data => {
        if (!Array.isArray(data.CLIPS)) data.CLIPS = [];
        // if (data.CLIPS.length > 9) data.CLIPS = data.CLIPS.slice(0,9);
        resolve(data["CLIPS"]);
      })
    });
  }

  setClips (value) {
    let set = {};
    set["CLIPS"] = value;
    return chrome.storage.local.set(set);
  }

  async addClip (clip) {
    let clips = await this.getClips();
    let id = '_' + Math.random().toString(36).substr(2, 9);
    let newClip = {...clip, clipId: id}
    clips.unshift(newClip);
    // if (clips.length > 9) clips = clips.slice(0, 9);
    this.setClips(clips);
    return newClip
  }

  async renameClip (data) {
    let clips = await this.getClips();
    console.log("rename", clips, data)
    let newClips = clips.map(clip => data.clipId === clip.clipId ? { ...clip, title: data.title, sourceTitle: data.title } : clip)
    this.setClips(newClips);
  }

  async updateClip(clipId, data) {
    let clips = await this.getClips();
    console.log("update", clips, data)
    let newClips = clips.map(clip => clip.clipId === clipId ? { ...clip, ...data } : clip)
    this.setClips(newClips);
  }

  async removeClip (clipId) {
    let clips = await this.getClips();
    let newClips = clips.filter(clip => clipId !== clip.clipId)
    this.setClips(newClips);
  }

  // IMAGES

  // TOOLS SETTINGS
  setToolsSettings(value) {
    let set = {};
    set["TOOLS_SETTINGS"] = value;
    return chrome.storage.local.set(set);
  }
  getToolsSettings() {
    return this.getField("TOOLS_SETTINGS");
  };

  // USERDATA
  getUserData() {
    return this.getField("USERDATA");
  };
  setUserData(value) {
    let set = {};
    set["USERDATA"] = value;
    return chrome.storage.local.set(set);
  };

  async getObturationSound () {
    let play = await this.getFieldRaw("OBTURATION_SOUND");
    if (typeof(play) === 'undefined') {
      this.setObturationSound(true);
      return true;
    } else {
      return play;
    }
  }

  setObturationSound(value) {
    let set = {};
    set["OBTURATION_SOUND"] = value;
    return chrome.storage.local.set(set);
  };

  async getAltaltStart () {
    let play = await this.getFieldRaw("ALTALT");
    if (typeof(play) === 'undefined') {
      this.setAltaltStart(false);
      return true;
    } else {
      return play;
    }
  }

  setAltaltStart(value) {
    let set = {}
    set["ALTALT"] = value;
    return chrome.storage.local.set(set);
  };

  async getAutoSnap () {
    let play = await this.getFieldRaw("AUTO_SNAP");
    if (typeof(play) === 'undefined') {
      this.setAutoSnap(false);
      return false;
    } else {
      return play;
    }
  }

  setAutoSnap(value) {
    let set = {};
    set["AUTO_SNAP"] = value;
    return chrome.storage.local.set(set);
  };

  async getAutoUpload () {
    let play = await this.getFieldRaw("AUTO_UPLOAD");
    if (typeof(play) === 'undefined') {
      this.setAutoUpload(true);
      return true;
    } else {
      return play;
    }
  }

  setAutoUpload(value) {
    let set = {};
    set["AUTO_UPLOAD"] = value;
    return chrome.storage.local.set(set);
  };

  // hotkeys

  async getHotkeyArea () {
    let play = await this.getFieldRaw("HOTKEY_AREA");
    if (typeof(play) === 'undefined') {
      this.setHotkeyArea(false);
      return false;
    } else {
      return play;
    }
  }

  setHotkeyArea(value) {
    let set = {};
    set["HOTKEY_AREA"] = value;
    return chrome.storage.local.set(set);
  };

  async getHotkeyTab () {
    let play = await this.getFieldRaw("HOTKEY_TAB");
    if (typeof(play) === 'undefined') {
      this.setHotkeyTab(false);
      return false;
    } else {
      return play;
    }
  }

  setHotkeyTab(value) {
    let set = {};
    set["HOTKEY_TAB"] = value;
    return chrome.storage.local.set(set);
  };

  async getHotkeyPage () {
    let play = await this.getFieldRaw("HOTKEY_PAGE");
    if (typeof(play) === 'undefined') {
      this.setHotkeyPage(false);
      return false;
    } else {
      return play;
    }
  }

  setHotkeyPage(value) {
    let set = {};
    set["HOTKEY_PAGE"] = value;
    return chrome.storage.local.set(set);
  };

  // end hotkeys

  async getShowSaveWarning() {
    let play = await this.getFieldRaw("NOT_SAVED_WARNING");
    if (typeof (play) === 'undefined') {
      this.setShowSaveWarning(true);
      return true;
    } else {
      return play;
    }
  }

  setShowSaveWarning(value) {
    let set = {};
    set["NOT_SAVED_WARNING"] = value;
    return chrome.storage.local.set(set);
  };

  // AUTOSNAP
  async getTabAutosnap(tab) {
    return await this.getField([tab,"_AUTOSNAP"].join(""));
  };
  setTabAutosnap(tab, value, cb) {
    let set = {};
    set[tab + "_AUTOSNAP"] = value;
    chrome.storage.local.set(set).then(cb);
  }

  // POPUP
  async getTabPopup(tab) {
    return await this.getField([tab, "_POPUP"].join(""));
  }
  setTabPopup(tab, value, cb) {
    let set = {};
    set[tab + "_POPUP"] = value;
    chrome.storage.local.set(set).then(cb);
  }

  // CAPTURE AREA
  async getTabCaptureArea (tab) {
    return await this.getField([tab, "_CAPTUREAREA"].join(""));
  }
  setTabCaptureArea (tab, value, cb) {
    let set = {};
    set[tab+"_CAPTUREAREA"] = value;
    chrome.storage.local.set(set).then(cb);
  }

  // CAPTURE VIDEO TAB
  async getTabCaptureVideoTab(tab) {
    return await this.getField([tab, "_CAPTUREVIDEOTAB"].join(""));
  }
  setTabCaptureVideoTab(tab, value, cb) {
    let set = {};
    set[tab + "_CAPTUREVIDEOTAB"] = value;
    chrome.storage.local.set(set).then(cb);
  }

  // CAPTURE VIDEO
  setTabCaptureVideo(tab, value, cb) {
    let set = {};
    set[tab + "_CAPTUREVIDEO"] = value;
    chrome.storage.local.set(set).then(cb);
  }
  async getTabCaptureVideo(tab) {
    return await this.getField([tab, "_CAPTUREVIDEO"].join(""));
  }

  // INJECTED
  async getTabInjected(tab, cb) {
    return await this.getField([tab, "_INJECTED"].join(""));
  }
  setTabInjected(tab, value, cb) {
    let set = {};
    set[tab + "_INJECTED"] = value;
    chrome.storage.local.set(set).then(cb);
  }

  // WHOLE TAB SET/GET

  setTab(tabid, tab, cb) {
    let set = {};
    set[tabid + "_CAPTUREVIDEO"] = tab['capturevideo'];
    set[tabid + "_CAPTUREVIDEOTAB"] = tab['capturevideotab'];
    set[tabid + "_CAPTUREAREA"] = tab['capturearea'];
    set[tabid + "_AUTOSNAP"] = tab['autosnap'];
    set[tabid + "_INJECTED"] = tab['injected'];
    set[tabid + "_POPUP"] = tab['popup']; // sdf
    // cb = cb || ()=>{};
    chrome.storage.local.set(set);//.then(cb);
  }

  async getTab (tabid, cb) {
    return await this.getFieldSet([
      tabid + "_POPUP",
      tabid + "_CAPTUREVIDEO",
      tabid + "_CAPTUREVIDEOTAB",
      tabid + "_CAPTUREAREA",
      tabid + "_INJECTED",
      tabid + "_AUTOSNAP"
    ]);
  }
}

export const storage = new Storage();
