(function () {
  const listenerName = '__sp_mainWorld_listener';

  if (typeof window[listenerName] !== 'undefined') {
    return;
  }

  // shared
  const __sendResponse = (id, response) => {
    window.postMessage(
      {
        type: 'sp-main-world-response',
        responseId: id,
        response,
      },
      window.location.origin
    );
  };

  const __run = (content) => {
    const s = document.createElement('script');
    const cs = document.createTextNode(content);
    s.setAttribute('class', 'iv-script-class');
    s.appendChild(cs);
    (document.body || document.head).appendChild(s);
  };

  // actions
  const getWindowVariableSafely = (variableName) => {
    if (!variableName) {
      return undefined;
    }

    const i = `${Date.now()}${Math.floor(Math.random() * 1000000)}`;

    __run(`
  var elCos = document.createElement('div');
  elCos.id = 'iv-token-div-${i}';
  elCos.style.cssText = 'display: none!important';
  var textCos = JSON.stringify(window.${variableName});
  var newContentCos = document.createTextNode(textCos);
  elCos.appendChild(newContentCos)
  document.body.appendChild(elCos);
  `);

    const el = document.querySelector(`#iv-token-div-${i}`);
    const result = el?.textContent || null;

    if (result === 'undefined') {
      return undefined;
    }

    return JSON.parse(result);
  };

  const setWindowVariableSafely = (variableName, newValue) => {
    if (!variableName) {
      return;
    }

    __run(`window['${variableName}'] = ${JSON.stringify(newValue)}`);
  };

  // listener
  window[listenerName] = (ev) => {
    const eventData = ev.data;

    if (
      !eventData ||
      eventData.type !== 'sp-main-world-request' ||
      ev.origin !== window.location.origin
    ) {
      return;
    }

    const payload = eventData.data;

    let ret;
    switch (payload?.action) {
      case 'getWindowVariableSafely':
        ret = getWindowVariableSafely(payload.variable);
        break;
      case 'setWindowVariableSafely':
        setWindowVariableSafely(payload.variable, payload.value);
        break;
    }

    __sendResponse(ev.data.responseId, ret);
  };

  window.addEventListener('message', window[listenerName]);
})();
