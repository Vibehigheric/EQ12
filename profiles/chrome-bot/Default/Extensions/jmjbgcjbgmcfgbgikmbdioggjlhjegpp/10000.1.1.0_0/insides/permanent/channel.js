// // response: clip
// {
//        "privacy": "private",
//        "tags": [],
//        "size": "220613",
//        "mimeType": "image/png",
//        "title": "1550814731962_2019-2-22 8.52.10 Can I use... Support tables for HTML5, CSS3, etc [ScreenClip]",
//        "clipId": "ePHuT9sMQvtER3xBzs7T",
//        "previewUrl": "https://storage.googleapis.com/screenclip-website-test.appspot.com/clips%2Fe19bT72sCWbPjPEFflu960Ecjr33%2FePHuT9sMQvtER3xBzs7T.png?GoogleAccessId=firebase-adminsdk-6fla1%40screenclip-website-test.iam.gserviceaccount.com&Expires=4706488333&Signature=FJTciW9d0CZSY1cFnWFntZJHCer7ZNgxZaUKcC33HfulmCn6nvHL7OC0DATl7IFAFpwbFUhpx11VrDnKbEUfbBQ1pM%2BoAJAbYh6uCBLbiNb04ndK7v5wvVymoiSr1BGfppgSShJFsrfswKPqs2ecn9Jjfx5Ni09GmDeaW9%2FNuzSzO2JbyNVYsmYjcxgu7TyFxMpZ2u2Y8XNHQIaVGgwPHIvTQrQXG%2BIyJ1VWYRAoFRoxKHQDtMT1IpkCnbu58KXO10Jg%2BQDt8dTF7s%2FErFJsF4wYEhS6G805xjVhgiLWqfTNRA8Xm4Ia0%2FzQ8Tl3dY0yF3jws6pK2zeUxbZ3Vd8lMw%3D%3D",
//        "downloadUrl": "https://storage.googleapis.com/screenclip-website-test.appspot.com/clips%2Fe19bT72sCWbPjPEFflu960Ecjr33%2FePHuT9sMQvtER3xBzs7T.png?GoogleAccessId=firebase-adminsdk-6fla1%40screenclip-website-test.iam.gserviceaccount.com&Expires=4706488333&Signature=FJTciW9d0CZSY1cFnWFntZJHCer7ZNgxZaUKcC33HfulmCn6nvHL7OC0DATl7IFAFpwbFUhpx11VrDnKbEUfbBQ1pM%2BoAJAbYh6uCBLbiNb04ndK7v5wvVymoiSr1BGfppgSShJFsrfswKPqs2ecn9Jjfx5Ni09GmDeaW9%2FNuzSzO2JbyNVYsmYjcxgu7TyFxMpZ2u2Y8XNHQIaVGgwPHIvTQrQXG%2BIyJ1VWYRAoFRoxKHQDtMT1IpkCnbu58KXO10Jg%2BQDt8dTF7s%2FErFJsF4wYEhS6G805xjVhgiLWqfTNRA8Xm4Ia0%2FzQ8Tl3dY0yF3jws6pK2zeUxbZ3Vd8lMw%3D%3D",
//        "sourceUrl": "chrome-extension://pnppojjkpjiajainaiemefddjnlcddlc/background.html",
//        "expiryTime": {
//            "_seconds": 1553406731,
//            "_nanoseconds": 962000000
//        },
//        "parentFolderId": "root",
//        "storageLocation": "firebaseStorage",
//        "description": "New clip.",
//        "ownedBy": "e19bT72sCWbPjPEFflu960Ecjr33",
//        "sourceTitle": "2019-2-22 8.52.10 Can I use... Support tables for HTML5, CSS3, etc [ScreenClip]",
//        "views": 0,
//        "creationTime": {
//            "_seconds": 1550814731,
//            "_nanoseconds": 962000000
//        }
// }

const IS_DEV = "production" === 'development'
const IS_TEST = "production" === 'testing'

class Channel {

  constructor(bg) {
    this.bg = bg;
    this.initFrame = this.initFrame.bind(this);
    if (this.bg.IS_DEV) {
      this.apiHost = 'http://localhost:5005';
      this.apiUrl = this.apiHost + '/api';
    } else if (this.bg.IS_TEST){
      this.apiHost = 'https://screen-link-test.web.app';
      this.apiUrl = this.apiHost + '/api';
    } else {
      this.apiHost = 'https://app.screenclip.com';
      this.apiUrl = this.apiHost + '/api';
    }
    this.communicationPageUrl = this.bg.siteHost + "/extension-communication.html";
    this.frameOrigin = "*";
    this.frame = null;
    this.initAxios();

    this.backOnline = this.backOnline.bind(this);
    window.addEventListener("online", this.backOnline);
  }

  initAxios() {
    axios.interceptors.response.use((response) => {
      return response;
    }, error => {
        let err = "";
        if (error.response) {
          err = "Code: " + error.response.status;
          console.log('Error Response:', error.request);
        } else if (error.request) {
          err = "The request was made but no response was received";
          console.log('Error Request:', error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error', error.message);
          err = error.message;
        }

        // browser.notifications.create({
        //   message: err,
        //   type: "basic",
        //   title: "Error",
        //   iconUrl: "./badges/normal/normal128.png"
        // });
        return Promise.reject(error);
      }
    );
  }

  initFrame () {
    this.frame = document.createElement("iframe");
    this.frame.src = this.communicationPageUrl;
    document.body.append(this.frame);
    this.frame.addEventListener("load", () => this.frameLoaded(this.frame));
  }

  frameLoaded (frame) {
    console.log("Channel: frame loaded");

    window.addEventListener("message", async (e) => {
      await this.frameMessaging(e)
    });
    frame.contentWindow.postMessage({ "event": "start-observe" }, this.frameOrigin);
  }

  async backOnline() {
    // let localClips = await this.bg.syncClips();
    let clips = this.getLatestClips(10);
    // console.log(localClips[0].clipId, clips[0].clipId, clips[0].url);
    // clips.forEach( (clip, i) => {
    //   if (clip.downloadUrl=='' && localClips.length-1>=i) clips[i].downloadUrl = localClips[i].downloadUrl;
    // })
    await this.bg.mixClips(clips);
    this.bg.broadcastClips();
  }

  async frameMessaging (e) {
    let userdata = e.data.details || {};

    console.log("Channel: frame event:", e.data.event, e.data);
    
    if (e.data.event === 'clips-reload') {
      // clips
      // await this.bg.syncClips();
      let clips = await this.getLatestClips(10);
      await this.bg.mixClips(clips);
      this.bg.broadcastClips();

    } else if (e.data.event === 'auth-sign-in') {
      // userdata
      let ud = {};
      ud.uid = userdata.uid;
      ud.username = userdata.displayName;
      ud.accessToken = userdata.accessToken;
      userdata = ud;

      const token = ud.accessToken
      let options = {
        url: this.apiUrl + '/login',
        headers: { 'Authorization': `Bearer ${token}` }
      };
      let resp = await axios(options)
      ud.serverUser = resp.data.user
      ud.username = ud.username == null ? ud.serverUser.displayName : ud.username;
      ud.userphoto = (typeof (ud.serverUser.photoUrl) === 'undefined') ? false : ud.serverUser.photoUrl;

      this.bg.storage.setUserData(userdata);

      // clips
      // await this.bg.syncClips();
      let clips = await this.getLatestClips(10);

      await this.bg.mixClips(clips);

      // broadcasts
      this.bg.broadcastClips();
      console.log("sign in", userdata);
      this.bg.broadcastUserData(userdata);
    } else if (e.data.event === 'auth-sign-out') {
      console.log("sign out");
      // this.bg.storage.setClips({});
      this.bg.mixClips([])
      this.bg.storage.setUserData({});
      this.bg.broadcastUserData({});

    } else if (e.data.event === 'auth-token-refreshed') {
      console.log("CHANNEL: message - auth-token-refreshed");
      let userdata = await this.bg.storage.getUserData();
      userdata.accessToken = e.data.details.accessToken;
      await this.bg.storage.setUserData(userdata);
      this.bg.broadcastUserData(userdata);
    } else if (e.data.event === 'clips-updated') {
      let clips = await this.getLatestClips(10);
      await this.bg.mixClips(clips);

      // broadcasts
      this.bg.broadcastClips();
    }
  }
  
  removeClip(clipId) {
    return new Promise(async (resolve, reject) => {
      // user
      let user = await this.bg.storage.getUserData();
      if (!user.hasOwnProperty("uid") || !navigator.onLine) {
        resolve({
          clipId: "",
          url: ""
        });
        return;
      }
      // base64
      let options = {
        method: 'delete',
        url: `${this.apiUrl}/clips/${clipId}`,
      };
      console.log("Channel: Removing Clip:", clipId);

      axios(options).then(res => {
        console.log("Channel: api resp: removed clip", clipId);
        resolve(res.data);
      }).catch(err => {
        console.error("Channel: error removing clip: ", clipId);
        reject(err);
      });
    });
  }

  updateClip(clipId, data) {
    return new Promise(async (resolve, reject) => {
      let options = {
        method: 'patch',
        url: `${this.apiUrl}/clips/${clipId}`,
        data,
      };
      console.log("Channel: Updating Clip with options:", options.data);

      axios(options).then(res => {
        console.log("Channel: api resp: updating clip", res);
        resolve(res.data);
      }).catch(err => {
        console.error("Channel: error updating clip: ", err);
        reject(err);
      });
    });
  }

  renameClip(data) {
    return new Promise(async (resolve, reject) => {
      // user
      let user = await this.bg.storage.getUserData();
      if (!user.hasOwnProperty("uid") || !navigator.onLine) {
        resolve({
          clipId: "",
          url: ""
        });
        return;
      }
      // base64
      let options = {
        method: 'patch',
        url: `${this.apiUrl}/clips/${data.clipId}`,
        data: {
          title: data.title,
        }
      };
      console.log("Channel: Updating Clip with options:", options.data);

      axios(options).then(res => {
        console.log("Channel: api resp: updating clip", res);
        resolve(res.data);
      }).catch(err => {
        console.error("Channel: error updating clip: ", err);
        reject(err);
      });
    });
  }

  postClip (data) {
    return new Promise(async (resolve, reject) => {
      // user
      let user = await this.bg.storage.getUserData();
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
        sourceUrl: window.location.href,
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
        let options = {
          method: 'post',
          url: `${this.apiUrl}/clips`,
          // headers: {
          //   Authorization: `Bearer ${user.accessToken}`
          // },
          data: postData,
        };
        console.log("Channel: Saving Clip with options:", options.data);
        // options.data[data.mimeType === 'video/webm' ? 'video' : 'image'] = base64;

        axios(options).then(res => {
          console.log("Channel: api resp: image sent", res);
          resolve(res.data);
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

  getImageData(url) {
    return new Promise(async (resolve, reject) => {
      let options = {
        method: "get",
        url: url,
        headers: {
          // Authorization: `Bearer ${user.accessToken}`
        }
      };
      axios(options).then(res => {
        console.log("Channel: api resp (get Image): image sent", res);
        resolve(res);
      }).catch(err => {
        console.error("Channel: error Get Image Data: ", err);
        reject(err);
      });
    });
  }

  arrayBufferToBase64 (buffer) {
    var binary = '';
    var bytes = new Uint8Array(buffer);
    var len = bytes.byteLength;
    for (var i = 0; i < len; i++) binary += String.fromCharCode(bytes[i]);
    return btoa(binary);
  }

  getLatestClips (amount = 10) {
    return new Promise( async (resolve, reject) => {
      const query = `?sortField=creationTime&sortDirection=descending&amount=${amount}`;
      const options = {
        method: "get",
        url: `${this.apiUrl}/clips${query}`,
      };
      axios(options).then(res => {
        console.log("Channel: api resp (get latest clips): image sent", res);
        resolve(res.data);
      }).catch(err => {
        console.error("Channel: error Get Latest Image: ", err);
        reject(err);
      });
    });
  }
}
export default Channel;