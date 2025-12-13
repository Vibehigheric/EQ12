let onlyOnceLogStock = !0;
const scanner = function() {
  function X(E, y) {
    const B = {};
    if (null == document.body) {
      B.status = 599;
    } else {
      if (document.body.textContent.match("you're not a robot")) {
        B.status = 403;
      } else {
        for (var R = document.evaluate("//comment()", document, null, XPathResult.ANY_TYPE, null), Q = R.iterateNext(), H = ""; Q;) {
          H += Q, Q = R.iterateNext();
        }
        if (H.match(/automated access|api-services-support@/)) {
          B.status = 403;
        } else {
          if (H.match(/ref=cs_503_link/)) {
            B.status = 503;
          } else {
            if (E.scrapeFilters && 0 < E.scrapeFilters.length) {
              R = {};
              Q = null;
              let F = "", f = null;
              const G = {};
              H = {};
              let Y = !1;
              const U = function(b, d, g) {
                var e = [];
                if (!b.selectors || 0 == b.selectors.length) {
                  if (!b.regExp) {
                    return F = "invalid selector, sel/regexp", !1;
                  }
                  e = document.getElementsByTagName("html")[0].innerHTML.match(new RegExp(b.regExp, "i"));
                  if (!e || e.length < b.reGroup) {
                    g = "regexp fail: html - " + b.name + g;
                    if (!1 === b.optional) {
                      return F = g, !1;
                    }
                    f += " // " + g;
                    return !0;
                  }
                  return e[b.reGroup];
                }
                let c = [];
                b.selectors.find(l => {
                  l = d.querySelectorAll(l);
                  return 0 < l.length ? (c = l, !0) : !1;
                });
                if (0 === c.length) {
                  if (!0 === b.optional) {
                    return !0;
                  }
                  F = "selector no match: " + b.name + g;
                  return !1;
                }
                if (b.parentSelector && (c = [c[0].parentNode.querySelector(b.parentSelector)], null == c[0])) {
                  if (!0 === b.optional) {
                    return !0;
                  }
                  F = "parent selector no match: " + b.name + g;
                  return !1;
                }
                if ("undefined" != typeof b.multiple && null != b.multiple && (!0 === b.multiple && 1 > c.length || !1 === b.multiple && 1 < c.length)) {
                  if (!Y) {
                    return Y = !0, U(b, d, g);
                  }
                  g = "selector multiple mismatch: " + b.name + g + " found: " + c.length;
                  if (!1 === b.optional) {
                    b = "";
                    for (var h in c) {
                      !c.hasOwnProperty(h) || 1000 < b.length || (b += " - " + h + ": " + c[h].outerHTML + " " + c[h].getAttribute("class") + " " + c[h].getAttribute("id"));
                    }
                    F = g + b + " el: " + d.getAttribute("class") + " " + d.getAttribute("id");
                    return !1;
                  }
                  f += " // " + g;
                  return !0;
                }
                if (b.isListSelector) {
                  return G[b.name] = c, !0;
                }
                if (!b.attribute) {
                  return F = "selector attribute undefined?: " + b.name + g, !1;
                }
                for (let l in c) {
                  if (c.hasOwnProperty(l)) {
                    var k = c[l];
                    if (!k) {
                      break;
                    }
                    if (b.childNode) {
                      b.childNode = Number(b.childNode);
                      h = k.childNodes;
                      if (h.length < b.childNode) {
                        g = "childNodes fail: " + h.length + " - " + b.name + g;
                        if (!1 === b.optional) {
                          return F = g, !1;
                        }
                        f += " // " + g;
                        return !0;
                      }
                      k = h[b.childNode];
                    }
                    h = null;
                    h = "text" == b.attribute ? k.textContent : "html" == b.attribute ? k.innerHTML : k.getAttribute(b.attribute);
                    if (!h || 0 == h.length || 0 == h.replace(/(\r\n|\n|\r)/gm, "").replace(/^\s+|\s+$/g, "").length) {
                      g = "selector attribute null: " + b.name + g;
                      if (!1 === b.optional) {
                        return F = g, !1;
                      }
                      f += " // " + g;
                      return !0;
                    }
                    if (b.regExp) {
                      k = h.match(new RegExp(b.regExp, "i"));
                      if (!k || k.length < b.reGroup) {
                        g = "regexp fail: " + h + " - " + b.name + g;
                        if (!1 === b.optional) {
                          return F = g, !1;
                        }
                        f += " // " + g;
                        return !0;
                      }
                      e.push(k[b.reGroup]);
                    } else {
                      e.push(h);
                    }
                    if (!b.multiple) {
                      break;
                    }
                  }
                }
                b.multiple || (e = e[0]);
                return e;
              };
              let aa = document, a = !1;
              for (let b in E.scrapeFilters) {
                if (a) {
                  break;
                }
                let d = E.scrapeFilters[b], g = d.pageVersionTest;
                var q = [], t = !1;
                for (const e of g.selectors) {
                  if (q = document.querySelectorAll(e), 0 < q.length) {
                    t = !0;
                    break;
                  }
                }
                if (t) {
                  if ("undefined" != typeof g.multiple && null != g.multiple) {
                    if (!0 === g.multiple && 2 > q.length) {
                      continue;
                    }
                    if (!1 === g.multiple && 1 < q.length) {
                      continue;
                    }
                  }
                  if (g.attribute && (t = null, t = "text" == g.attribute ? "" : q[0].getAttribute(g.attribute), null == t)) {
                    continue;
                  }
                  Q = b;
                  for (let e in d) {
                    if (a) {
                      break;
                    }
                    q = d[e];
                    if (q.name != g.name) {
                      if (q.parentList) {
                        t = [];
                        if ("undefined" != typeof G[q.parentList]) {
                          t = G[q.parentList];
                        } else {
                          if (!0 === U(d[q.parentList], aa, b)) {
                            t = G[q.parentList];
                          } else {
                            break;
                          }
                        }
                        H[q.parentList] || (H[q.parentList] = []);
                        for (let c in t) {
                          if (a) {
                            break;
                          }
                          if (!t.hasOwnProperty(c)) {
                            continue;
                          }
                          let h = U(q, t[c], b);
                          if (!1 === h) {
                            a = !0;
                            break;
                          }
                          if (!0 !== h) {
                            if (H[q.parentList][c] || (H[q.parentList][c] = {}), q.multiple) {
                              for (let k in h) {
                                h.hasOwnProperty(k) && !q.keepBR && (h[k] = h[k].replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                              }
                              h = h.join("\u271c\u271c");
                              H[q.parentList][c][q.name] = h;
                            } else {
                              H[q.parentList][c][q.name] = q.keepBR ? h : h.replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " ");
                            }
                          }
                        }
                      } else {
                        t = U(q, aa, b);
                        if (!1 === t) {
                          a = !0;
                          break;
                        }
                        if (!0 !== t) {
                          if (q.multiple) {
                            for (let c in t) {
                              t.hasOwnProperty(c) && !q.keepBR && (t[c] = t[c].replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                            }
                            t = t.join();
                          } else {
                            q.keepBR || (t = t.replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                          }
                          R[q.name] = t;
                        }
                      }
                    }
                  }
                  a = !0;
                }
              }
              if (null == Q) {
                F += " // no pageVersion matched", B.status = 308, B.payload = [f, F, E.dbg1 ? document.getElementsByTagName("html")[0].innerHTML : ""];
              } else {
                if ("" === F) {
                  B.payload = [f];
                  B.scrapedData = R;
                  for (let b in H) {
                    B[b] = H[b];
                  }
                } else {
                  B.status = 305, B.payload = [f, F, E.dbg2 ? document.getElementsByTagName("html")[0].innerHTML : ""];
                }
              }
            } else {
              B.status = 306;
            }
          }
        }
      }
    }
    y(B);
  }
  let Z = !0;
  window.self === window.top && (Z = !1);
  window.sandboxHasRun && (Z = !1);
  Z && (window.sandboxHasRun = !0, window.addEventListener("message", function(E) {
    if (E.source == window.parent && E.data && (E.origin == "chrome-extension://" + chrome.runtime.id || E.origin.startsWith("moz-extension://") || E.origin.startsWith("safari-extension://"))) {
      var y = E.data.value;
      "data" == E.data.key && y.url && y.url == document.location && setTimeout(function() {
        null == document.body ? setTimeout(function() {
          X(y, function(B) {
            window.parent.postMessage({sandbox:B}, "*");
          });
        }, 1500) : X(y, function(B) {
          window.parent.postMessage({sandbox:B}, "*");
        });
      }, 800);
    }
  }, !1), window.parent.postMessage({sandbox:document.location + "", isUrlMsg:!0}, "*"));
  window.addEventListener("error", function(E, y, B, R, Q) {
    "ipbakfmnjdenbmoenhicfmoojdojjjem" != chrome.runtime.id && "blfpbjkajgamcehdbehfdioapoiibdmc" != chrome.runtime.id || console.log(Q);
    return !1;
  });
  return {scan:X};
}();
(function() {
  let X = !1, Z = !1;
  const E = window.opera || -1 < navigator.userAgent.indexOf(" OPR/");
  var y = -1 < navigator.userAgent.toLowerCase().indexOf("firefox");
  const B = -1 < navigator.userAgent.toLowerCase().indexOf("edge/"), R = /Apple Computer/.test(navigator.vendor) && /Safari/.test(navigator.userAgent), Q = !E && !y && !B & !R, H = y ? "Firefox" : R ? "Safari" : Q ? "Chrome" : E ? "Opera" : B ? "Edge" : "Unknown", q = chrome.runtime.getManifest().version;
  let t = !1;
  try {
    t = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent);
  } catch (a) {
  }
  if (!window.keepaHasRun) {
    window.keepaHasRun = !0;
    var F = 0;
    chrome.runtime.onMessage.addListener((a, b, d) => {
      switch(a.key) {
        case "updateToken":
          f.iframeStorage ? f.iframeStorage.contentWindow.postMessage({origin:"keepaContentScript", key:"updateTokenWebsite", value:a.value}, f.iframeStorage.src) : window.postMessage({origin:"keepaContentScript", key:"updateTokenWebsite", value:a.value}, "*");
      }
    });
    window.addEventListener("message", function(a) {
      if ("undefined" == typeof a.data.sandbox) {
        if ("https://keepa.com" == a.origin || "https://test.keepa.com" == a.origin || "https://dyn.keepa.com" == a.origin) {
          if (a.data.hasOwnProperty("origin") && "keepaIframe" == a.data.origin) {
            f.handleIFrameMessage(a.data.key, a.data.value, function(b) {
              try {
                a.source.postMessage({origin:"keepaContentScript", key:a.data.key, value:b, id:a.data.id}, a.origin);
              } catch (d) {
              }
            });
          } else {
            if ("string" === typeof a.data) {
              const b = a.data.split(",");
              if (2 > b.length) {
                return;
              }
              if (2 < b.length) {
                let d = 2;
                const g = b.length;
                for (; d < g; d++) {
                  b[1] += "," + b[d];
                }
              }
              f.handleIFrameMessage(b[0], b[1], function(d) {
                a.source.postMessage({origin:"keepaContentScript", value:d}, a.origin);
              });
            }
          }
        }
        if (a.origin.match(/^https?:\/\/.*?\.amazon\.(de|com|co\.uk|co\.jp|jp|ca|fr|es|nl|it|in|com\.mx|com\.br)/)) {
          let b;
          try {
            b = JSON.parse(a.data);
          } catch (d) {
            return;
          }
          (b = b.asin) && /^([BC][A-Z0-9]{9}|\d{9}(!?X|\d))$/.test(b.trim()) && (b != f.ASIN ? (f.ASIN = b, f.swapIFrame()) : 0 != F ? (window.clearTimeout(F), F = 1) : F = window.setTimeout(function() {
            f.swapIFrame();
          }, 1000));
        }
      }
    });
    var f = {domain:0, iframeStorage:null, ASIN:null, tld:"", placeholder:"", cssFlex:function() {
      let a = "flex";
      const b = ["flex", "-webkit-flex", "-moz-box", "-webkit-box", "-ms-flexbox"], d = document.createElement("flexelement");
      for (let g in b) {
        try {
          if ("undefined" != d.style[b[g]]) {
            a = b[g];
            break;
          }
        } catch (e) {
        }
      }
      return a;
    }(), getDomain:function(a) {
      switch(a) {
        case "com":
          return 1;
        case "co.uk":
          return 2;
        case "de":
          return 3;
        case "fr":
          return 4;
        case "co.jp":
          return 5;
        case "jp":
          return 5;
        case "ca":
          return 6;
        case "it":
          return 8;
        case "es":
          return 9;
        case "in":
          return 10;
        case "com.mx":
          return 11;
        case "com.br":
          return 12;
        case "com.au":
          return 13;
        case "nl":
          return 14;
        default:
          return -1;
      }
    }, revealWorking:!1, juvecOnlyOnce:!1, revealMapOnlyOnce:!1, revealCache:{}, revealMAP:function() {
      f.revealMapOnlyOnce || (f.revealMapOnlyOnce = !0, chrome.runtime?.id && chrome.runtime.sendMessage({type:"isPro"}, a => {
        if (null == a.value) {
          console.log("stock data fail");
        } else {
          var b = a.amazonSellerIds, d = a.stockData, g = !0 === a.value, e = c => {
            c = c.trim();
            let h = d.amazonNames[c];
            return h ? "W" === h ? d.warehouseIds[f.domain] : "A" === h ? d.amazonIds[f.domain] : h : (c = c.match(new RegExp(d.sellerId))) && c[1] ? c[1] : null;
          };
          chrome.storage.local.get("revealStock", function(c) {
            "undefined" == typeof c && (c = {});
            let h = !0;
            try {
              h = "0" != c.revealStock;
            } catch (m) {
            }
            onlyOnceLogStock && (onlyOnceLogStock = !1, console.log("Stock " + g + " " + h));
            try {
              if ((h || "com" == f.tld) && !f.revealWorking) {
                if (f.revealWorking = !0, document.getElementById("keepaMAP")) {
                  f.revealWorking = !1;
                } else {
                  var k = function() {
                    const m = new MutationObserver(function(u) {
                      setTimeout(function() {
                        f.revealMAP();
                      }, 100);
                      try {
                        m.disconnect();
                      } catch (p) {
                      }
                    });
                    m.observe(document.getElementById("keepaMAP").parentNode.parentNode.parentNode, {childList:!0, subtree:!0});
                  }, l = (m, u, p, v, z, w, N, O, T, L) => {
                    if (("undefined" == typeof f.revealCache[v] || null == m.parentElement.querySelector(".keepaStock")) && "undefined" !== typeof b) {
                      null == O && (O = b[f.domain]);
                      var M = "" == m.id && "aod-pinned-offer" == m.parentNode.id;
                      w = w || M;
                      try {
                        p = p || -1 != m.textContent.toLowerCase().indexOf("to cart to see") || !w && /(our price|always remove it|add this item to your cart|see product details in cart|see price in cart)/i.test(document.getElementById("price").textContent);
                      } catch (n) {
                      }
                      if (p || g) {
                        I(m, u, p, v, w);
                        var S = n => {
                          const W = document.getElementById("keepaStock" + v);
                          if (null != W) {
                            W.innerHTML = "";
                            if (null != n && null != n.price && p) {
                              var V = document.createElement("div");
                              n = 5 == f.domain ? n.price : (Number(n.price) / 100).toFixed(2);
                              let ba = new Intl.NumberFormat(" en-US en-GB de-DE fr-FR ja-JP en-CA zh-CN it-IT es-ES hi-IN es-MX pt-BR en-AU nl-NL tr-TR".split(" ")[f.domain], {style:"currency", currency:" USD GBP EUR EUR JPY CAD CNY EUR EUR INR MXN BRL AUD EUR TRY".split(" ")[f.domain]});
                              0 < n && (V.innerHTML = 'Price&emsp;&ensp;<span style="font-weight: bold;">' + ba.format(n) + "</span>");
                              W.parentNode.parentNode.parentNode.prepend(V);
                            }
                            g && (n = f.revealCache[v].stock, 999 == n ? n = "999+" : 1000 == n ? n = "1000+" : -3 != f.revealCache[v].price && 1 > f.revealCache[v].price && (30 == n || T) ? n += "+" : f.revealCache[v].isMaxQty && (n += "+"), V = document.createElement("span"), V.style = "font-weight: bold;", V.innerText = n + " ", n = document.createElement("span"), n.style = "color:#da4c33;", n.innerText = " order limit", W.appendChild(V), f.revealCache[v].limit && (0 < f.revealCache[v].orderLimit && 
                            (n.innerText += ": " + f.revealCache[v].orderLimit), W.appendChild(n)), V = f.revealCache[v].errorCode) && (n = document.createElement("span"), n.style = "color: #f7d1d1;", n.innerText = " (e_" + V + ")", null != f.revealCache[v].error && (n.title = f.revealCache[v].error + ". Contact info@keepa.com with a screenshot & URL for assistance."), W.appendChild(n));
                          }
                        };
                        if ("undefined" != typeof f.revealCache[v] && -1 != f.revealCache[v]) {
                          "pending" != f.revealCache[v] && S(f.revealCache[v]);
                        } else {
                          f.revealCache[v] = "pending";
                          w = m = "";
                          try {
                            m = document.querySelector("meta[name=encrypted-slate-token]").getAttribute("content"), w = document.querySelector("#aod-offer-list input#aod-atc-csrf-token").getAttribute("value");
                          } catch (n) {
                          }
                          chrome.runtime?.id && chrome.runtime.sendMessage({type:"getStock", asin:u, oid:v, sellerId:O, maxQty:N, hasPlus:T, isMAP:p, host:document.location.hostname, force:p, referer:document.location + "", domainId:f.domain, cachedStock:f.revealCache[O], offscreen:!1, atcCsrf:w || L, slateToken:m, session:z}, n => {
                            if ("undefined" == typeof n || null == n || !1 === n?.stock) {
                              if (n = document.getElementById("keepaMAP")) {
                                n.innerHTML = "";
                              }
                            } else {
                              f.revealCache[v] = n, f.revealCache[O] = n, S(n);
                            }
                          });
                        }
                      }
                    }
                  }, I = (m, u, p, v, z) => {
                    u = "" == m.id && "aod-pinned-offer" == m.parentNode.id;
                    var w = (z ? m.parentElement : m).querySelector(".keepaMAP");
                    if (null == (z ? m.parentElement : m).querySelector(".keepaStock")) {
                      null != w && null != w.parentElement && w.parentElement.remove();
                      var N = z ? "165px" : "55px;height:20px;";
                      w = document.createElement("div");
                      w.id = "keepaMAP" + (z ? p + v : "");
                      w.className = "a-section a-spacing-none a-spacing-top-micro aod-clear-float keepaStock";
                      p = document.createElement("div");
                      p.className = "a-fixed-left-grid";
                      var O = document.createElement("div");
                      O.style = "padding-left:" + N;
                      z && (O.className = "a-fixed-left-grid-inner");
                      var T = document.createElement("div");
                      T.style = "width:" + N + ";margin-left:-" + N + ";float:left;";
                      T.className = "a-fixed-left-grid-col aod-padding-right-10 a-col-left";
                      N = document.createElement("div");
                      N.style = "padding-left:0%;float:left;";
                      N.className = "a-fixed-left-grid-col a-col-right";
                      var L = document.createElement("span");
                      L.className = "a-size-small a-color-tertiary";
                      var M = document.createElement("span");
                      M.style = "color: #dedede;";
                      M.innerText = "loading\u2026";
                      var S = document.createElement("span");
                      S.className = "a-size-small a-color-base";
                      S.id = "keepaStock" + v;
                      S.appendChild(M);
                      N.appendChild(S);
                      T.appendChild(L);
                      O.appendChild(T);
                      O.appendChild(N);
                      p.appendChild(O);
                      w.appendChild(p);
                      L.className = "a-size-small a-color-tertiary";
                      f.revealWorking = !1;
                      g && (L.innerText = "Stock");
                      z ? u ? (m = document.querySelector("#aod-pinned-offer-show-more-link"), 0 == m.length && document.querySelector("#aod-pinned-offer-main-content-show-more"), m.prepend(w)) : m.parentNode.insertBefore(w, m.parentNode.children[m.parentNode.children.length - 1]) : m.appendChild(w);
                      z || k();
                    }
                  }, J = document.location.href, P = new MutationObserver(function(m) {
                    try {
                      var u = document.querySelectorAll("#aod-offer,#aod-pinned-offer");
                      if (null != u && 0 != u.length) {
                        m = null;
                        var p = u[0].querySelector('input[name="session-id"]');
                        if (p) {
                          m = p.getAttribute("value");
                        } else {
                          if (p = document.querySelector("#session-id")) {
                            m = document.querySelector("#session-id").value;
                          }
                        }
                        if (!m) {
                          var v = document.querySelectorAll("script");
                          for (const z of v) {
                            let w = z.text.match("ue_sid.?=.?'([0-9-]{19})'");
                            w && (m = w[1]);
                          }
                        }
                        if (m) {
                          for (const z of u) {
                            if (null != z && "DIV" == z.nodeName) {
                              let w;
                              p = 999;
                              let N = z.querySelector('input[name="offeringID.1"]');
                              if (N) {
                                w = N.getAttribute("value");
                              } else {
                                try {
                                  const L = z.querySelectorAll("[data-aod-atc-action]");
                                  if (0 < L.length) {
                                    let M = JSON.parse(L[0].dataset.aodAtcAction);
                                    w = M.oid;
                                    p = M.maxQty;
                                  }
                                } catch (L) {
                                  try {
                                    const M = z.querySelectorAll("[data-aw-aod-cart-api]");
                                    if (0 < M.length) {
                                      let S = JSON.parse(M[0].dataset.awAodCartApi);
                                      w = S.oid;
                                      p = S.maxQty;
                                    }
                                  } catch (M) {
                                  }
                                }
                              }
                              if (!w) {
                                continue;
                              }
                              const O = z.children[0];
                              u = null;
                              if (d) {
                                for (v = 0; v < d.soldByOffers.length; v++) {
                                  let L = z.querySelector(d.soldByOffers[v]);
                                  if (null == L) {
                                    continue;
                                  }
                                  u = e(L.innerText);
                                  if (null != u) {
                                    break;
                                  }
                                  let M = L.getAttribute("href") || L.innerHTML;
                                  u = e(M);
                                  if (null != u) {
                                    break;
                                  }
                                }
                              }
                              const T = z.textContent.toLowerCase().includes("add to cart to see product details.");
                              l(O, f.ASIN, T, w, m, !0, p, u);
                            }
                          }
                        } else {
                          console.error("missing sessionId");
                        }
                      }
                    } catch (z) {
                      console.log(z), f.reportBug(z, "MAP error: " + J);
                    }
                  });
                  P.observe(document.querySelector("body"), {childList:!0, attributes:!1, characterData:!1, subtree:!0, attributeOldValue:!1, characterDataOldValue:!1});
                  window.onunload = function u() {
                    try {
                      window.detachEvent("onunload", u), P.disconnect();
                    } catch (p) {
                    }
                  };
                  var r = document.querySelector(d.soldOfferId);
                  c = null;
                  if (d) {
                    var A = document.querySelector(d.soldByBBForm);
                    A && (c = A.getAttribute("value"));
                    if (null == c) {
                      for (A = 0; A < d.soldByBB.length; A++) {
                        var C = document.querySelector(d.soldByBB[A]);
                        if (null != C && (c = e(C.innerHTML), null != c)) {
                          break;
                        }
                      }
                    }
                  }
                  if (null != r && null != r.value) {
                    var K = r.parentElement.querySelector("#session-id");
                    const u = r.parentElement.querySelector("#ASIN"), p = r.parentElement.querySelector("#selectQuantity #quantity > option:last-child");
                    let v = r.parentElement.querySelector('input[name*="CSRF" i]')?.getAttribute("value");
                    if (null != K && null != u) {
                      for (C = 0; C < d.mainEl.length; C++) {
                        let z = document.querySelector(d.mainEl[C]);
                        if (null != z) {
                          A = C = !1;
                          if (null != p) {
                            try {
                              0 < p.innerText.indexOf("+") && (A = !0), C = Number("" == p.value ? p.innerText.replaceAll("+", "") : p.value);
                            } catch (w) {
                              console.log(w);
                            }
                          }
                          l(z, u.value, !1, r.value, K.value, !1, C, c, A, v);
                          break;
                        }
                      }
                    }
                  }
                  var x = document.getElementById("price");
                  if (null != x && /(our price|always remove it|add this item to your cart|see product details in cart|see price in cart)/i.test(x.textContent)) {
                    let u = document.getElementById("merchant-info");
                    K = r = "";
                    if (u) {
                      if (-1 == u.textContent.toLowerCase().indexOf("amazon.c")) {
                        const p = x.querySelector('span[data-action="a-modal"]');
                        if (p) {
                          var D = p.getAttribute("data-a-modal");
                          D.match(/offeringID\.1=(.*?)&amp/) && (r = RegExp.$1);
                        }
                        if (0 == r.length) {
                          if (D.match('map_help_pop_(.*?)"')) {
                            K = RegExp.$1;
                          } else {
                            f.revealWorking = !1;
                            return;
                          }
                        }
                      }
                      if (null != r && 10 < r.length) {
                        const p = document.querySelector("#session-id");
                        l(x, f.ASIN, !1, r, p.value, !1, !1, K);
                      }
                    } else {
                      f.revealWorking = !1;
                    }
                  } else {
                    f.revealWorking = !1;
                  }
                }
              }
            } catch (m) {
              f.revealWorking = !1, console.log(m);
            }
          });
        }
      }));
    }, onPageLoad:function() {
      f.tld = RegExp.$1;
      const a = RegExp.$3;
      f.ASIN || (f.ASIN = a);
      f.domain = f.getDomain(f.tld);
      chrome.storage.local.get(["s_boxType", "s_boxOfferListing"], function(b) {
        "undefined" == typeof b && (b = {});
        document.addEventListener("DOMContentLoaded", function(d) {
          d = document.getElementsByTagName("head")[0];
          const g = document.createElement("script");
          g.type = "text/javascript";
          g.src = chrome.runtime.getURL("selectionHook.js");
          d.appendChild(g);
          "0" == b.s_boxType ? f.swapIFrame() : f.getPlaceholderAndInsertIFrame((e, c) => {
            if (void 0 !== e) {
              c = document.createElement("div");
              c.setAttribute("id", "keepaButton");
              c.setAttribute("style", "    background-color: #444;\n    border: 0 solid #ccc;\n    border-radius: 6px 6px 6px 6px;\n    color: #fff;\n    cursor: pointer;\n    font-size: 12px;\n    margin: 15px;\n    padding: 6px;\n    text-decoration: none;\n    text-shadow: none;\n    display: flex;\n    box-shadow: 0px 0px 7px 0px #888;\n    width: 100px;\n    background-repeat: no-repeat;\n    height: 32px;\n    background-position-x: 7px;\n    background-position-y: 7px;\n    text-align: center;\n    background-image: url(https://cdn.keepa.com/img/logo_circled_w.svg);\n    background-size: 80px;");
              var h = document.createElement("style");
              h.appendChild(document.createTextNode("#keepaButton:hover{background-color:#666 !important}"));
              document.head.appendChild(h);
              c.addEventListener("click", function() {
                const k = document.getElementById("keepaButton");
                k.parentNode.removeChild(k);
                f.swapIFrame();
              }, !1);
              e.parentNode.insertBefore(c, e);
            }
          });
        }, !1);
      });
    }, swapIFrame:function() {
      if ("com.au" == f.tld) {
        try {
          f.revealMAP(document, f.ASIN, f.tld), f.revealMapOnlyOnce = !1;
        } catch (b) {
        }
      } else {
        if (!document.getElementById("keepaButton")) {
          f.swapIFrame.swapTimer && clearTimeout(f.swapIFrame.swapTimer);
          f.swapIFrame.swapTimer = setTimeout(function() {
            if (!t) {
              document.getElementById("keepaContainer") || f.getPlaceholderAndInsertIFrame(f.insertIFrame);
              try {
                f.revealMAP(document, f.ASIN, f.tld), f.revealMapOnlyOnce = !1;
              } catch (b) {
              }
              f.swapIFrame.swapTimer = setTimeout(function() {
                document.getElementById("keepaContainer") || f.getPlaceholderAndInsertIFrame(f.insertIFrame);
              }, 2000);
            }
          }, 2000);
          var a = document.getElementById("keepaContainer");
          if (null != f.iframeStorage && a) {
            try {
              f.iframeStorage.contentWindow.postMessage({origin:"keepaContentScript", key:"updateASIN", value:{d:f.domain, a:f.ASIN, eType:H, eVersion:q, url:document.location.href}}, "*");
            } catch (b) {
              console.error(b);
            }
          } else {
            f.getPlaceholderAndInsertIFrame(f.insertIFrame);
            try {
              f.revealMAP(document, f.ASIN, f.tld), f.revealMapOnlyOnce = !1;
            } catch (b) {
            }
          }
        }
      }
    }, getDevicePixelRatio:function() {
      let a = 1;
      void 0 !== window.screen.systemXDPI && void 0 !== window.screen.logicalXDPI && window.screen.systemXDPI > window.screen.logicalXDPI ? a = window.screen.systemXDPI / window.screen.logicalXDPI : void 0 !== window.devicePixelRatio && (a = window.devicePixelRatio);
      return a;
    }, getPlaceholderAndInsertIFrame:function(a) {
      chrome.storage.local.get("keepaBoxPlaceholder keepaBoxPlaceholderBackup keepaBoxPlaceholderBackupClass keepaBoxPlaceholderAppend keepaBoxPlaceholderBackupAppend webGraphType webGraphRange".split(" "), function(b) {
        "undefined" == typeof b && (b = {});
        let d = 0;
        const g = function() {
          if (!document.getElementById("keepaButton") && !document.getElementById("amazonlive-homepage-widget")) {
            var e = document.getElementById("gpdp-btf-container");
            if (e && e.previousElementSibling) {
              f.insertIFrame(e.previousElementSibling, !1, !0);
            } else {
              if ((e = document.getElementsByClassName("mocaGlamorContainer")[0]) || (e = document.getElementById("dv-sims")), e ||= document.getElementById("mas-terms-of-use"), e && e.nextSibling) {
                f.insertIFrame(e.nextSibling, !1, !0);
              } else {
                var c = b.keepaBoxPlaceholder || "#bottomRow";
                e = !1;
                if (c = document.querySelector(c)) {
                  "sims_fbt" == c.previousElementSibling.id && (c = c.previousElementSibling, "bucketDivider" == c.previousElementSibling.className && (c = c.previousElementSibling), e = !0), 1 == b.keepaBoxPlaceholderAppend && (c = c.nextSibling), a(c, e);
                } else {
                  if (c = b.keepaBoxPlaceholderBackup || "#elevatorBottom", "ATFCriticalFeaturesDataContainer" == c && (c = "#ATFCriticalFeaturesDataContainer"), c = document.querySelector(c)) {
                    1 == b.keepaBoxPlaceholderBackupAppend && (c = c.nextSibling), a(c, !0);
                  } else {
                    if (c = document.getElementById("hover-zoom-end")) {
                      a(c, !0);
                    } else {
                      if (t) {
                        if ((c = document.querySelector("#ATFCriticalFeaturesDataContainer,#atc-toast-overlay,#productTitleGroupAnchor")) && c.nextSibling) {
                          a(c.nextSibling, !0);
                          return;
                        }
                        document.querySelector("#tabular_feature_div,#olpLinkWidget_feature_div,#tellAFriendBox_feature_div");
                        if (c && c.nextSibling) {
                          a(c.nextSibling, !0);
                          return;
                        }
                      }
                      c = b.keepaBoxPlaceholderBackupClass || ".a-fixed-left-grid";
                      if ((c = document.querySelector(c)) && c.nextSibling) {
                        a(c.nextSibling, !0);
                      } else {
                        e = 0;
                        c = document.getElementsByClassName("twisterMediaMatrix");
                        var h = !!document.getElementById("dm_mp3Player");
                        if ((c = 0 == c.length ? document.getElementById("handleBuy") : c[0]) && 0 == e && !h && null != c.nextElementSibling) {
                          let k = !1;
                          for (h = c; h;) {
                            if (h = h.parentNode, "table" === h.tagName.toLowerCase()) {
                              if ("buyboxrentTable" === h.className || /buyBox/.test(h.className) || "buyingDetailsGrid" === h.className) {
                                k = !0;
                              }
                              break;
                            } else if ("html" === h.tagName.toLowerCase()) {
                              break;
                            }
                          }
                          if (!k) {
                            c = c.nextElementSibling;
                            a(c, !1);
                            return;
                          }
                        }
                        c = document.getElementsByClassName("bucketDivider");
                        0 == c.length && (c = document.getElementsByClassName("a-divider-normal"));
                        if (!c[e]) {
                          if (!c[0]) {
                            40 > d++ && window.setTimeout(function() {
                              g();
                            }, 100);
                            return;
                          }
                          e = 0;
                        }
                        for (h = c[e]; h && c[e];) {
                          if (h = h.parentNode, "table" === h.tagName.toLowerCase()) {
                            if ("buyboxrentTable" === h.className || /buyBox/.test(h.className) || "buyingDetailsGrid" === h.className) {
                              h = c[++e];
                            } else {
                              break;
                            }
                          } else if ("html" === h.tagName.toLowerCase()) {
                            break;
                          }
                        }
                        f.placeholder = c[e];
                        c[e] && c[e].parentNode && (e = document.getElementsByClassName("lpo")[0] && c[1] && 0 == e ? c[1] : c[e], a(e, !1));
                      }
                    }
                  }
                }
              }
            }
          }
        };
        g();
      });
    }, getAFComment:function(a) {
      for (a = [a]; 0 < a.length;) {
        const b = a.pop();
        for (let d = 0; d < b.childNodes.length; d++) {
          const g = b.childNodes[d];
          if (8 === g.nodeType && -1 < g.textContent.indexOf("MarkAF")) {
            return g;
          }
          a.push(g);
        }
      }
      return null;
    }, insertIFrame:function(a, b) {
      if (null != f.iframeStorage && document.getElementById("keepaContainer")) {
        f.swapIFrame();
      } else {
        var d = document.getElementById("hover-zoom-end"), g = function(e) {
          var c = document.getElementById(e);
          const h = [];
          for (; c;) {
            h.push(c), c.id = "a-different-id", c = document.getElementById(e);
          }
          for (c = 0; c < h.length; ++c) {
            h[c].id = e;
          }
          return h;
        }("hover-zoom-end");
        chrome.storage.local.get("s_boxHorizontal", function(e) {
          "undefined" == typeof e && (e = {});
          if (null == a) {
            setTimeout(() => {
              f.getPlaceholderAndInsertIFrame(f.insertIFrame);
            }, 3000);
          } else {
            var c = e.s_boxHorizontal, h = window.innerWidth - 50;
            if (!document.getElementById("keepaContainer")) {
              e = document.createElement("div");
              "0" == c ? (h -= 550, 960 > h && (h = 960), e.setAttribute("style", "min-width: 935px; max-width:" + h + "px;display: flex;  height: 500px; border:0 none; margin: 10px 0 0;")) : e.setAttribute("style", "min-width: 935px; width: calc(100% - 30px); height: 500px; display: flex; border:0 none; margin: 10px 0 0;");
              t && (c = (window.innerWidth - 1 * parseFloat(getComputedStyle(document.documentElement).fontSize)) / 935, e.setAttribute("style", "width: 935px;height: " + Math.max(300, 500 * c) + "px;display: flex;border:0 none;transform-origin: 0 0;transform:scale(" + c + ");margin: 10px -1rem 0 -1rem;"));
              e.setAttribute("id", "keepaContainer");
              var k = document.createElement("iframe");
              c = document.createElement("div");
              c.setAttribute("id", "keepaClear");
              k.setAttribute("style", "width: 100%; height: 100%; border:0 none;overflow: hidden;");
              k.setAttribute("src", "https://keepa.com/keepaBox.html");
              k.setAttribute("scrolling", "no");
              k.setAttribute("id", "keepa");
              Z ||= !0;
              e.appendChild(k);
              h = !1;
              if (!b) {
                null == a.parentNode || "promotions_feature_div" !== a.parentNode.id && "dp-out-of-stock-top_feature_div" !== a.parentNode.id || (a = a.parentNode);
                try {
                  var l = a.previousSibling.previousSibling;
                  null != l && "technicalSpecifications_feature_div" == l.id && (a = l);
                } catch (K) {
                }
                0 < g.length && (d = g[g.length - 1]) && "centerCol" != d.parentElement.id && ((l = f.getFirstInDOM([a, d], document.body)) && 600 < l.parentElement.offsetWidth && (a = l), a === d && (h = !0));
                (l = document.getElementById("title") || document.getElementById("title_row")) && f.getFirstInDOM([a, l], document.body) !== l && (a = l);
              }
              l = document.getElementById("vellumMsg");
              null != l && (a = l);
              l = document.body;
              var I = document.documentElement;
              I = Math.max(l.scrollHeight, l.offsetHeight, I.clientHeight, I.scrollHeight, I.offsetHeight);
              var J = a.offsetTop / I;
              if (0.5 < J || 0 > J) {
                l = f.getAFComment(l), null != l && (J = a.offsetTop / I, 0.5 > J && (a = l));
              }
              if (a.parentNode) {
                l = document.querySelector(".container_vertical_middle");
                "burjPageDivider" == a.id ? (a.parentNode.insertBefore(e, a), b || a.parentNode.insertBefore(c, e.nextSibling)) : "bottomRow" == a.id ? (a.parentNode.insertBefore(e, a), b || a.parentNode.insertBefore(c, e.nextSibling)) : h ? (a.parentNode.insertBefore(e, a.nextSibling), b || a.parentNode.insertBefore(c, e.nextSibling)) : null != l ? (a = l, a.parentNode.insertBefore(e, a.nextSibling), b || a.parentNode.insertBefore(c, e.nextSibling)) : (a.parentNode.insertBefore(e, a), b || a.parentNode.insertBefore(c, 
                e));
                f.iframeStorage = k;
                e.style.display = f.cssFlex;
                var P = !1, r = 5;
                if (!t) {
                  var A = setInterval(function() {
                    if (0 >= r--) {
                      clearInterval(A);
                    } else {
                      var K = null != document.getElementById("keepa");
                      try {
                        if (!K) {
                          throw f.getPlaceholderAndInsertIFrame(f.insertIFrame), 1;
                        }
                        if (P) {
                          throw 1;
                        }
                        document.getElementById("keepa").contentDocument.location = iframeUrl;
                      } catch (x) {
                        clearInterval(A);
                      }
                    }
                  }, 4000), C = function() {
                    P = !0;
                    k.removeEventListener("load", C, !1);
                    f.synchronizeIFrame();
                  };
                  k.addEventListener("load", C, !1);
                }
              } else {
                f.swapIFrame();
              }
            }
          }
        });
      }
    }, handleIFrameMessage:function(a, b, d) {
      switch(a) {
        case "resize":
          X ||= !0;
          a = b;
          b = "" + b;
          -1 == b.indexOf("px") && (b += "px");
          let g = document.getElementById("keepaContainer");
          g && (g.style.height = b, t && (g.style.marginBottom = -(a * (1 - window.innerWidth / 935)) + "px"));
          break;
        case "ping":
          d({location:chrome.runtime.id + " " + document.location});
          break;
        case "openPage":
          chrome.runtime?.id && chrome.runtime.sendMessage({type:"openPage", url:b});
          break;
        case "getToken":
          let e = {d:f.domain, a:f.ASIN, eType:H, eVersion:q, url:document.location.href};
          chrome.runtime?.id ? f.sendMessageWithRetry({type:"getCookie", key:"token"}, 3, 1000, c => {
            e.token = c?.value;
            e.install = c?.install;
            d(e);
          }, c => {
            console.log("failed token retrieval: ", c);
            d(e);
          }) : d(e);
          break;
        case "setCookie":
          chrome.runtime?.id && chrome.runtime.sendMessage({type:"setCookie", key:b.key, val:b.val});
      }
    }, sendMessageWithRetry:function(a, b, d, g, e) {
      let c = 0, h = !1;
      const k = () => {
        c += 1;
        chrome.runtime.sendMessage(a, l => {
          h || (h = !0, g(l));
        });
        setTimeout(() => {
          h || (c < b ? setTimeout(k, d) : (console.log("Failed to receive a response after maximum retries."), e()));
        }, d);
      };
      k();
    }, synchronizeIFrame:function() {
      let a = 0;
      chrome.storage.local.get("s_boxHorizontal", function(g) {
        "undefined" != typeof g && "undefined" != typeof g.s_boxHorizontal && (a = g.s_boxHorizontal);
      });
      let b = window.innerWidth, d = !1;
      t || window.addEventListener("resize", function() {
        d || (d = !0, window.setTimeout(function() {
          if (b != window.innerWidth && "0" == a) {
            b = window.innerWidth;
            let g = window.innerWidth - 50;
            g -= 550;
            935 > g && (g = 935);
            document.getElementById("keepaContainer").style.width = g;
          }
          d = !1;
        }, 100));
      }, !1);
    }, getFirstInDOM:function(a, b) {
      let d;
      for (b = b.firstChild; b; b = b.nextSibling) {
        if ("IFRAME" !== b.nodeName && 1 === b.nodeType) {
          if (-1 !== a.indexOf(b)) {
            return b;
          }
          if (d = f.getFirstInDOM(a, b)) {
            return d;
          }
        }
      }
      return null;
    }, getClipRect:function(a) {
      "string" === typeof a && (a = document.querySelector(a));
      let b = 0, d = 0;
      const g = function(e) {
        b += e.offsetLeft;
        d += e.offsetTop;
        e.offsetParent && g(e.offsetParent);
      };
      g(a);
      return 0 == d && 0 == b ? f.getClipRect(a.parentNode) : {top:d, left:b, width:a.offsetWidth, height:a.offsetHeight};
    }, findPlaceholderBelowImages:function(a) {
      const b = a;
      let d, g = 100;
      do {
        for (g--, d = null; !d;) {
          d = a.nextElementSibling, d || (d = a.parentNode.nextElementSibling), a = d ? d : a.parentNode.parentNode, !d || "IFRAME" !== d.nodeName && "SCRIPT" !== d.nodeName && 1 === d.nodeType || (d = null);
        }
      } while (0 < g && 100 < f.getClipRect(d).left);
      return d ? d : b;
    }, httpGet:function(a, b) {
      const d = new XMLHttpRequest();
      b && (d.onreadystatechange = function() {
        4 == d.readyState && b.call(this, d.responseText);
      });
      d.open("GET", a, !0);
      d.send();
    }, httpPost2:function(a, b, d, g, e) {
      const c = new XMLHttpRequest();
      g && (c.onreadystatechange = function() {
        4 == c.readyState && g.call(this, c.responseText);
      });
      c.withCredentials = e;
      c.open("POST", a, !0);
      c.setRequestHeader("Content-Type", d);
      c.send(b);
    }, httpPost:function(a, b, d, g) {
      f.httpPost2(a, b, "text/plain;charset=UTF-8", d, g);
    }, lastBugReport:0, reportBug:function(a, b, d) {
      var g = Date.now();
      if (!(6E5 > g - f.lastBugReport || /(dead object)|(Script error)|(\.location is null)/i.test(a))) {
        f.lastBugReport = g;
        g = "";
        try {
          g = Error().stack.split("\n").splice(1).splice(1).join("&ensp;&lArr;&ensp;");
          if (!/(keepa|content)\.js/.test(g)) {
            return;
          }
          g = g.replace(RegExp("chrome-extension://.*?/content/", "g"), "").replace(/:[0-9]*?\)/g, ")").replace(/[ ]{2,}/g, "");
        } catch (e) {
        }
        if ("object" == typeof a) {
          try {
            a = a instanceof Error ? a.toString() : JSON.stringify(a);
          } catch (e) {
          }
        }
        null == d && (d = {exception:a, additional:b, url:document.location.host, stack:g});
        null != d.url && d.url.startsWith("blob:") || (d.keepaType = Q ? "keepaChrome" : E ? "keepaOpera" : R ? "keepaSafari" : B ? "keepaEdge" : "keepaFirefox", d.version = q, chrome.storage.local.get("token", function(e) {
          "undefined" == typeof e && (e = {token:"undefined"});
          f.httpPost("https://dyn.keepa.com/service/bugreport/?user=" + e.token + "&type=" + H, JSON.stringify(d));
        }));
      }
    }};
    window.onerror = function(a, b, d, g, e) {
      let c;
      "string" !== typeof a && (e = a.error, c = a.filename || a.fileName, d = a.lineno || a.lineNumber, g = a.colno || a.columnNumber, a = a.message || a.name || e.message || e.name);
      a = a.toString();
      let h = "";
      g = g || 0;
      if (e && e.stack) {
        h = e.stack;
        try {
          h = e.stack.split("\n").splice(1).splice(1).join("&ensp;&lArr;&ensp;");
          if (!/(keepa|content)\.js/.test(h)) {
            return;
          }
          h = h.replace(RegExp("chrome-extension://.*?/content/", "g"), "").replace(/:[0-9]*?\)/g, ")").replace(/[ ]{2,}/g, "");
        } catch (k) {
        }
      }
      "undefined" === typeof d && (d = 0);
      "undefined" === typeof g && (g = 0);
      a = {msg:a, url:(b || c || document.location.toString()) + ":" + d + ":" + g, stack:h};
      "ipbakfmnjdenbmoenhicfmoojdojjjem" != chrome.runtime.id && "blfpbjkajgamcehdbehfdioapoiibdmc" != chrome.runtime.id || console.log(a);
      f.reportBug(null, null, a);
      return !1;
    };
    if (window.self == window.top && !(/.*music\.amazon\..*/.test(document.location.href) || /.*primenow\.amazon\..*/.test(document.location.href) || /.*amazonlive-portal\.amazon\..*/.test(document.location.href) || /.*amazon\.com\/restaurants.*/.test(document.location.href))) {
      y = function(a) {
        chrome.runtime.sendMessage({type:"sendData", val:{key:"m1", payload:[a]}}, function() {
        });
      };
      var G = document.location.href, Y = !1;
      document.addEventListener("DOMContentLoaded", function(a) {
        if (!Y) {
          try {
            if (G.startsWith("https://test.keepa.com") || G.startsWith("https://keepa.com")) {
              let b = document.createElement("div");
              b.id = "extension";
              b.setAttribute("type", H);
              b.setAttribute("version", q);
              document.body.appendChild(b);
              Y = !0;
            }
          } catch (b) {
          }
        }
      });
      var U = !1;
      chrome.runtime.sendMessage({type:"isActive"});
      if (!/((\/images)|(\/review)|(\/customer-reviews)|(ask\/questions)|(\/product-reviews))/.test(G) && !/\/e\/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/.test(G) && (G.match(/^https:\/\/.*?\.amazon\.(de|com|co\.uk|co\.jp|ca|fr|it|es|nl|in|com\.mx|com\.br|com\.au)\/[^.]*?(\/|[?&]ASIN=)([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/) || G.match(/^https:\/\/.*?\.amazon\.(de|com|co\.uk|co\.jp|ca|fr|it|es|nl|in|com\.mx|com\.br|com\.au)\/(.*?)\/dp\/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))\//) || G.match(/^https:\/\/.*?\.amzn\.(com).*?\/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/))) {
        f.onPageLoad(!1), U = !0;
      } else if (!G.match(/^https:\/\/.*?\.amazon\.(de|com|co\.uk|co\.jp|ca|fr|it|nl|es|in|com\.mx|com\.br|com\.au)\/[^.]*?\/(wishlist|registry)/) && !G.match(/^htt(p|ps):\/\/w*?\.amzn\.(com)[^.]*?\/(wishlist|registry)/)) {
        if (G.match("^https://.*?(?:seller).*?.amazon.(de|com|co.uk|co.jp|ca|fr|it|nl|es|in|com.mx|com.br|com.au)/")) {
          y("s" + f.getDomain(RegExp.$1));
          let a = !1;
          function b() {
            a || (a = !0, chrome.runtime.sendMessage({type:"isSellerActive"}), setTimeout(() => {
              a = !1;
            }, 1000));
          }
          b();
          document.addEventListener("mousemove", b);
          document.addEventListener("keydown", b);
          document.addEventListener("touchstart", b);
        } else {
          G.match(/^https:\/\/.*?(?:af.?ilia|part|assoc).*?\.amazon\.(de|com|co\.uk|co\.jp|nl|ca|fr|it|es|in|com\.mx|com\.br|com\.au)\/home/) && y("a" + f.getDomain(RegExp.$1));
        }
      }
      if (!t) {
        y = /^https:\/\/.*?\.amazon\.(de|com|co\.uk|co\.jp|ca|fr|it|es|nl|in|com\.mx|com\.br|com\.au)\/(s([\/?])|gp\/bestsellers\/|gp\/search\/|.*?\/b\/)/;
        (U || G.match(y)) && document.addEventListener("DOMContentLoaded", function(a) {
          let b = null;
          chrome.runtime.sendMessage({type:"getFilters"}, function(d) {
            b = d;
            if (null != b && null != b.value) {
              let g = function() {
                let l = G.match("^https?://.*?.amazon.(de|com|co.uk|co.jp|ca|fr|it|es|in|com.br|nl|com.mx)/");
                if (U || l) {
                  let I = f.getDomain(RegExp.$1);
                  scanner.scan(d.value, function(J) {
                    J.key = "f1";
                    J.domainId = I;
                    chrome.runtime.sendMessage({type:"sendData", val:J}, function(P) {
                    });
                  });
                }
              };
              g();
              let e = document.location.href, c = -1, h = -1, k = -1;
              h = setInterval(function() {
                e != document.location.href && (e = document.location.href, clearTimeout(k), k = setTimeout(function() {
                  g();
                }, 2000), clearTimeout(c), c = setTimeout(function() {
                  clearInterval(h);
                }, 180000));
              }, 2000);
              c = setTimeout(function() {
                clearInterval(h);
              }, 180000);
            }
          });
        });
        y = document.location.href;
        y.match("^https://.*?.amazon.(de|com|co.uk|co.jp|ca|fr|it|es|in|nl|com.mx|com.br|com.au)/") && -1 == y.indexOf("aws.amazon.") && -1 == y.indexOf("music.amazon.") && -1 == y.indexOf("services.amazon.") && -1 == y.indexOf("primenow.amazon.") && -1 == y.indexOf("kindle.amazon.") && -1 == y.indexOf("watch.amazon.") && -1 == y.indexOf("developer.amazon.") && -1 == y.indexOf("skills-store.amazon.") && -1 == y.indexOf("pay.amazon.") && document.addEventListener("DOMContentLoaded", function(a) {
          setTimeout(function() {
            chrome.runtime.onMessage.addListener(function(b, d, g) {
              switch(b.key) {
                case "collectASINs":
                  b = {};
                  var e = !1;
                  d = (document.querySelector("#main") || document.querySelector("#zg") || document.querySelector("#pageContent") || document.querySelector("#wishlist-page") || document.querySelector("#merchandised-content") || document.querySelector("#reactApp") || document.querySelector("[id^='contentGrid']") || document.querySelector("#container") || document.querySelector(".a-container") || document).getElementsByTagName("a");
                  if (void 0 != d && null != d) {
                    for (let h = 0; h < d.length; h++) {
                      var c = d[h].href;
                      /\/images/.test(c) || /\/e\/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/.test(c) || !c.match(/^https?:\/\/.*?\.amazon\.(de|com|co\.uk|co\.jp|ca|fr|it|es|nl|in|com\.mx|com\.br|com\.au)\/[^.]*?(?:\/|\?ASIN=)([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/) && !c.match(/^https?:\/\/.*?\.amzn\.(com)[^.]*?\/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/) || (e = RegExp.$2, c = f.getDomain(RegExp.$1), "undefined" === typeof b[c] && (b[c] = []), b[c].includes(e) || b[c].push(e), e = !0);
                    }
                  }
                  if (e) {
                    g(b);
                  } else {
                    return alert("Keepa: No product ASINs found on this page."), !1;
                  }
                  break;
                default:
                  g({});
              }
            });
            chrome.storage.local.get(["overlayPriceGraph", "webGraphType", "webGraphRange"], ({overlayPriceGraph:b = 0, webGraphType:d = "[]", webGraphRange:g = 365} = {}) => {
              function e(x) {
                if (!r.has(x)) {
                  var D = x.href;
                  if (J.test(D) || P.test(D)) {
                    var m = null;
                  } else {
                    if (m = I.exec(D), !m || D.includes("offer-listing")) {
                      m = null;
                    } else {
                      b: {
                        if (D = m[2], "string" !== typeof D || 0 === D.length) {
                          var u = !1;
                        } else {
                          for (u of D) {
                            D = u.charCodeAt(0);
                            const p = 65 <= D && 90 >= D;
                            if (!(48 <= D && 57 >= D || p)) {
                              u = !1;
                              break b;
                            }
                          }
                          u = !0;
                        }
                      }
                      m = u ? {tld:m[1], asin:m[2]} : null;
                    }
                  }
                  m && (r.add(x), aa.add_events(k, l, x, x.href, m.tld, m.asin));
                }
              }
              function c() {
                A.forEach(e);
                A.clear();
                C = !1;
              }
              function h(x) {
                1 === x.nodeType && ("A" === x.tagName && A.add(x), x.querySelectorAll?.("a").forEach(D => A.add(D)), C || (C = !0, requestIdleCallback(c, {timeout:80})));
              }
              if (1 == b) {
                try {
                  var k = JSON.parse(d);
                } catch {
                  k = void 0;
                }
                var l = Number(g) || 365, I = /^(?:https?:\/\/[^/]*?\.amazon\.([^./]+\.[^./]+|[^./]+)\/[^.]*?(?:\/|\?ASIN=)|https?:\/\/[^/]*?\.amzn\.com\/)([BC][A-Z0-9]{9}|\d{9}(?:X|\d))/i, J = /\/images/, P = /\/e\/([BC][A-Z0-9]{9}|\d{9}(?:X|\d))/, r = new WeakSet();
                Array.from(document.links).forEach(e);
                var A = new Set(), C = !1, K = new MutationObserver(x => {
                  x.forEach(D => D.addedNodes.forEach(h));
                });
                K.observe(document.documentElement, {childList:!0, subtree:!0});
                window.addEventListener("unload", () => K.disconnect(), {once:!0});
              }
            });
          }, 100);
        });
        var aa = {_urlCache:new Map(), _blobUrlCache:new Map(), _containerId:"pf_preview", _gen:0, _getContainer(a) {
          let b = a.getElementById(this._containerId);
          if (b) {
            return b;
          }
          b = a.createElement("div");
          b.id = this._containerId;
          Object.assign(b.style, {position:"fixed", bottom:"12px", right:"12px", zIndex:"10000000", background:"#fff", boxShadow:"0 1px 7px -2px #444", display:"none", pointerEvents:"none"});
          a.body.appendChild(b);
          return b;
        }, _createImage(a, b, d) {
          a = a.createElement("img");
          Object.assign(a.style, {display:"block", position:"relative", padding:"5px", borderTop:"2px solid #ff9f29", borderBottom:"3px solid grey", width:`${b}px`, height:`${d}px`, maxWidth:`${b}px`, maxHeight:`${d}px`});
          return a;
        }, _createSpinner(a, b, d) {
          a = a.createElement("div");
          Object.assign(a.style, {width:`${b}px`, height:`${d}px`, display:"flex", justifyContent:"center", alignItems:"center"});
          a.innerHTML = '\n      <style>\n        @keyframes sp { to { transform: rotate(360deg) } }\n        .sp{\n          width:32px;height:32px;\n          border:4px solid #ff9f29;\n          border-right-color:transparent;\n          border-radius:50%;\n          animation:sp .7s linear infinite;\n        }\n      </style><div class="sp"></div>';
          return a;
        }, _createError(a, b) {
          a = a.createElement("div");
          a.textContent = 429 === b ? "Keepa price graph is rate limited. Please slow down and try again in a minute." : `Couldn\u2019t load Keepa price graph (status ${b}).`;
          Object.assign(a.style, {padding:"8px 12px", width:"100%", textAlign:"center", color:"#c00", font:"12px/1.4 sans-serif"});
          return a;
        }, _viewportDims(a) {
          return {w:Math.min(1000, Math.max(128, Math.floor(0.30 * a.innerWidth))), h:Math.min(1000, Math.max(128, Math.floor(0.30 * a.innerHeight)))};
        }, _buildUrl({asin:a, tld:b, w:d, h:g, graphTypeArr:e, range:c}) {
          a = `https://graph.keepa.com/pricehistory.png?type=${300 > d || 150 > g ? 1 : 2}` + `&asin=${a}&domain=${b}&width=${d}&height=${g}`;
          return a = Array.isArray(e) ? a + (`&amazon=${e[0]}&new=${e[1]}` + `&used=${e[2]}&salesrank=${e[3]}` + `&range=${c}` + `&fba=${e[10]}&fbm=${e[7]}` + `&bb=${e[18]}&ld=${e[8]}` + `&bbu=${e[32]}&pe=${e[33]}` + `&wd=${e[9]}`) : a + "&amazon=1&new=1&used=1&salesrank=1&range=365";
        }, _getUrlCached(a) {
          const b = `${a.asin}|${a.w}x${a.h}|${a.range || 365}`;
          this._urlCache.has(b) || this._urlCache.set(b, this._buildUrl(a));
          return this._urlCache.get(b);
        }, _show(a, b, d, g, e, c) {
          const h = a.currentTarget.ownerDocument, k = h.defaultView;
          this._hide(h);
          const l = ++this._gen, {w:I, h:J} = this._viewportDims(k), P = this._getUrlCached({asin:e, tld:c, w:I, h:J, graphTypeArr:b, range:d}), r = this._getContainer(h), A = this._createImage(h, I, J), C = this._createSpinner(h, I, J);
          r._currentGen = l;
          b = k.innerWidth - a.clientX < 1.05 * I;
          a = k.innerHeight - a.clientY < 1.05 * J;
          r.style.right = b ? "" : "12px";
          r.style.left = b ? "12px" : "";
          r.style.bottom = a ? "" : "12px";
          r.style.top = a ? "12px" : "";
          r.innerHTML = "";
          r.appendChild(C);
          r.style.display = "block";
          const K = () => this._hide(h);
          k.addEventListener("scroll", K, {passive:!0, capture:!0});
          k.addEventListener("resize", K, {passive:!0});
          r._unbind = () => {
            k.removeEventListener("scroll", K, !0);
            k.removeEventListener("resize", K);
          };
          this._blobUrlCache.has(P) ? l === this._gen && (A.src = this._blobUrlCache.get(P), r.replaceChild(A, C)) : f.sendMessageWithRetry({type:"fetchGraph", url:P}, 3, 3000, x => {
            l === this._gen && (x.ok ? (x = x.dataUrl, this._blobUrlCache.set(P, x), A.src = x, A.decode().then(() => {
              l === this._gen && (r.contains(C) ? r.replaceChild(A, C) : r.appendChild(A));
            })) : 0 === x.status ? this._hide(h) : (x = this._createError(h, x.status), r.replaceChild(x, C)));
          }, () => {
            l === this._gen && this._hide(h);
          });
        }, _hide(a = document) {
          (a = a.getElementById(this._containerId)) && "none" !== a.style.display && (a.style.display = "none", a.innerHTML = "", a._unbind?.(), a._unbind = null);
        }, add_events(a, b, d, g, e, c) {
          g.includes("#") || "pf_prevImg" === d.getAttribute("keepaPreview") || (d.setAttribute("keepaPreview", "pf_prevImg"), d.addEventListener("pointerenter", h => this._show(h, a, b, g, c, e)), d.addEventListener("pointerleave", () => this._hide(d.ownerDocument)));
        }};
      }
    }
  }
})();

