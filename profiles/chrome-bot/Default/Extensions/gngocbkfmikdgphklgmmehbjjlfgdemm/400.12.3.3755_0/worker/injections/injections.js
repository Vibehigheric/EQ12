(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApplyCoupons = void 0;
var apply_coupons_base_1 = require("../../../../worker/injections/apply-coupons/apply-coupons-base");
var runtime_message_types_1 = require("../../../../enums/runtime-message-types");
var runtime_message_1 = require("../../../../models/runtime-message");
var data_utils_1 = require("../../../../utils/data-utils");
var ApplyCoupons = /** @class */ (function (_super) {
    __extends(ApplyCoupons, _super);
    function ApplyCoupons(params) {
        return _super.call(this, params) || this;
    }
    ApplyCoupons.prototype.getHeaderImage = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getContentInjectionImagePath('working.gif')];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    ApplyCoupons.prototype.setTitle = function (el) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.addTitleTestingCodesText(el)];
                    case 1:
                        _a.sent();
                        return [4 /*yield*/, this.addTitleTestingCodesDescriptionText(el)];
                    case 2:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCoupons.prototype.setStatusText = function (el) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setStatusTextApplying(el)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCoupons.prototype.setStatusCount = function (el) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setStatusCountText(el)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCoupons.prototype.setFooter = function (el) {
        return __awaiter(this, void 0, void 0, function () {
            var image;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getContentInjectionImagePath('foot.png')];
                    case 1:
                        image = _a.sent();
                        this.addFooterImage(el, image);
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCoupons.prototype.setStatusCode = function (el, code) {
        el.classList.remove(this.HIDDEN_CLASS);
        el.innerText = code;
    };
    ApplyCoupons.prototype.showResult = function (el, detail) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.showFinalHeader(detail.success)];
                    case 1:
                        _a.sent();
                        return [4 /*yield*/, this.constructResultUI(el, detail.success, detail.amount)];
                    case 2:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCoupons.prototype.showFinalHeader = function (success) {
        return __awaiter(this, void 0, void 0, function () {
            var imageName, image;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        imageName = success ? 'flex' : 'towel';
                        return [4 /*yield*/, this.getContentInjectionImagePath("".concat(imageName, ".gif"))];
                    case 1:
                        image = _a.sent();
                        this.headerImageElement.src = image;
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCoupons.prototype.constructResultUI = function (el, success, amount) {
        var _a;
        return __awaiter(this, void 0, void 0, function () {
            var merchant;
            var _this = this;
            return __generator(this, function (_b) {
                merchant = this.data.merchant;
                el.appendChild(this.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                    var titleMsg, _a;
                    return __generator(this, function (_b) {
                        switch (_b.label) {
                            case 0:
                                titleMsg = success ? 'successfullyAppliedCoupons' : 'didNotFindBetterCoupon';
                                _a = div;
                                return [4 /*yield*/, this.getLocalizedString(titleMsg)];
                            case 1:
                                _a.innerText = _b.sent();
                                return [2 /*return*/];
                        }
                    });
                }); }));
                el.appendChild(this.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                    var currency, _a;
                    return __generator(this, function (_b) {
                        switch (_b.label) {
                            case 0:
                                if (!success) return [3 /*break*/, 2];
                                return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.GetCurrencySymbol, merchant))];
                            case 1:
                                currency = _b.sent();
                                div.className = 'highlight-main';
                                div.innerHTML = data_utils_1.DataUtils.getSafeHtml(data_utils_1.DataUtils.formatCurrencyAmount(amount, currency));
                                return [3 /*break*/, 4];
                            case 2:
                                div.className = 'highlight';
                                _a = div;
                                return [4 /*yield*/, this.getLocalizedString('alreadyBestPrice')];
                            case 3:
                                _a.innerText = _b.sent();
                                _b.label = 4;
                            case 4: return [2 /*return*/];
                        }
                    });
                }); }));
                if ((_a = merchant.reward) === null || _a === void 0 ? void 0 : _a.amount) {
                    el.appendChild(this.createElement('img', function (img) { return __awaiter(_this, void 0, void 0, function () {
                        var _a;
                        return __generator(this, function (_b) {
                            switch (_b.label) {
                                case 0:
                                    _a = img;
                                    return [4 /*yield*/, this.getContentInjectionImagePath('plus.png')];
                                case 1:
                                    _a.src = _b.sent();
                                    return [2 /*return*/];
                            }
                        });
                    }); }));
                    el.appendChild(this.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                        var _a;
                        return __generator(this, function (_b) {
                            switch (_b.label) {
                                case 0:
                                    div.className = 'highlight';
                                    _a = div;
                                    return [4 /*yield*/, this.constructCtaString(runtime_message_types_1.RuntimeMessageTypes.ConstructRewardString)];
                                case 1:
                                    _a.innerHTML = _b.sent();
                                    return [2 /*return*/];
                            }
                        });
                    }); }));
                    el.appendChild(this.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                        var msg, _a, _b, _c;
                        return __generator(this, function (_d) {
                            switch (_d.label) {
                                case 0:
                                    msg = this.data.merchant.reward.showUpTo ? 'popup_merchant_earn_currency_per_up_to' : 'popup_merchant_earn_currency_per';
                                    _a = div;
                                    _c = (_b = data_utils_1.DataUtils).getSafeHtml;
                                    return [4 /*yield*/, this.getLocalizedString(msg, this.data.merchant.reward.amount.toString(), this.data.location.currencySymbol)];
                                case 1:
                                    _a.innerHTML = _c.apply(_b, [_d.sent()]);
                                    return [2 /*return*/];
                            }
                        });
                    }); }));
                }
                return [2 /*return*/];
            });
        });
    };
    return ApplyCoupons;
}(apply_coupons_base_1.ApplyCouponsBase));
exports.ApplyCoupons = ApplyCoupons;
(function () {
    var brand = 'SB';
    window['Prdg'] = window['Prdg'] || {};
    window['Prdg'][brand] = window['Prdg'][brand] || {};
    window['Prdg'][brand]['ApplyCoupons'] = ApplyCoupons;
})();

},{"../../../../enums/runtime-message-types":9,"../../../../models/runtime-message":17,"../../../../utils/data-utils":18,"../../../../worker/injections/apply-coupons/apply-coupons-base":20}],2:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SBInjectionFactory = void 0;
var coupon_worker_base_1 = require("../../../worker/injections/coupon-worker-base");
var ext_installed_messenger_base_1 = require("../../../worker/injections/ext-installed-messenger-base");
var serp_injection_base_1 = require("../../../worker/injections/serp-injection-base");
var notification_base_1 = require("../../../worker/injections/notification/notification-base");
var slider_base_1 = require("../../../worker/injections/slider/slider-base");
var conquest_base_1 = require("../../../worker/injections/conquest/conquest-base");
var lost_activation_1 = require("../../../worker/injections/lost-activation/lost-activation");
var apply_coupons_1 = require("./apply-coupons/apply-coupons");
var view_coupons_1 = require("./view-coupons/view-coupons");
var content_injection_type_1 = require("../../../enums/content-injection-type");
var brand_injection_factory_base_1 = require("../../../models/content-injection/brand-injection-factory-base");
var ext_present_injection_base_1 = require("../../../worker/injections/ext-present-injection-base");
var SBInjectionFactory = /** @class */ (function (_super) {
    __extends(SBInjectionFactory, _super);
    function SBInjectionFactory() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.map = new Map()
            .set(content_injection_type_1.ContentInjectionType.ApplyCoupons, apply_coupons_1.ApplyCoupons)
            .set(content_injection_type_1.ContentInjectionType.CouponWorker, coupon_worker_base_1.CouponWorkerBase)
            .set(content_injection_type_1.ContentInjectionType.ExtInstalledMessenger, ext_installed_messenger_base_1.ExtInstalledMessengerBase)
            .set(content_injection_type_1.ContentInjectionType.ExtPresentMessenger, ext_present_injection_base_1.ExtPresentMessengerBase)
            .set(content_injection_type_1.ContentInjectionType.Notification, notification_base_1.NotificationBase)
            .set(content_injection_type_1.ContentInjectionType.SerpInjection, serp_injection_base_1.SerpInjectionBase)
            .set(content_injection_type_1.ContentInjectionType.Slider, slider_base_1.SliderBase)
            .set(content_injection_type_1.ContentInjectionType.ViewCoupons, view_coupons_1.ViewCoupons)
            .set(content_injection_type_1.ContentInjectionType.Conquest, conquest_base_1.ConquestBase)
            .set(content_injection_type_1.ContentInjectionType.LostActivation, lost_activation_1.LostActivationBase);
        return _this;
    }
    return SBInjectionFactory;
}(brand_injection_factory_base_1.BrandInjectionFactoryBase));
exports.SBInjectionFactory = SBInjectionFactory;
window['Prdg'] = window['Prdg'] || {};
window['Prdg']['SBInjectionFactory'] = new SBInjectionFactory();

},{"../../../enums/content-injection-type":5,"../../../models/content-injection/brand-injection-factory-base":13,"../../../worker/injections/conquest/conquest-base":21,"../../../worker/injections/coupon-worker-base":24,"../../../worker/injections/ext-installed-messenger-base":25,"../../../worker/injections/ext-present-injection-base":26,"../../../worker/injections/lost-activation/lost-activation":30,"../../../worker/injections/notification/notification-base":32,"../../../worker/injections/serp-injection-base":33,"../../../worker/injections/slider/slider-base":35,"./apply-coupons/apply-coupons":1,"./view-coupons/view-coupons":3}],3:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewCoupons = void 0;
var view_coupons_base_1 = require("../../../../worker/injections/view-coupons/view-coupons-base");
var inline_registration_1 = require("../../../../worker/injections/inline-registration/inline-registration");
var ViewCoupons = /** @class */ (function (_super) {
    __extends(ViewCoupons, _super);
    function ViewCoupons(params) {
        return _super.call(this, params) || this;
    }
    ViewCoupons.prototype.onUIConstructed = function () {
        if (!this.data.memberId) {
            var target = this.getElement('#inline');
            target.classList.add(this.clientName);
            target.classList.remove('hidden');
            var reg = new inline_registration_1.InlineRegistration({
                injectionId: "".concat(this.clientName, "-inline-reg"),
                extensionRuntimeId: this.extensionRuntimeId,
                parent: target,
                data: this.data
            });
        }
    };
    return ViewCoupons;
}(view_coupons_base_1.ViewCouponsBase));
exports.ViewCoupons = ViewCoupons;
(function () {
    var brand = 'SB';
    window['Prdg'] = window['Prdg'] || {};
    window['Prdg'][brand] = window['Prdg'][brand] || {};
    window['Prdg'][brand]['ViewCoupons'] = ViewCoupons;
})();

},{"../../../../worker/injections/inline-registration/inline-registration":28,"../../../../worker/injections/view-coupons/view-coupons-base":37}],4:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Clients = void 0;
var Clients;
(function (Clients) {
    Clients[Clients["sb"] = 22] = "sb";
    Clients[Clients["mp"] = 257] = "mp";
    Clients[Clients["tada"] = 258] = "tada";
    Clients[Clients["ibd"] = 260] = "ibd";
    Clients[Clients["upm"] = 263] = "upm";
})(Clients = exports.Clients || (exports.Clients = {}));

},{}],5:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContentInjectionType = void 0;
// any updates to this file must also have a corresponding update to all InjectionFactories (ie IBDInjectionFactory)
var ContentInjectionType;
(function (ContentInjectionType) {
    ContentInjectionType[ContentInjectionType["SerpInjection"] = 0] = "SerpInjection";
    ContentInjectionType[ContentInjectionType["Slider"] = 1] = "Slider";
    ContentInjectionType[ContentInjectionType["ViewCoupons"] = 2] = "ViewCoupons";
    ContentInjectionType[ContentInjectionType["ApplyCoupons"] = 3] = "ApplyCoupons";
    ContentInjectionType[ContentInjectionType["CouponWorker"] = 4] = "CouponWorker";
    ContentInjectionType[ContentInjectionType["Notification"] = 5] = "Notification";
    ContentInjectionType[ContentInjectionType["ExtInstalledMessenger"] = 6] = "ExtInstalledMessenger";
    ContentInjectionType[ContentInjectionType["ExtPresentMessenger"] = 7] = "ExtPresentMessenger";
    ContentInjectionType[ContentInjectionType["Conquest"] = 8] = "Conquest";
    ContentInjectionType[ContentInjectionType["LostActivation"] = 9] = "LostActivation";
})(ContentInjectionType = exports.ContentInjectionType || (exports.ContentInjectionType = {}));

},{}],6:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConsoleLogLevels = void 0;
var ConsoleLogLevels;
(function (ConsoleLogLevels) {
    ConsoleLogLevels[ConsoleLogLevels["Off"] = 0] = "Off";
    ConsoleLogLevels[ConsoleLogLevels["Error"] = 1] = "Error";
    ConsoleLogLevels[ConsoleLogLevels["Warn"] = 2] = "Warn";
    ConsoleLogLevels[ConsoleLogLevels["Info"] = 3] = "Info";
    ConsoleLogLevels[ConsoleLogLevels["Debug"] = 4] = "Debug";
    ConsoleLogLevels[ConsoleLogLevels["Trace"] = 5] = "Trace";
    ConsoleLogLevels[ConsoleLogLevels["All"] = 6] = "All";
})(ConsoleLogLevels = exports.ConsoleLogLevels || (exports.ConsoleLogLevels = {}));

},{}],7:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PageIds = void 0;
var PageIds;
(function (PageIds) {
    PageIds[PageIds["Default"] = 274] = "Default";
    PageIds[PageIds["ActivationSliderClick"] = 281] = "ActivationSliderClick";
    PageIds[PageIds["CouponSliderClick"] = 282] = "CouponSliderClick";
    PageIds[PageIds["PopupMerchantClick"] = 283] = "PopupMerchantClick";
    PageIds[PageIds["PopupFeaturedMerchantClick"] = 284] = "PopupFeaturedMerchantClick";
    PageIds[PageIds["LostActivationSliderClick"] = 332] = "LostActivationSliderClick";
    PageIds[PageIds["SecondChanceActivation"] = 333] = "SecondChanceActivation";
})(PageIds = exports.PageIds || (exports.PageIds = {}));

},{}],8:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RedirectContext = void 0;
/**
 * In most cases, we shouldn't have to specify this value and we should use normal business logic
 * to determine which tab to activate/redirect in.  But sometimes, business logic is illogical.
 */
var RedirectContext;
(function (RedirectContext) {
    RedirectContext[RedirectContext["Default"] = 0] = "Default";
    RedirectContext[RedirectContext["SilentTab"] = 1] = "SilentTab"; // Force silent tab (e.g. for this post-registration and/or login scenario)
})(RedirectContext = exports.RedirectContext || (exports.RedirectContext = {}));

},{}],9:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RuntimeMessageTypes = void 0;
var RuntimeMessageTypes;
(function (RuntimeMessageTypes) {
    RuntimeMessageTypes[RuntimeMessageTypes["DataInsightsResults"] = 0] = "DataInsightsResults";
    RuntimeMessageTypes[RuntimeMessageTypes["Activate"] = 1] = "Activate";
    RuntimeMessageTypes[RuntimeMessageTypes["CallBrandServiceFunction"] = 2] = "CallBrandServiceFunction";
    RuntimeMessageTypes[RuntimeMessageTypes["CheckPromoCode"] = 3] = "CheckPromoCode";
    RuntimeMessageTypes[RuntimeMessageTypes["CloseSettings"] = 4] = "CloseSettings";
    RuntimeMessageTypes[RuntimeMessageTypes["ConstructActivateString"] = 5] = "ConstructActivateString";
    RuntimeMessageTypes[RuntimeMessageTypes["ConstructRedirectUrl"] = 6] = "ConstructRedirectUrl";
    RuntimeMessageTypes[RuntimeMessageTypes["ConstructRewardString"] = 7] = "ConstructRewardString";
    RuntimeMessageTypes[RuntimeMessageTypes["DismissActivation"] = 8] = "DismissActivation";
    RuntimeMessageTypes[RuntimeMessageTypes["ExecuteCallback"] = 9] = "ExecuteCallback";
    // TODO BTN-2358 Commenting out for now so we can compare when new refletion is implemented
    // ExecuteReflect,
    // ExecuteReflectCmd,
    RuntimeMessageTypes[RuntimeMessageTypes["FormatClientCurrency"] = 10] = "FormatClientCurrency";
    // TODO BTN-2358 Commenting out for now so we can compare when new refletion is implemented
    // GetAllReflects,
    RuntimeMessageTypes[RuntimeMessageTypes["GetCdnHost"] = 11] = "GetCdnHost";
    RuntimeMessageTypes[RuntimeMessageTypes["GetCurrencySymbol"] = 12] = "GetCurrencySymbol";
    RuntimeMessageTypes[RuntimeMessageTypes["GetFeaturedMerchants"] = 13] = "GetFeaturedMerchants";
    RuntimeMessageTypes[RuntimeMessageTypes["GetFeaturedOfferPlacement"] = 14] = "GetFeaturedOfferPlacement";
    RuntimeMessageTypes[RuntimeMessageTypes["GetFilePath"] = 15] = "GetFilePath";
    RuntimeMessageTypes[RuntimeMessageTypes["GetLocalizedMessage"] = 16] = "GetLocalizedMessage";
    RuntimeMessageTypes[RuntimeMessageTypes["GetPopupData"] = 17] = "GetPopupData";
    RuntimeMessageTypes[RuntimeMessageTypes["GetSerpMerchantMetasByUrls"] = 18] = "GetSerpMerchantMetasByUrls";
    RuntimeMessageTypes[RuntimeMessageTypes["GetStorageItem"] = 19] = "GetStorageItem";
    RuntimeMessageTypes[RuntimeMessageTypes["InjectContent"] = 20] = "InjectContent";
    RuntimeMessageTypes[RuntimeMessageTypes["Log"] = 21] = "Log";
    RuntimeMessageTypes[RuntimeMessageTypes["LogCouponResults"] = 22] = "LogCouponResults";
    RuntimeMessageTypes[RuntimeMessageTypes["LogImpression"] = 23] = "LogImpression";
    RuntimeMessageTypes[RuntimeMessageTypes["Login"] = 24] = "Login";
    RuntimeMessageTypes[RuntimeMessageTypes["NavigateToFeaturedMerchant"] = 25] = "NavigateToFeaturedMerchant";
    RuntimeMessageTypes[RuntimeMessageTypes["NotificationClicked"] = 26] = "NotificationClicked";
    RuntimeMessageTypes[RuntimeMessageTypes["NotificationRemoveClicked"] = 27] = "NotificationRemoveClicked";
    RuntimeMessageTypes[RuntimeMessageTypes["OpenGoTab"] = 28] = "OpenGoTab";
    RuntimeMessageTypes[RuntimeMessageTypes["OpenNewTab"] = 29] = "OpenNewTab";
    RuntimeMessageTypes[RuntimeMessageTypes["OpenProdegeTab"] = 30] = "OpenProdegeTab";
    RuntimeMessageTypes[RuntimeMessageTypes["OpenSettings"] = 31] = "OpenSettings";
    RuntimeMessageTypes[RuntimeMessageTypes["OpenSiteTab"] = 32] = "OpenSiteTab";
    RuntimeMessageTypes[RuntimeMessageTypes["RedeemPromoCode"] = 33] = "RedeemPromoCode";
    RuntimeMessageTypes[RuntimeMessageTypes["RefreshAccountBalance"] = 34] = "RefreshAccountBalance";
    RuntimeMessageTypes[RuntimeMessageTypes["Register"] = 35] = "Register";
    RuntimeMessageTypes[RuntimeMessageTypes["RemoveSurvey"] = 36] = "RemoveSurvey";
    RuntimeMessageTypes[RuntimeMessageTypes["ResetCouponCoolDown"] = 37] = "ResetCouponCoolDown";
    RuntimeMessageTypes[RuntimeMessageTypes["SendDataFromHostToExt"] = 38] = "SendDataFromHostToExt";
    RuntimeMessageTypes[RuntimeMessageTypes["SendPasswordReminder"] = 39] = "SendPasswordReminder";
    RuntimeMessageTypes[RuntimeMessageTypes["SetActivationConfirmed"] = 40] = "SetActivationConfirmed";
    RuntimeMessageTypes[RuntimeMessageTypes["SetActivationInjected"] = 41] = "SetActivationInjected";
    RuntimeMessageTypes[RuntimeMessageTypes["SetStorageItem"] = 42] = "SetStorageItem";
    RuntimeMessageTypes[RuntimeMessageTypes["SetTabShopperMarketingInjected"] = 43] = "SetTabShopperMarketingInjected";
    RuntimeMessageTypes[RuntimeMessageTypes["ShowTutorial"] = 44] = "ShowTutorial";
    RuntimeMessageTypes[RuntimeMessageTypes["UpdateMemberPrefs"] = 45] = "UpdateMemberPrefs";
    RuntimeMessageTypes[RuntimeMessageTypes["UserClickedInPage"] = 46] = "UserClickedInPage";
    RuntimeMessageTypes[RuntimeMessageTypes["GetMagicReceiptsOffers"] = 47] = "GetMagicReceiptsOffers";
})(RuntimeMessageTypes = exports.RuntimeMessageTypes || (exports.RuntimeMessageTypes = {}));

},{}],10:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SliderType = void 0;
var SliderType;
(function (SliderType) {
    SliderType[SliderType["Activation"] = 0] = "Activation";
    SliderType[SliderType["Coupons"] = 1] = "Coupons";
    SliderType[SliderType["Conquest"] = 2] = "Conquest";
    SliderType[SliderType["LostActivation"] = 3] = "LostActivation";
})(SliderType = exports.SliderType || (exports.SliderType = {}));

},{}],11:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UrlTypes = void 0;
var UrlTypes;
(function (UrlTypes) {
    UrlTypes["Merchant"] = "MERCHANT";
    UrlTypes["Checkout"] = "CHECKOUT";
    UrlTypes["Serp"] = "SERP";
})(UrlTypes = exports.UrlTypes || (exports.UrlTypes = {}));

},{}],12:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Constants = void 0;
var Constants = /** @class */ (function () {
    function Constants() {
    }
    Constants.COUPON_SCRIPTS_FOLDER = 'extension-coupon-scripts';
    Constants.DATA_INSIGHTS_FOLDER = 'extension-data-insights';
    Constants.ONE_HOUR_MS = 3600000;
    Constants.ONE_DAY_MS = 86400000;
    Constants.ONE_MIN_MS = 60000;
    Constants.WAIT_INTERVAL = 2000;
    Constants.API_RETRIES = 5;
    Constants.HTTP_RETRIES = 2;
    Constants.ACTIVATION_STATE = 7;
    Constants.TOKEN_COOKIE = '__urqm';
    Constants.TUTORIAL_KEY = 'tutorial-viewed';
    Constants.DEFAULT_REDIRECT_ENDPOINT = '/g/shopredir';
    Constants.JUMP_PAGE_REDIRECT_ENDPOINT = '/jumppage';
    Constants.DISCOVER_CLICK_COMMAND = 'oh-offer-click';
    Constants.DISCOVER_OS3_SB_BASE_URL = 'https://seek.gg/vc/';
    // Does not include QA redirects https://prodege.atlassian.net/wiki/spaces/AMP/pages/6804930570/AdGate+O+O+Integrations#Offer-Wall-Mappings
    Constants.DISCOVER_OS3_SB_REDIRECT_ENDPOINTS = [
        'nqiXr2Y',
        'nqiXr2c',
        'nqiXr2g',
        'nqiXr2o',
        'nqiYqG0', // TADA
    ];
    Constants.FLAGS_STORAGE_KEY = 'flags';
    Constants.IS_MV3 = true;
    Constants.LEGACY_ID_NAMES = {
        SBMP: 'SSE_TBUID',
        TADA: 'guid'
    };
    Constants.EMAIL_REGEX = new RegExp('^(([^<>()\\[\\]\\\\.,;:\\s@"]+(\\.[^<>()\\[\\]\\\\.,;:\\s@"]+)*)|(".+"))@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\])|(([a-zA-Z\\-0-9]+\\.)+[a-zA-Z]{2,}))$');
    return Constants;
}());
exports.Constants = Constants;

},{}],13:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BrandInjectionFactoryBase = void 0;
var BrandInjectionFactoryBase = /** @class */ (function () {
    function BrandInjectionFactoryBase() {
    }
    BrandInjectionFactoryBase.prototype.construct = function (type, params) {
        var injection;
        if (this.map.has(type)) {
            injection = new (this.map.get(type))(params);
        }
        return injection;
    };
    return BrandInjectionFactoryBase;
}());
exports.BrandInjectionFactoryBase = BrandInjectionFactoryBase;

},{}],14:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApplyCouponsLogItem = void 0;
var coupon_log_item_1 = require("./coupon-log-item");
var ApplyCouponsLogItem = /** @class */ (function (_super) {
    __extends(ApplyCouponsLogItem, _super);
    function ApplyCouponsLogItem(data) {
        var _this = _super.call(this, coupon_log_item_1.CouponSliderType.Apply, data) || this;
        _this.couponsErred = 0;
        _this.couponsFailed = 0;
        _this.couponsApplied = 0;
        _this.couponsAttempted = 0;
        _this.couponsSucceeded = 0;
        _this.cartTotalFinal = 0;
        _this.cartTotalInitial = 0;
        _this.cartDiscountCalculated = 0;
        _this.autoApplyActive = data.merchant.couponApplyEnabled ? 1 : 0;
        return _this;
    }
    return ApplyCouponsLogItem;
}(coupon_log_item_1.CouponLogItem));
exports.ApplyCouponsLogItem = ApplyCouponsLogItem;

},{"./coupon-log-item":15}],15:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponLogDetail = exports.CouponSliderType = exports.CouponLogItem = void 0;
var CouponLogItem = /** @class */ (function () {
    function CouponLogItem(sliderType, data) {
        var _this = this;
        var _a, _b, _c;
        this.sliderType = sliderType;
        this.merchantID = data.merchant.id;
        this.checkoutUrl = document.location.href;
        this.couponsAvailable = ((_a = data.merchant.coupons) === null || _a === void 0 ? void 0 : _a.length) || 0;
        this.merchantSessionID = data.merchantSessionID;
        this.trackingCouponDetails = new Map();
        (_c = (_b = data.merchant) === null || _b === void 0 ? void 0 : _b.coupons) === null || _c === void 0 ? void 0 : _c.forEach(function (c) {
            _this.trackingCouponDetails.set(c.code, new CouponLogDetail(c.id));
        });
    }
    return CouponLogItem;
}());
exports.CouponLogItem = CouponLogItem;
var CouponSliderType;
(function (CouponSliderType) {
    CouponSliderType[CouponSliderType["View"] = 1] = "View";
    CouponSliderType[CouponSliderType["Apply"] = 2] = "Apply";
})(CouponSliderType = exports.CouponSliderType || (exports.CouponSliderType = {}));
var CouponLogDetail = /** @class */ (function () {
    function CouponLogDetail(id) {
        this.id = id;
    }
    return CouponLogDetail;
}());
exports.CouponLogDetail = CouponLogDetail;

},{}],16:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewCouponsLogItem = void 0;
var coupon_log_item_1 = require("./coupon-log-item");
var ViewCouponsLogItem = /** @class */ (function (_super) {
    __extends(ViewCouponsLogItem, _super);
    function ViewCouponsLogItem(data) {
        var _this = _super.call(this, coupon_log_item_1.CouponSliderType.View, data) || this;
        _this.couponsCopied = 0;
        return _this;
    }
    return ViewCouponsLogItem;
}(coupon_log_item_1.CouponLogItem));
exports.ViewCouponsLogItem = ViewCouponsLogItem;

},{"./coupon-log-item":15}],17:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RuntimeMessage = void 0;
var RuntimeMessage = /** @class */ (function () {
    function RuntimeMessage(type, value) {
        this.type = type;
        this.value = value;
    }
    return RuntimeMessage;
}());
exports.RuntimeMessage = RuntimeMessage;

},{}],18:[function(require,module,exports){
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DataUtils = void 0;
var dompurify_1 = __importDefault(require("dompurify"));
var DataUtils = /** @class */ (function () {
    function DataUtils() {
    }
    /**
     *
     * @param value The value to check
     * @param type {string} The type to check against, ie. 'string', 'object', 'array', etc.
     * @returns {boolean}
     */
    DataUtils.is = function (value, type) {
        return Object.prototype.toString
            .call(value)
            .slice(this.STRING_LENGTH_TO_REMOVE, this.STRING_END_INDEX)
            .toLowerCase() === type;
    };
    /**
     *
     * @param value The value to check
     * @returns {boolean}
     */
    DataUtils.isNonEmptyObject = function (value) {
        return this.is(value, 'object') && Boolean(Object.keys(value).length);
    };
    /**
     *
     * @param value The value to check
     * @returns {boolean}
     */
    DataUtils.isNonEmptyString = function (value) {
        return this.is(value, 'string') && value !== '';
    };
    DataUtils.getCashBack = function (amount, isPercentage) {
        amount /= 100;
        var result = Number.isInteger(amount) ? amount : amount.toFixed(2);
        return isPercentage ? "".concat(result, "%") : "".concat(result);
    };
    DataUtils.formatCurrencyAmount = function (amount, currency) {
        var formatted;
        if (currency === '€') {
            formatted = "".concat(amount, " ").concat(currency); // 10 €
        }
        else {
            formatted = "".concat(currency).concat(amount); // // $10, £10
        }
        return formatted;
    };
    DataUtils.copyTextToClipboard = function (couponCode) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(couponCode);
        }
        else {
            var el = document.createElement('textarea');
            el.value = couponCode;
            el.style.opacity = '0';
            el.style.position = 'fixed';
            el.style.width = '0';
            el.style.height = '0';
            el.style.margin = '0';
            el.style.padding = '0';
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
        }
    };
    DataUtils.isHTML = function (str) {
        var doc = new DOMParser().parseFromString(str, 'text/html');
        return Array.from(doc.body.childNodes).some(function (node) { return node.nodeType === 1; });
    };
    // Next step is to move individual calls away from !fullSafety, by removing tags from messages.json
    //  and verifying exaclty which PCH injections can have tags
    //  and reduce number of allowed tags.
    DataUtils.getSafeHtml = function (dirty, fullSafety) {
        if (fullSafety === void 0) { fullSafety = true; }
        var allowedTags = [];
        var allowedAttrs = [];
        if (!fullSafety) {
            allowedTags = ['b', 'i', 'em', 'strong', 'a', 'p', 'br'];
            allowedAttrs = ['href', 'target', 'id', 'class'];
        }
        return dompurify_1.default.sanitize(dirty, {
            ALLOWED_TAGS: allowedTags,
            ALLOWED_ATTR: allowedAttrs,
        });
    };
    DataUtils.STRING_LENGTH_TO_REMOVE = 8;
    DataUtils.STRING_END_INDEX = -1;
    return DataUtils;
}());
exports.DataUtils = DataUtils;

},{"dompurify":38}],19:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PromiseUtils = void 0;
var PromiseUtils = /** @class */ (function () {
    function PromiseUtils() {
    }
    PromiseUtils.reject = function (rej, message, reason) {
        console.error(message, reason);
        rej(reason);
    };
    PromiseUtils.waitFor = function (delegate, interval, limit) {
        if (interval === void 0) { interval = 100; }
        if (limit === void 0) { limit = 10; }
        return new Promise(function (res, rej) {
            var tries = 1;
            var wait = function () {
                setTimeout(function () {
                    var result = delegate();
                    if (result !== undefined) {
                        res(result);
                    }
                    else if (tries === limit) {
                        rej('waitFor limit reached.');
                    }
                    else {
                        tries++;
                        wait();
                    }
                }, interval);
            };
            wait();
        });
    };
    return PromiseUtils;
}());
exports.PromiseUtils = PromiseUtils;

},{}],20:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApplyCouponsBase = void 0;
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var runtime_message_1 = require("../../../models/runtime-message");
var coupon_injection_base_1 = require("../coupon-injection-base");
var apply_coupons_log_item_1 = require("../../../models/content-injection/logging/apply-coupons-log-item");
var data_utils_1 = require("../../../utils/data-utils");
var ApplyCouponsBase = /** @class */ (function (_super) {
    __extends(ApplyCouponsBase, _super);
    function ApplyCouponsBase(params) {
        var _this = _super.call(this, params) || this;
        _this.SELECTORS = {
            title: '#title',
            header: '#header',
            footer: '#footer',
            result: '#result',
            progress: '#progress-inner',
            continue: '#continue',
            complete: '#complete',
            container: '#apply-coupons-container',
            processing: '#processing',
            statusText: '#status-text',
            statusCode: '#status-code',
            statusCount: '#status-count',
            applyCoupons: '#apply-coupons'
        };
        _this.HIDDEN_CLASS = 'hidden';
        _this.couponIndex = 0;
        _this.initWorker().then(function () {
            _this.setEventListeners();
            _this.setElements().then(function () {
                _this.couponWorker.process();
            });
        });
        return _this;
    }
    Object.defineProperty(ApplyCouponsBase.prototype, "couponCount", {
        get: function () { return this.data.merchant.coupons.length; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(ApplyCouponsBase.prototype, "statusCountElement", {
        get: function () { return this.getElement(this.SELECTORS.statusCount); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(ApplyCouponsBase.prototype, "titleElement", {
        get: function () { return this.getElement(this.SELECTORS.title); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(ApplyCouponsBase.prototype, "headerElement", {
        get: function () { return this.getElement(this.SELECTORS.header); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(ApplyCouponsBase.prototype, "footerElement", {
        get: function () { return this.getElement(this.SELECTORS.footer); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(ApplyCouponsBase.prototype, "continueElement", {
        get: function () { return this.getElement(this.SELECTORS.continue); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(ApplyCouponsBase.prototype, "headerImageElement", {
        get: function () { return this.headerElement.querySelector('img'); },
        enumerable: false,
        configurable: true
    });
    ApplyCouponsBase.prototype.initWorker = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = this;
                        return [4 /*yield*/, this.waitForWindowInstance('CouponWorker')];
                    case 1:
                        _a.couponWorker = _b.sent();
                        this.logItem.merchantScriptWorkerType = this.couponWorker.testerType;
                        if (this.couponWorker.isJson) {
                            this.logItem.merchantScriptActive = 1;
                        }
                        else {
                            this.logItem.merchantScriptActive = this.data.merchant.hasMerchantScript ? 1 : 0;
                        }
                        this.data.merchant.coupons = this.couponWorker.dedupeCoupons();
                        this.logItem.couponsAvailable = this.data.merchant.coupons.length;
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.setElements = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setHeader()];
                    case 1:
                        _a.sent();
                        return [4 /*yield*/, this.setTitle(this.titleElement)];
                    case 2:
                        _a.sent();
                        return [4 /*yield*/, this.setStatusText(this.getElement(this.SELECTORS.statusText))];
                    case 3:
                        _a.sent();
                        return [4 /*yield*/, this.setFooter(this.footerElement)];
                    case 4:
                        _a.sent();
                        return [4 /*yield*/, this.setX()];
                    case 5:
                        _a.sent();
                        this.setDismissClicks();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.setHeader = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                this.headerElement.appendChild(this.createElement('img', function (img) { return __awaiter(_this, void 0, void 0, function () {
                    var _a;
                    return __generator(this, function (_b) {
                        switch (_b.label) {
                            case 0:
                                _a = img;
                                return [4 /*yield*/, this.getHeaderImage()];
                            case 1:
                                _a.src = _b.sent();
                                return [2 /*return*/];
                        }
                    });
                }); }));
                return [2 /*return*/];
            });
        });
    };
    ApplyCouponsBase.prototype.addTitleTestingCodesText = function (title) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                title.appendChild(this.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                    var _a;
                    return __generator(this, function (_b) {
                        switch (_b.label) {
                            case 0:
                                _a = div;
                                return [4 /*yield*/, this.getLocalizedString('testingCouponCodes')];
                            case 1:
                                _a.innerText = _b.sent();
                                return [2 /*return*/];
                        }
                    });
                }); }));
                return [2 /*return*/];
            });
        });
    };
    ApplyCouponsBase.prototype.addTitleTestingCodesDescriptionText = function (title) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                title.appendChild(this.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                    var _a, _b, _c;
                    return __generator(this, function (_d) {
                        switch (_d.label) {
                            case 0:
                                div.id = 'testing-codes-desc';
                                _a = div;
                                _c = (_b = data_utils_1.DataUtils).getSafeHtml;
                                return [4 /*yield*/, this.getLocalizedString('testingCouponCodesSaveMoney')];
                            case 1:
                                _a.innerHTML = _c.apply(_b, [_d.sent(), false]);
                                return [2 /*return*/];
                        }
                    });
                }); }));
                return [2 /*return*/];
            });
        });
    };
    ApplyCouponsBase.prototype.setStatusTextApplying = function (statusText) {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = statusText;
                        return [4 /*yield*/, this.getLocalizedString('applyingCouponsPurchase')];
                    case 1:
                        _a.innerText = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.setStatusCountText = function (statusCount) {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = statusCount;
                        return [4 /*yield*/, this.getLocalizedString('applyingCouponsCount', this.couponIndex.toString(), this.couponCount.toString())];
                    case 1:
                        _a.innerText = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.addFooterImage = function (footer, image) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                footer.appendChild(this.createElement('img', function (img) {
                    img.src = image;
                }));
                return [2 /*return*/];
            });
        });
    };
    ApplyCouponsBase.prototype.setEventListeners = function () {
        var _this = this;
        this.couponWorker.onInitialTotal = function (detail) { _this.setInitialTotal(detail); };
        this.couponWorker.onStartProcessCoupon = function (detail) { _this.startProcessCoupon(detail); };
        this.couponWorker.onSaveCouponResult = function (detail) { _this.saveCouponResult(detail); };
        this.couponWorker.onCompleted = function (detail) { _this.onCompleted(detail); };
        this.couponWorker.onCouponInjectionError = function (detail) { _this.onCouponInjectionError(detail); };
    };
    ApplyCouponsBase.prototype.setInitialTotal = function (detail) {
        this.logItem.cartTotalInitial = this.formatCurrencyForLog(detail.total);
    };
    ApplyCouponsBase.prototype.startProcessCoupon = function (detail) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        this.logItem.sliderClicked = 1;
                        this.couponIndex++;
                        return [4 /*yield*/, this.updateProgress()];
                    case 1:
                        _a.sent();
                        document.dispatchEvent(new CustomEvent('coupon-attempted'));
                        this.setStatusCode(this.getElement(this.SELECTORS.statusCode), detail.coupon);
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.updateProgress = function () {
        return __awaiter(this, void 0, void 0, function () {
            var percent;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        percent = (this.couponIndex / this.couponCount) * 100;
                        this.getElement(this.SELECTORS.progress).style.width = "".concat(percent, "%");
                        return [4 /*yield*/, this.setStatusCount(this.statusCountElement)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.saveCouponResult = function (detail) {
        var logDetail = this.logItem.trackingCouponDetails.get(detail.couponCode);
        logDetail.attempted = 1;
        this.logItem.couponsAttempted++;
        logDetail.savings = this.formatCurrencyForLog(detail.savings);
        logDetail.cartTotal = this.formatCurrencyForLog(detail.total);
        switch (detail.message) {
            case 'failure':
                logDetail.failed = detail.savings ? 0 : 1;
                this.logItem.couponsFailed++;
                break;
            case 'success':
                logDetail.succeeded = detail.savings ? 1 : 0;
                this.logItem.couponsSucceeded++;
                break;
            default:
                logDetail.erred = 1;
                this.logItem.couponsErred++;
                break;
        }
        this.logItem.trackingCouponDetails.set(detail.couponCode, logDetail);
    };
    ApplyCouponsBase.prototype.onCompleted = function (detail) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.logItem.cartDiscountCalculated = this.formatCurrencyForLog(detail.amount);
                this.calculateFinalTotal(detail.total);
                this.logCouponApplied(detail.couponCode, detail.couponCodes);
                if (detail.shouldRefresh) {
                    this.shouldRefreshAfterContinueToCheckout = true;
                }
                this.trySendLog();
                this.showCompletedUI(detail);
                this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.ResetCouponCoolDown, this.data.tabId));
                return [2 /*return*/];
            });
        });
    };
    ApplyCouponsBase.prototype.calculateFinalTotal = function (total) {
        if (total && total > 0) {
            this.logItem.cartTotalFinal = this.formatCurrencyForLog(total);
        }
        else {
            // api merchants might not have final coupon applied yet, need to loop through object and find lowest cartTotal
            this.logItem.cartTotalFinal = Array.from(this.logItem.trackingCouponDetails.values())
                .map(function (e) { return e.cartTotal; })
                .sort()[0];
        }
    };
    ApplyCouponsBase.prototype.logCouponApplied = function (couponCode, couponCodes) {
        var _this = this;
        var setApplied = function (code) {
            var detail = _this.logItem.trackingCouponDetails.get(code);
            detail.applied = 1;
            _this.logItem.trackingCouponDetails.set(code, detail);
        };
        // if there is a couponcode, then we know that it applied the coupon, and we need to update the applied for that coupon.
        // stackable and more than one code worked. Only can happen with Stackable
        if (couponCodes) {
            couponCodes.forEach(function (code) {
                setApplied(code);
                _this.logItem.couponsApplied++;
            });
        }
        else if (couponCode) {
            setApplied(couponCode);
            this.logItem.couponsApplied = 1;
        }
    };
    ApplyCouponsBase.prototype.showCompletedUI = function (detail) {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.getElement(this.SELECTORS.processing).classList.add(this.HIDDEN_CLASS);
                        return [4 /*yield*/, this.showResult(this.getElement(this.SELECTORS.result), detail)];
                    case 1:
                        _b.sent();
                        _a = this.continueElement;
                        return [4 /*yield*/, this.getLocalizedString('continueToCheckout')];
                    case 2:
                        _a.innerText = _b.sent();
                        this.continueElement.onclick = function () { _this.continueToCheckout(); };
                        this.getElement(this.SELECTORS.complete).classList.remove(this.HIDDEN_CLASS);
                        return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.continueToCheckout = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        this.hide();
                        if (!this.shouldRefreshAfterContinueToCheckout) return [3 /*break*/, 4];
                        //reset cooldown in case user let Continue Checkout sit for awhile before clicking, since we are getting ready to reload for api merchant
                        return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.ResetCouponCoolDown, this.data.tabId))];
                    case 1:
                        //reset cooldown in case user let Continue Checkout sit for awhile before clicking, since we are getting ready to reload for api merchant
                        _a.sent();
                        // Don't show activation slider after reloading no matter the tab is activated or not. We have already tried activation
                        // Activated (Activation succeeded before applying coupons) OR Not Activated (Activation failed before applying coupons)
                        return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.SetActivationInjected, { tabId: this.data.tabId }))];
                    case 2:
                        // Don't show activation slider after reloading no matter the tab is activated or not. We have already tried activation
                        // Activated (Activation succeeded before applying coupons) OR Not Activated (Activation failed before applying coupons)
                        _a.sent();
                        // Activated
                        return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.SetActivationConfirmed, { tabId: this.data.tabId }))];
                    case 3:
                        // Activated
                        _a.sent();
                        document.location.reload();
                        _a.label = 4;
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.onCouponInjectionError = function (detail) {
        this.logItem.trackingCouponDetails.set('errors', {
            extCode: detail.extCode,
            message: detail.message
        });
    };
    ApplyCouponsBase.prototype.getContentInjectionImagePath = function (file) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getExtensionFilePath("assets/images/coupon-injection/".concat(file))];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    ApplyCouponsBase.prototype.dismiss = function () {
        this.hide();
    };
    ApplyCouponsBase.prototype.hide = function () {
        this.getElement(this.SELECTORS.container).classList.add(this.HIDDEN_CLASS);
    };
    ApplyCouponsBase.prototype.constructLogItem = function () {
        return new apply_coupons_log_item_1.ApplyCouponsLogItem(this.data);
    };
    ApplyCouponsBase.prototype.onInteraction = function (detail) {
        throw 'Apply coupons is automatic. There is no onInteraction implementation.';
    };
    ApplyCouponsBase.prototype.onUIConstructed = function () {
        throw new Error('Method not implemented.');
    };
    return ApplyCouponsBase;
}(coupon_injection_base_1.CouponInjectionBase));
exports.ApplyCouponsBase = ApplyCouponsBase;

},{"../../../enums/runtime-message-types":9,"../../../models/content-injection/logging/apply-coupons-log-item":14,"../../../models/runtime-message":17,"../../../utils/data-utils":18,"../coupon-injection-base":23}],21:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConquestBase = void 0;
var content_injection_type_1 = require("../../../enums/content-injection-type");
var redirect_context_1 = require("../../../enums/redirect-context");
var slider_all_base_1 = require("../slider-all-base");
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var runtime_message_1 = require("../../../models/runtime-message");
var ConquestBase = /** @class */ (function (_super) {
    __extends(ConquestBase, _super);
    function ConquestBase(params) {
        var _this = _super.call(this, params) || this;
        _this.REWARDS_ACTIVATED = 'rewards-activated';
        _this.SELECTORS = {
            cta: '#cta',
            and: '#and',
            logo: '#logo',
            slider: '#slider',
            dismiss: '.dismiss',
            dismissLink: '#footer .dismiss',
            secondaryContent: '#secondary-content',
            conquest: '#conquest',
            conquestImage: '#conquest-image',
            copyText: '.copy-text',
        };
        _this.HIDDEN_CLASS = 'hidden';
        _this.setElements();
        return _this;
    }
    // based on Biz rules. No need for creating a CTA (use offer copy text instead), no terms, activated, custom coupon text
    ConquestBase.prototype.setElements = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setLogo()];
                    case 1:
                        _a.sent();
                        return [4 /*yield*/, this.setConquestImage()];
                    case 2:
                        _a.sent();
                        return [4 /*yield*/, this.setCopyText()];
                    case 3:
                        _a.sent();
                        return [4 /*yield*/, this.setCTA()];
                    case 4:
                        _a.sent();
                        return [4 /*yield*/, this.setDismiss()];
                    case 5:
                        _a.sent();
                        this.show();
                        this.onUIConstructed();
                        return [2 /*return*/];
                }
            });
        });
    };
    ConquestBase.prototype.setConquestImage = function () {
        var _this = this;
        var _a, _b;
        if ((_b = (_a = this.data.merchant) === null || _a === void 0 ? void 0 : _a.placement) === null || _b === void 0 ? void 0 : _b.image) {
            var conquestImg = this.getElement(this.SELECTORS.conquestImage);
            conquestImg.src = this.data.merchant.placement.image;
            conquestImg.addEventListener('click', function () {
                _this.onInteraction();
            });
        }
        else {
            var conquest = this.getElement(this.SELECTORS.conquest);
            conquest.classList.add(this.HIDDEN_CLASS);
            var copyText = this.getElement(this.SELECTORS.copyText);
            copyText.classList.add('copy-text-no-img');
        }
    };
    ConquestBase.prototype.setCopyText = function () {
        var _a, _b;
        return __awaiter(this, void 0, void 0, function () {
            var copyText;
            return __generator(this, function (_c) {
                copyText = this.getElement(this.SELECTORS.copyText);
                if ((_b = (_a = this.data.merchant) === null || _a === void 0 ? void 0 : _a.placement) === null || _b === void 0 ? void 0 : _b.copyText) {
                    copyText.textContent = this.data.merchant.placement.copyText;
                }
                return [2 /*return*/];
            });
        });
    };
    ConquestBase.prototype.setLogo = function () {
        return __awaiter(this, void 0, void 0, function () {
            var img, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        img = this.getElement(this.SELECTORS.logo);
                        img.onerror = function () { img.parentElement.remove(); };
                        _a = img;
                        return [4 /*yield*/, this.getImageFilePath('logo-dark.svg')];
                    case 1:
                        _a.src = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ConquestBase.prototype.setCTA = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setCTAText()];
                    case 1:
                        _a.sent();
                        this.cta.onclick = function () {
                            _this.onInteraction();
                        };
                        return [2 /*return*/];
                }
            });
        });
    };
    ConquestBase.prototype.setCTAText = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.cta.innerText = "Shop Now";
                return [2 /*return*/];
            });
        });
    };
    ConquestBase.prototype.setDismiss = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.setXClose();
                        _a = this.getElement(this.SELECTORS.dismissLink);
                        return [4 /*yield*/, this.getLocalizedString('remindMeLater')];
                    case 1:
                        _a.innerText = _b.sent();
                        this.getElements(this.SELECTORS.dismiss).forEach(function (a) {
                            a.onclick = function () { _this.dismiss(); };
                        });
                        return [2 /*return*/];
                }
            });
        });
    };
    ConquestBase.prototype.setXClose = function () {
        return __awaiter(this, void 0, void 0, function () {
            var xClose, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        xClose = this.getElement(this.BASE_SELECTORS.x).querySelector('img');
                        _a = xClose;
                        return [4 /*yield*/, this.getExtensionFilePath('assets/images/conquest-close.svg')];
                    case 1:
                        _a.src = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ConquestBase.prototype.onInteraction = function (redirectContext) {
        var _this = this;
        var _a, _b, _c;
        if (redirectContext === void 0) { redirectContext = redirect_context_1.RedirectContext.Default; }
        if ((_c = (_b = (_a = this.data) === null || _a === void 0 ? void 0 : _a.merchant) === null || _b === void 0 ? void 0 : _b.placement) === null || _c === void 0 ? void 0 : _c.clickUrl) {
            this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.OpenNewTab, { "url": this.data.merchant.placement.clickUrl }));
        }
        else {
            if (!this.data.activated) {
                this.activate(redirectContext);
            }
        }
        setTimeout(function () {
            _this.hide();
        }, 500);
    };
    return ConquestBase;
}(slider_all_base_1.SliderAllBase));
exports.ConquestBase = ConquestBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.Conquest)] = ConquestBase;

},{"../../../enums/content-injection-type":5,"../../../enums/redirect-context":8,"../../../enums/runtime-message-types":9,"../../../models/runtime-message":17,"../slider-all-base":34}],22:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContentInjectionBase = void 0;
var clients_1 = require("../../enums/clients");
var log_levels_1 = require("../../enums/log-levels");
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var runtime_message_1 = require("../../models/runtime-message");
var ContentInjectionBase = /** @class */ (function () {
    function ContentInjectionBase(params) {
        var _a;
        this.showDebugging = false; // leave false normally, flip to true to see logs when debugging.
        this.data = params.data;
        this.extensionRuntimeId = params.extensionRuntimeId;
        if (((_a = params.data) === null || _a === void 0 ? void 0 : _a.consoleLogLevel) >= log_levels_1.ConsoleLogLevels.Debug) {
            this.showDebugging = true;
        }
    }
    Object.defineProperty(ContentInjectionBase.prototype, "clientName", {
        get: function () {
            return clients_1.Clients[this.data.client];
        },
        enumerable: false,
        configurable: true
    });
    ContentInjectionBase.prototype.createElement = function (tag, fn) {
        var el = document.createElement(tag);
        if (fn) {
            fn(el);
        }
        return el;
    };
    ContentInjectionBase.prototype.getExtensionFilePath = function (relativePath) {
        return __awaiter(this, void 0, void 0, function () {
            var message;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        message = new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.GetFilePath, relativePath);
                        return [4 /*yield*/, this.sendExtensionMessage(message)];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    ContentInjectionBase.prototype.sendExtensionMessage = function (message) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                // Before sending message, do a runtime.connect (Like a ping) to wake up the SW first, just in case it is inactive/asleep.    
                return [2 /*return*/, new Promise(function (resolve) { return __awaiter(_this, void 0, void 0, function () {
                        var port, disconnectCallback;
                        var _this = this;
                        return __generator(this, function (_a) {
                            switch (_a.label) {
                                case 0: return [4 /*yield*/, window['browserApi'].runtime.connect()];
                                case 1:
                                    port = _a.sent();
                                    disconnectCallback = function () { return _this.handleDisconnect(message, resolve); };
                                    port.onDisconnect.addListener(disconnectCallback);
                                    return [2 /*return*/];
                            }
                        });
                    }); })];
            });
        });
    };
    ContentInjectionBase.prototype.handleDisconnect = function (message, resolve) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.onDisconnectSendExtensionMessage(message)];
                    case 1:
                        response = _a.sent();
                        resolve(response);
                        return [2 /*return*/];
                }
            });
        });
    };
    ContentInjectionBase.prototype.onDisconnectSendExtensionMessage = function (message) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        var cb = function (response) {
                            resolve(response);
                        };
                        window['browserApi'].runtime.sendMessage(_this.extensionRuntimeId, message, {}, cb);
                    })];
            });
        });
    };
    // Debug output will go to the clientPage/browser debugger and not the extension/background debugger
    ContentInjectionBase.prototype.log = function (message, data) {
        var consoleArgs = ['*CI', message]; // prifix makes it easier to filter
        if (this.showDebugging) {
            if (data) {
                // Errors/Exception come through as plain object (so you can't check typeof), but Errors don't stringify, have to make an object.
                if (data.message && data.stack) {
                    data = { error: data.message, stack: data.stack };
                }
                consoleArgs.push(JSON.stringify(data, null, 2));
            }
            console.log.apply(null, consoleArgs);
        }
    };
    ContentInjectionBase.prototype.constructMerchantCtaString = function (merchant, activated, type, isShort) {
        if (isShort === void 0) { isShort = false; }
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(type, {
                        reward: merchant.reward,
                        clientId: this.data.client,
                        locationId: merchant.loc,
                        isShort: isShort,
                        activated: activated
                    }))];
            });
        });
    };
    return ContentInjectionBase;
}());
exports.ContentInjectionBase = ContentInjectionBase;

},{"../../enums/clients":4,"../../enums/log-levels":6,"../../enums/runtime-message-types":9,"../../models/runtime-message":17}],23:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponInjectionBase = void 0;
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var runtime_message_1 = require("../../models/runtime-message");
var merchant_injection_base_1 = require("./merchant-injection-base");
var CouponInjectionBase = /** @class */ (function (_super) {
    __extends(CouponInjectionBase, _super);
    function CouponInjectionBase(params) {
        var _this = _super.call(this, params) || this;
        _this.initLogging();
        return _this;
    }
    CouponInjectionBase.prototype.initLogging = function () {
        var _this = this;
        this.logItem = this.constructLogItem();
        window.addEventListener('beforeunload', function () { _this.trySendLog(); });
        window.addEventListener('close', function () { _this.trySendLog(); });
    };
    CouponInjectionBase.prototype.trySendLog = function () {
        // change details from map to object for posting log to db
        var couponDetails = JSON.stringify(Object.fromEntries(this.logItem.trackingCouponDetails));
        this.logItem.couponDetails = couponDetails;
        if (!this.logSent) {
            this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.LogCouponResults, this.logItem));
            this.logSent = true;
        }
    };
    CouponInjectionBase.prototype.formatCurrencyForLog = function (val) {
        if (val) {
            return Math.floor(val * 100);
        }
        else {
            return 0;
        }
    };
    return CouponInjectionBase;
}(merchant_injection_base_1.MerchantInjectionBase));
exports.CouponInjectionBase = CouponInjectionBase;

},{"../../enums/runtime-message-types":9,"../../models/runtime-message":17,"./merchant-injection-base":31}],24:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponWorkerBase = void 0;
var content_injection_type_1 = require("../../enums/content-injection-type");
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var runtime_message_1 = require("../../models/runtime-message");
var content_injection_base_1 = require("./content-injection-base");
var CouponWorkerBase = /** @class */ (function (_super) {
    __extends(CouponWorkerBase, _super);
    function CouponWorkerBase(params) {
        var _this = _super.call(this, params) || this;
        _this._initialElementsCheckPassed = false;
        _this._initialElementsCheckFailed = false;
        _this.couponCodes = [];
        _this.emptyFn = function () { };
        _this.onInitialTotal = _this.emptyFn;
        _this.onStartProcessCoupon = _this.emptyFn;
        _this.onSaveCouponResult = _this.emptyFn;
        _this.onCompleted = _this.emptyFn;
        _this.onCouponInjectionError = _this.emptyFn;
        _this.setEventListeners();
        _this.initWorker();
        return _this;
    }
    Object.defineProperty(CouponWorkerBase.prototype, "isJson", {
        get: function () { return this._isJson; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CouponWorkerBase.prototype, "testerType", {
        get: function () { return this._testerType; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CouponWorkerBase.prototype, "initialElementsCheckPassed", {
        get: function () { return this._initialElementsCheckPassed; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CouponWorkerBase.prototype, "initialElementsCheckFailed", {
        get: function () { return this._initialElementsCheckFailed; },
        enumerable: false,
        configurable: true
    });
    CouponWorkerBase.prototype.setEventListeners = function () {
        var _this = this;
        var set = function (type, fn) {
            document.addEventListener(type, function (e) {
                if (e.detail.extCode === _this.data.client) {
                    fn(e.detail);
                }
            });
        };
        set('initialElementsChecked', function (detail) {
            _this.log('Initial elements checked', detail);
            _this.onInitialElementsChecked(detail);
        });
        set('initialTotal', function (detail) {
            _this.log('Initial total:', detail);
            _this.onInitialTotal(detail);
        });
        set('startProcessCoupon', function (detail) {
            _this.log('Start process coupon', detail);
            _this.onStartProcessCoupon(detail);
        });
        set('saveCouponResult', function (detail) {
            _this.log('Save coupon result', detail);
            _this.onSaveCouponResult(detail);
        });
        set('showFinalResult', function (detail) {
            _this.log('Show final result', detail);
            _this.onCompleted(detail);
        });
        set('couponInjectionError', function (detail) {
            _this.log('Coupon injection error', detail);
            _this.onCouponInjectionError(detail);
        });
        set('logMerchantPageError', function (detail) {
            _this.log('C@C merchant script error', detail.errorMessage);
            if (detail.type === 'loudFail') {
                _this.onCompleted({ success: false, total: null, amount: null, couponCode: null, couponCodes: null, shouldRefresh: null });
            }
        });
    };
    CouponWorkerBase.prototype.onInitialElementsChecked = function (detail) {
        this._initialElementsCheckPassed = detail.passed;
        if (!detail.passed && this.data.jsonMerchantDefinition && this.data.merchant.hasMerchantScript && this.data.merchant.couponApplyEnabled && this.data.merchant.coupons) {
            this._initialElementsCheckFailed = !detail.passed;
        }
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.InjectContent, {
            data: this.data,
            tabId: this.data.tabId,
            type: content_injection_type_1.ContentInjectionType.Slider
        }));
    };
    CouponWorkerBase.prototype.initWorker = function () {
        this._isJson = !!this.data.jsonMerchantDefinition;
        window['CouponInjection'].testedCoupons = [];
        if (this.isJson) {
            this.log('CouponSliderBase is workertype = JSON');
            this._testerType = window['CouponInjection'].WORKER_TYPE_JSON;
            this.couponWorker = new Prdg.CouponInjection.JsonCouponWorker(this.data.jsonMerchantDefinition, this.extensionRuntimeId, this.data.client);
            this.couponWorker.checkInitialElementsJson();
        }
        else {
            var merchantWorker = new CouponMerchantWorker();
            merchantWorker.init($, function () { });
            //this creates couponWorker and kicks off checkInitialState which fires event initialElementsChecked    
            this.couponWorker = Prdg.CouponInjection.CouponWorkerFactory.construct(merchantWorker, this.extensionRuntimeId, this.data.client, Prdg.CouponInjection.elementIds, Prdg.CouponInjection.customFuncs);
            this._testerType = this.couponWorker.merchantWorker.testerType;
            this.log("CouponSliderBase is Not Json. It is workertype : ".concat(this.couponWorker.merchantWorker.testerType));
        }
        // Setting these because the non-JSON merchant "inheritance" pattern needs them
        if (typeof CouponMerchantWorker !== 'undefined') {
            var set = function (self, prop) {
                CouponMerchantWorker.prototype[prop] = self.couponWorker[prop];
                merchantWorker[prop] = merchantWorker[prop] || self.couponWorker[prop];
            };
            set(this, 'pollTimeoutCounter');
            set(this, 'pollInterval');
            set(this, 'waitFor');
            set(this, 'waitForRemoveCoupon');
            set(this, 'triggerEvent');
            set(this, 'setReactCouponCode');
            set(this, 'waitForApplyPromoCode');
            set(this, 'calculateTotalAsync');
            set(this, 'calculateTotal');
            set(this, 'getFirstVisible');
            set(this, 'getFirst');
            merchantWorker.elementIds = merchantWorker.elementIds || Prdg.CouponInjection.elementIds;
            merchantWorker.customFuncs = merchantWorker.customFuncs || Prdg.CouponInjection.customFuncs;
        }
    };
    CouponWorkerBase.prototype.dedupeCoupons = function () {
        var _this = this;
        var _a;
        var coupons = [];
        this.couponCodes = [];
        (_a = this.data.merchant.coupons) === null || _a === void 0 ? void 0 : _a.forEach(function (coupon) {
            var code = coupon.code;
            if (!_this.couponCodes.some(function (c) { return c === code; })) {
                _this.couponCodes.push(code);
                coupons.push(coupon);
            }
        });
        return coupons;
    };
    CouponWorkerBase.prototype.process = function () {
        this.couponWorker.process(this.couponCodes);
    };
    return CouponWorkerBase;
}(content_injection_base_1.ContentInjectionBase));
exports.CouponWorkerBase = CouponWorkerBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.CouponWorker)] = CouponWorkerBase;

},{"../../enums/content-injection-type":5,"../../enums/runtime-message-types":9,"../../models/runtime-message":17,"./content-injection-base":22}],25:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExtInstalledMessengerBase = void 0;
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var runtime_message_1 = require("../../models/runtime-message");
var host_messenger_base_1 = require("./host-messenger-base");
var content_injection_type_1 = require("../../enums/content-injection-type");
// ExtensionPresent
var ExtInstalledMessengerBase = /** @class */ (function (_super) {
    __extends(ExtInstalledMessengerBase, _super);
    function ExtInstalledMessengerBase(params) {
        var _this = _super.call(this, params, 'ExtensionInstalled') || this;
        _this.addInstalledListener();
        return _this;
    }
    ExtInstalledMessengerBase.prototype.addInstalledListener = function () {
        var _this = this;
        window.addEventListener('message', function (evt) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!(evt.source !== window && ['cmpData', 'refData'].includes(evt.data.messageType))) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.sendDataFromHostToExt(evt.data)];
                    case 1:
                        _a.sent();
                        _a.label = 2;
                    case 2: return [2 /*return*/];
                }
            });
        }); });
    };
    ExtInstalledMessengerBase.prototype.sendDataFromHostToExt = function (data) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.SendDataFromHostToExt, data))];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    return ExtInstalledMessengerBase;
}(host_messenger_base_1.HostMessengerBase));
exports.ExtInstalledMessengerBase = ExtInstalledMessengerBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.ExtInstalledMessenger)] = ExtInstalledMessengerBase;

},{"../../enums/content-injection-type":5,"../../enums/runtime-message-types":9,"../../models/runtime-message":17,"./host-messenger-base":27}],26:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExtPresentMessengerBase = void 0;
var host_messenger_base_1 = require("./host-messenger-base");
var content_injection_type_1 = require("../../enums/content-injection-type");
// ExtensionPresent
var ExtPresentMessengerBase = /** @class */ (function (_super) {
    __extends(ExtPresentMessengerBase, _super);
    function ExtPresentMessengerBase(params) {
        return _super.call(this, params, 'ExtensionPresent') || this;
    }
    return ExtPresentMessengerBase;
}(host_messenger_base_1.HostMessengerBase));
exports.ExtPresentMessengerBase = ExtPresentMessengerBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.ExtPresentMessenger)] = ExtPresentMessengerBase;

},{"../../enums/content-injection-type":5,"./host-messenger-base":27}],27:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.HostMessengerEvent = exports.HostMessengerBase = void 0;
var clients_1 = require("../../enums/clients");
var content_injection_base_1 = require("./content-injection-base");
var content_injection_type_1 = require("../../enums/content-injection-type");
var HostMessengerBase = /** @class */ (function (_super) {
    __extends(HostMessengerBase, _super);
    function HostMessengerBase(params, type) {
        var _this = _super.call(this, params) || this;
        _this.type = type;
        _this.dispatchEvent();
        return _this;
    }
    HostMessengerBase.prototype.dispatchEvent = function () {
        var evt = "".concat(clients_1.Clients[this.data.client]).concat(this.type);
        document.dispatchEvent(new Event(evt));
    };
    return HostMessengerBase;
}(content_injection_base_1.ContentInjectionBase));
exports.HostMessengerBase = HostMessengerBase;
var HostMessengerEvent = /** @class */ (function () {
    function HostMessengerEvent() {
    }
    return HostMessengerEvent;
}());
exports.HostMessengerEvent = HostMessengerEvent;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.ExtPresentMessenger)] = HostMessengerBase;

},{"../../enums/clients":4,"../../enums/content-injection-type":5,"./content-injection-base":22}],28:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.InlineRegistration = void 0;
var redirect_context_1 = require("../../../enums/redirect-context");
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var runtime_message_1 = require("../../../models/runtime-message");
var merchant_injection_base_1 = require("../merchant-injection-base");
var data_utils_1 = require("../../../utils/data-utils");
var InlineRegistration = /** @class */ (function (_super) {
    __extends(InlineRegistration, _super);
    function InlineRegistration(params) {
        var _this = _super.call(this, params) || this;
        _this.SELECTORS = {
            FORM: '#reg form',
            INPUT: '#reg form input',
            STATUS: '#reg-status',
            BUTTON: '#reg form button',
            INLINE_REG: '#reg',
            REG_REWARD: '#reg-reward'
        };
        _this.setStyle();
        _this.addUI();
        return _this;
    }
    Object.defineProperty(InlineRegistration.prototype, "input", {
        get: function () { return this.getElement(this.SELECTORS.INPUT); },
        enumerable: false,
        configurable: true
    });
    InlineRegistration.prototype.fetchFile = function (path) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, fetch(path)];
                    case 1:
                        response = _a.sent();
                        return [4 /*yield*/, response.text()];
                    case 2: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    InlineRegistration.prototype.setStyle = function () {
        return __awaiter(this, void 0, void 0, function () {
            var path, css;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getExtensionFilePath('worker/injections/inline-registration.css')];
                    case 1:
                        path = _a.sent();
                        return [4 /*yield*/, this.fetchFile(path)];
                    case 2:
                        css = _a.sent();
                        this.getElement('style').innerHTML = css;
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.addUI = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setContent()];
                    case 1:
                        _a.sent();
                        return [4 /*yield*/, this.setContainer()];
                    case 2:
                        _a.sent();
                        return [4 /*yield*/, this.setReward()];
                    case 3:
                        _a.sent();
                        return [4 /*yield*/, this.setForm()];
                    case 4:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.setContent = function () {
        return __awaiter(this, void 0, void 0, function () {
            var path, html;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getExtensionFilePath('worker/injections/inline-registration.html')];
                    case 1:
                        path = _a.sent();
                        return [4 /*yield*/, this.fetchFile(path)];
                    case 2:
                        html = _a.sent();
                        this.injectionContainer.innerHTML = html;
                        this.injectionContainer.classList.add('reg-container', this.clientName);
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.setContainer = function () {
        return __awaiter(this, void 0, void 0, function () {
            var container, background;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        container = this.getElement(this.SELECTORS.INLINE_REG);
                        return [4 /*yield*/, this.getImageFilePath('bg_coupons_join_cta.png')];
                    case 1:
                        background = _a.sent();
                        container.style.background = "url(".concat(background, ")");
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.setReward = function () {
        return __awaiter(this, void 0, void 0, function () {
            var reward;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.constructCtaString(runtime_message_types_1.RuntimeMessageTypes.ConstructRewardString)];
                    case 1:
                        reward = _a.sent();
                        if (reward) {
                            // TODO: another string construction thing.
                            this.getElement(this.SELECTORS.REG_REWARD).innerHTML = data_utils_1.DataUtils.getSafeHtml("Get ".concat(reward), false);
                        }
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.setForm = function () {
        return __awaiter(this, void 0, void 0, function () {
            var form, _a, _b;
            var _this = this;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        form = this.getElement(this.SELECTORS.FORM);
                        form.onsubmit = function (e) { _this.onInteraction(e); };
                        _a = this.getElement(this.SELECTORS.BUTTON);
                        return [4 /*yield*/, this.getLocalizedString('joinBtnLabel')];
                    case 1:
                        _a.innerHTML = _c.sent();
                        _b = this.input;
                        return [4 /*yield*/, this.getLocalizedString('joinEmailPlaceholder')];
                    case 2:
                        _b.placeholder = _c.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.onInteraction = function (detail) {
        return __awaiter(this, void 0, void 0, function () {
            var e, status, email, response, _a;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        e = detail;
                        e.preventDefault();
                        status = this.getElement(this.SELECTORS.STATUS);
                        email = this.input.value;
                        return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.Register, { email: email }))];
                    case 1:
                        response = _b.sent();
                        if (!(response === null || response === void 0 ? void 0 : response.data)) return [3 /*break*/, 3];
                        status.innerHTML = '';
                        status.classList.add('success');
                        status.appendChild(this.createElement('b', function (b) { return __awaiter(_this, void 0, void 0, function () {
                            var _a;
                            return __generator(this, function (_b) {
                                switch (_b.label) {
                                    case 0:
                                        _a = b;
                                        return [4 /*yield*/, this.getLocalizedString('regConfirmHeadline')];
                                    case 1:
                                        _a.innerHTML = _b.sent();
                                        return [2 /*return*/];
                                }
                            });
                        }); }));
                        status.appendChild(this.createElement('span', function (span) { return __awaiter(_this, void 0, void 0, function () {
                            var _a;
                            return __generator(this, function (_b) {
                                switch (_b.label) {
                                    case 0:
                                        _a = span;
                                        return [4 /*yield*/, this.getLocalizedString('regConfirmCheckEmail')];
                                    case 1:
                                        _a.innerHTML = _b.sent();
                                        return [2 /*return*/];
                                }
                            });
                        }); }));
                        return [4 /*yield*/, this.activate(redirect_context_1.RedirectContext.SilentTab, this.data.urlType)];
                    case 2:
                        _b.sent();
                        this.getElement(this.SELECTORS.INLINE_REG).classList.add('hidden');
                        return [3 /*break*/, 5];
                    case 3:
                        status.classList.add('error');
                        _a = status;
                        return [4 /*yield*/, this.getLocalizedString('popup_error_generic')];
                    case 4:
                        _a.innerHTML = _b.sent();
                        _b.label = 5;
                    case 5:
                        status.classList.remove('hidden');
                        return [2 /*return*/];
                }
            });
        });
    };
    InlineRegistration.prototype.hide = function () {
        throw new Error("Method not implemented.");
    };
    InlineRegistration.prototype.dismiss = function () {
        throw new Error("Method not implemented.");
    };
    InlineRegistration.prototype.onUIConstructed = function () {
        throw new Error("Method not implemented.");
    };
    return InlineRegistration;
}(merchant_injection_base_1.MerchantInjectionBase));
exports.InlineRegistration = InlineRegistration;

},{"../../../enums/redirect-context":8,"../../../enums/runtime-message-types":9,"../../../models/runtime-message":17,"../../../utils/data-utils":18,"../merchant-injection-base":31}],29:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractableInjectionBase = void 0;
var clients_1 = require("../../enums/clients");
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var runtime_message_1 = require("../../models/runtime-message");
var content_injection_base_1 = require("./content-injection-base");
var InteractableInjectionBase = /** @class */ (function (_super) {
    __extends(InteractableInjectionBase, _super);
    function InteractableInjectionBase(params) {
        var _this = _super.call(this, params) || this;
        _this.FONT_FAMILY = 'OpenSans';
        _this.UPM_FONT_FAMILY = 'Lato';
        _this.IMAGE_ASSET_LOCATION = 'assets/images/';
        _this.BASE_SELECTORS = {
            x: '#x-close-button',
            dismiss: '.dismiss'
        };
        _this.css = params.css;
        _this.html = params.html;
        _this.injectionId = params.injectionId;
        _this.parent = params.parent || document.documentElement;
        _this.injectDOMContainer();
        return _this;
    }
    Object.defineProperty(InteractableInjectionBase.prototype, "shadowId", {
        get: function () {
            return "".concat(this.injectionId, "-shadow--container");
        },
        enumerable: false,
        configurable: true
    });
    InteractableInjectionBase.prototype.getImageFilePath = function (image) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getExtensionFilePath("".concat(this.IMAGE_ASSET_LOCATION, "/").concat(image))];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    InteractableInjectionBase.prototype.injectDOMContainer = function () {
        if (!document.getElementById(this.injectionId)) {
            // For SPAs, this element may already exist. Remove it and inject a new one.
            var container = document.getElementById(this.shadowId);
            if (container) {
                container.remove();
            }
            var shadowContainer = this.createElement('div');
            shadowContainer.id = this.shadowId;
            shadowContainer.style.zIndex = '2147483647';
            if (typeof shadowContainer.attachShadow === 'function') { // Shadow dom is available 
                var shadowRoot = shadowContainer.attachShadow({ mode: 'open' });
                this.root = shadowRoot;
                this.parent.appendChild(shadowContainer);
            }
            else {
                this.root = this.parent;
            }
            var style = this.createElement('style');
            if (this.css) {
                style.innerHTML = Sanitizer.escapeHTML(this.css);
            }
            this.appendStyle(style);
            var injectionContainer = this.createElement('div');
            injectionContainer.id = this.injectionId;
            injectionContainer.style.fontFamily = "".concat(this.data.client === clients_1.Clients.upm ? this.UPM_FONT_FAMILY : this.FONT_FAMILY, ", Helvetica, Arial");
            if (this.html) {
                injectionContainer.innerHTML = this.html;
            }
            this.root.appendChild(injectionContainer);
            this.injectionContainer = injectionContainer;
            return true;
        }
        else {
            return false;
        }
    };
    InteractableInjectionBase.prototype.appendStyle = function (style) {
        if (this.root === document.documentElement) {
            document.head.appendChild(style);
        }
        else if (this.root) {
            this.root.insertBefore(style, this.root.firstChild);
        }
    };
    InteractableInjectionBase.prototype.getElement = function (selector) {
        return this.root.querySelector(selector);
    };
    InteractableInjectionBase.prototype.getElements = function (selector) {
        return Array.from(this.root.querySelectorAll(selector));
    };
    InteractableInjectionBase.prototype.getLocalizedString = function (msgName) {
        var substitutions = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            substitutions[_i - 1] = arguments[_i];
        }
        return __awaiter(this, void 0, void 0, function () {
            var extensionMessage;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        extensionMessage = new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.GetLocalizedMessage, { msgName: msgName, substitutions: substitutions });
                        return [4 /*yield*/, this.sendExtensionMessage(extensionMessage)];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    InteractableInjectionBase.prototype.setX = function () {
        return __awaiter(this, void 0, void 0, function () {
            var xButton, xImagePath, xImage;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        xButton = this.getElement(this.BASE_SELECTORS.x);
                        return [4 /*yield*/, this.getExtensionFilePath('assets/images/close.svg')];
                    case 1:
                        xImagePath = _a.sent();
                        if (xButton) {
                            xButton.style.setProperty('--x-image', "url(".concat(xImagePath, ")"));
                            xImage = new Image();
                            xImage.src = xImagePath;
                            xImage.onerror = function () {
                                xButton.remove();
                            };
                        }
                        return [2 /*return*/];
                }
            });
        });
    };
    InteractableInjectionBase.prototype.setDismissClicks = function () {
        var _this = this;
        this.getElements(this.BASE_SELECTORS.dismiss).forEach(function (a) {
            a.onclick = function () { _this.dismiss(); };
        });
    };
    return InteractableInjectionBase;
}(content_injection_base_1.ContentInjectionBase));
exports.InteractableInjectionBase = InteractableInjectionBase;

},{"../../enums/clients":4,"../../enums/runtime-message-types":9,"../../models/runtime-message":17,"./content-injection-base":22}],30:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.LostActivationBase = void 0;
var content_injection_type_1 = require("../../../enums/content-injection-type");
var redirect_context_1 = require("../../../enums/redirect-context");
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var runtime_message_1 = require("../../../models/runtime-message");
var slider_all_base_1 = require("../slider-all-base");
var page_ids_1 = require("../../../enums/page-ids");
var LostActivationBase = /** @class */ (function (_super) {
    __extends(LostActivationBase, _super);
    function LostActivationBase(params) {
        var _this = _super.call(this, params) || this;
        _this.REWARDS_ACTIVATED = 'rewards-activated';
        _this.logoPath = 'assets/images/logo-dark.svg';
        _this.SELECTORS = {
            x: '#x-close-button',
            message: '#message-text',
            alertIcon: '#alert-icon',
            cta: '#cta',
            logo: '#logo',
            slider: '#slider',
            dismiss: '.dismiss',
            dismissLink: '#interaction .dismiss',
        };
        _this.setElements();
        return _this;
    }
    LostActivationBase.prototype.setElements = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, Promise.all([
                            this.setLogo(),
                            this.setCTA(),
                            this.setDismiss(),
                        ])];
                    case 1:
                        _a.sent();
                        this.show();
                        this.terms = this.data.merchant.displayTerms;
                        this.setTerms();
                        this.onUIConstructed();
                        return [2 /*return*/];
                }
            });
        });
    };
    LostActivationBase.prototype.setLogo = function () {
        return __awaiter(this, void 0, void 0, function () {
            var path, img, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        path = 'assets/images/slider-logo.svg';
                        img = this.getElement(this.SELECTORS.logo);
                        img.onerror = function () { img.parentElement.remove(); };
                        _a = img;
                        return [4 /*yield*/, this.getExtensionFilePath(path)];
                    case 1:
                        _a.src = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    LostActivationBase.prototype.setCTA = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setCTAText()];
                    case 1:
                        _a.sent();
                        this.cta.addEventListener('click', this.onInteraction.bind(this));
                        return [2 /*return*/];
                }
            });
        });
    };
    LostActivationBase.prototype.setCTAText = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a, message, ctaText, messageElement, ctaElement, path, img, _b;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0: return [4 /*yield*/, Promise.all([
                            this.getLocalizedString('lostActivationExplanation'),
                            this.getLocalizedString('lostActivationCallToAction'),
                        ])];
                    case 1:
                        _a = _c.sent(), message = _a[0], ctaText = _a[1];
                        messageElement = this.getElement(this.SELECTORS.message);
                        messageElement.textContent = message;
                        ctaElement = this.getElement(this.SELECTORS.cta);
                        ctaElement.textContent = ctaText;
                        path = 'assets/images/error.svg';
                        img = this.getElement(this.SELECTORS.alertIcon);
                        img.onerror = function () { img.parentElement.remove(); };
                        _b = img;
                        return [4 /*yield*/, this.getExtensionFilePath(path)];
                    case 2:
                        _b.src = _c.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    LostActivationBase.prototype.setDismiss = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                this.setX();
                this.getElements(this.SELECTORS.dismiss).forEach(function (a) {
                    a.onclick = function () { _this.dismiss(); };
                });
                return [2 /*return*/];
            });
        });
    };
    LostActivationBase.prototype.onInteraction = function (redirectContext) {
        var _a, _b, _c;
        if (redirectContext === void 0) { redirectContext = redirect_context_1.RedirectContext.Default; }
        if ((_c = (_b = (_a = this.data) === null || _a === void 0 ? void 0 : _a.merchant) === null || _b === void 0 ? void 0 : _b.placement) === null || _c === void 0 ? void 0 : _c.clickUrl) {
            this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.OpenNewTab, { "url": this.data.merchant.placement.clickUrl }));
        }
        else {
            if (!this.data.activated) {
                this.activate(redirectContext, undefined, page_ids_1.PageIds.LostActivationSliderClick);
            }
        }
        this.autoDismissActivated();
    };
    return LostActivationBase;
}(slider_all_base_1.SliderAllBase));
exports.LostActivationBase = LostActivationBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.LostActivation)] = LostActivationBase;

},{"../../../enums/content-injection-type":5,"../../../enums/page-ids":7,"../../../enums/redirect-context":8,"../../../enums/runtime-message-types":9,"../../../models/runtime-message":17,"../slider-all-base":34}],31:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MerchantInjectionBase = void 0;
var page_ids_1 = require("../../enums/page-ids");
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var url_types_1 = require("../../enums/url-types");
var runtime_message_1 = require("../../models/runtime-message");
var interactable_injection_base_1 = require("./interactable-injection-base");
var promise_utils_1 = require("../../utils/promise-utils");
var MerchantInjectionBase = /** @class */ (function (_super) {
    __extends(MerchantInjectionBase, _super);
    function MerchantInjectionBase() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(MerchantInjectionBase.prototype, "isCheckout", {
        get: function () { return this.data.urlType === url_types_1.UrlTypes.Checkout; },
        enumerable: false,
        configurable: true
    });
    MerchantInjectionBase.prototype.constructCtaString = function (type, isShort) {
        if (isShort === void 0) { isShort = false; }
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.constructMerchantCtaString(this.data.merchant, this.data.activated, type, isShort)];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    MerchantInjectionBase.prototype.activate = function (redirectContext, urlType, pageId) {
        var _a, _b;
        if (urlType === void 0) { urlType = this.data.urlType; }
        if (pageId === void 0) { pageId = page_ids_1.PageIds.Default; }
        if (!pageId || pageId === page_ids_1.PageIds.Default) {
            if (this.isCheckout) {
                if (((_b = (_a = this.data.merchant) === null || _a === void 0 ? void 0 : _a.coupons) === null || _b === void 0 ? void 0 : _b.length) === 0) {
                    pageId = page_ids_1.PageIds.SecondChanceActivation;
                }
                else {
                    pageId = page_ids_1.PageIds.CouponSliderClick;
                }
            }
            else if (this.data.urlType === url_types_1.UrlTypes.Merchant) {
                pageId = page_ids_1.PageIds.ActivationSliderClick;
            }
        }
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.Activate, {
            urlType: urlType,
            pageId: pageId,
            redirectContext: redirectContext,
            merchantId: this.data.merchant.id,
            tabId: this.data.tabId
        }));
    };
    MerchantInjectionBase.prototype.waitForWindowInstance = function (name) {
        return __awaiter(this, void 0, void 0, function () {
            var prop, x_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        prop = "Prdg".concat(this.clientName.toUpperCase()).concat(name);
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, promise_utils_1.PromiseUtils.waitFor(function () { return window[prop]; }, 500)];
                    case 2: return [2 /*return*/, _a.sent()];
                    case 3:
                        x_1 = _a.sent();
                        console.log("Error waiting for window instance: ".concat(prop, ":"), x_1);
                        return [3 /*break*/, 4];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    return MerchantInjectionBase;
}(interactable_injection_base_1.InteractableInjectionBase));
exports.MerchantInjectionBase = MerchantInjectionBase;

},{"../../enums/page-ids":7,"../../enums/runtime-message-types":9,"../../enums/url-types":11,"../../models/runtime-message":17,"../../utils/promise-utils":19,"./interactable-injection-base":29}],32:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NotificationBase = void 0;
var constants_1 = require("../../../models/constants");
var content_injection_type_1 = require("../../../enums/content-injection-type");
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var runtime_message_1 = require("../../../models/runtime-message");
var interactable_injection_base_1 = require("../../injections/interactable-injection-base");
var data_utils_1 = require("../../../utils/data-utils");
var NotificationBase = /** @class */ (function (_super) {
    __extends(NotificationBase, _super);
    function NotificationBase(params) {
        var _this = _super.call(this, params) || this;
        _this.AUTO_CLOSE_MILLISECONDS = constants_1.Constants.ONE_HOUR_MS * 4;
        _this.SELECTORS = {
            ICON: '#icon img',
            TEXT: '#text',
            LINK: '#link',
            TITLE: '#title',
            NOTIFICATION: '#notification'
        };
        _this.setElements();
        return _this;
    }
    NotificationBase.prototype.setElements = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setIcon()];
                    case 1:
                        _a.sent();
                        this.setTitle();
                        this.setText();
                        this.setLink();
                        this.setX();
                        this.setDismissClicks();
                        this.setAutoClose();
                        return [2 /*return*/];
                }
            });
        });
    };
    NotificationBase.prototype.setIcon = function () {
        return __awaiter(this, void 0, void 0, function () {
            var src;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getExtensionFilePath(this.data.icon)];
                    case 1:
                        src = _a.sent();
                        this.getElement(this.SELECTORS.ICON).src = src;
                        return [2 /*return*/];
                }
            });
        });
    };
    NotificationBase.prototype.setTitle = function () {
        if (this.data.title) {
            this.getElement(this.SELECTORS.TITLE).innerHTML = data_utils_1.DataUtils.getSafeHtml(this.data.title, false);
        }
    };
    NotificationBase.prototype.setText = function () {
        if (this.data.text) {
            this.getElement(this.SELECTORS.TEXT).innerHTML = data_utils_1.DataUtils.getSafeHtml(this.data.text, false);
        }
    };
    NotificationBase.prototype.setLink = function () {
        var _this = this;
        var link = this.getElement(this.SELECTORS.LINK);
        link.innerHTML = data_utils_1.DataUtils.getSafeHtml(this.data.linkText, false);
        link.onclick = function () { _this.onInteraction(); };
    };
    NotificationBase.prototype.hide = function () {
        this.getElement(this.SELECTORS.NOTIFICATION).classList.add('hidden');
    };
    NotificationBase.prototype.dismiss = function () {
        this.hide();
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.NotificationRemoveClicked, this.data.id));
    };
    NotificationBase.prototype.setAutoClose = function () {
        var _this = this;
        setTimeout(function () {
            _this.dismiss();
        }, this.AUTO_CLOSE_MILLISECONDS);
    };
    NotificationBase.prototype.onInteraction = function (detail) {
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.NotificationClicked, this.data.id));
        this.hide();
    };
    NotificationBase.prototype.onUIConstructed = function () {
        throw new Error("Method not implemented.");
    };
    return NotificationBase;
}(interactable_injection_base_1.InteractableInjectionBase));
exports.NotificationBase = NotificationBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.Notification)] = NotificationBase;

},{"../../../enums/content-injection-type":5,"../../../enums/runtime-message-types":9,"../../../models/constants":12,"../../../models/runtime-message":17,"../../../utils/data-utils":18,"../../injections/interactable-injection-base":29}],33:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SerpInjectionBase = void 0;
var content_injection_base_1 = require("./content-injection-base");
var runtime_message_1 = require("../../models/runtime-message");
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var content_injection_type_1 = require("../../enums/content-injection-type");
var data_utils_1 = require("../../utils/data-utils");
var SerpInjectionBase = /** @class */ (function (_super) {
    __extends(SerpInjectionBase, _super);
    function SerpInjectionBase(params) {
        var _this = _super.call(this, params) || this;
        _this.INJECT_TYPE = 'small';
        _this.urls = [];
        _this.merchantObjects = [];
        _this.setSearchUsed();
        _this.injectContent();
        return _this;
    }
    SerpInjectionBase.prototype.setSearchUsed = function () {
        var _this = this;
        var smallElements = document.querySelectorAll(this.data.pattern);
        smallElements.forEach(function (el) {
            var url = el.getAttribute('href');
            if (url && url.indexOf('http') === 0 && el.getAttribute('sbSearchUsed') !== 'true') {
                if (url.indexOf('url=http') > 0) {
                    url = unescape(url.match(/url=([^&]+)/).pop());
                }
                else if (_this.data.matchURL && url.indexOf(_this.data.matchURL) > 0) {
                    var matchUrl = _this.data.matchURL ? new RegExp("".concat(_this.data.matchURL, "([^&]+)")) : null;
                    url = unescape(url.match(matchUrl).pop());
                }
                el['injectUrl'] = url;
                el['injectType'] = _this.INJECT_TYPE;
                _this.merchantObjects.push(el);
                _this.urls.push(url);
                el.setAttribute("searchUsed".concat(_this.data.client), 'true');
            }
        });
    };
    SerpInjectionBase.prototype.injectContent = function () {
        return __awaiter(this, void 0, void 0, function () {
            var idStarter, metas, idCounter_1, _loop_1, this_1, i;
            var _this = this;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        idStarter = "prdg" + this.data.client;
                        if (!(this.urls.length > 0)) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.GetSerpMerchantMetasByUrls, {
                                urls: this.urls,
                                clientId: this.data.client
                            }))];
                    case 1:
                        metas = _a.sent();
                        if (metas) {
                            idCounter_1 = 0;
                            _loop_1 = function (i) {
                                var element = this_1.merchantObjects[i];
                                var meta = metas[i];
                                if (meta) {
                                    // TODO: ADD flagHtml
                                    // let flagHtml = '';
                                    // if (uCountry && meta.loc != uCountry) {
                                    //   let flag = this.getFlagSuffix(meta.loc);
                                    //   flagHtml = chrome.extension.getURL(`assets/images/shopearn/flag-${flag}.png`);
                                    // }
                                    var parent_1 = element;
                                    // Required currently for google as they have a different order of the links and the text that doesn't work with old layout.
                                    // Not very clean as you are working from inner element (the title), not the one it looks like it is hovering over.
                                    if (this_1.data.manuallyPushUpLevels) {
                                        for (var i_1 = 0; i_1 < this_1.data.manuallyPushUpLevels; i_1++) {
                                            if (parent_1.parentElement) {
                                                parent_1 = parent_1.parentElement;
                                            }
                                        }
                                    }
                                    var alreadyInjected = Array.from(parent_1.childNodes).some(function (element) { var _a; return (_a = element.id) === null || _a === void 0 ? void 0 : _a.startsWith(idStarter); });
                                    if (parent_1.childNodes && !alreadyInjected) {
                                        var container = this_1.createElement('div', function (div) { return __awaiter(_this, void 0, void 0, function () {
                                            var _a, _b, _c, _d;
                                            return __generator(this, function (_e) {
                                                switch (_e.label) {
                                                    case 0:
                                                        div.id = idStarter + '_' + idCounter_1;
                                                        div.style.display = "table";
                                                        _b = (_a = div).appendChild;
                                                        return [4 /*yield*/, this.injectImage()];
                                                    case 1:
                                                        _b.apply(_a, [_e.sent()]);
                                                        _d = (_c = div).appendChild;
                                                        return [4 /*yield*/, this.injectText(meta)];
                                                    case 2:
                                                        _d.apply(_c, [_e.sent()]);
                                                        return [2 /*return*/];
                                                }
                                            });
                                        }); });
                                        parent_1.insertBefore(container, parent_1.childNodes[0]);
                                        idCounter_1++;
                                    }
                                }
                            };
                            this_1 = this;
                            for (i in this.urls) {
                                _loop_1(i);
                            }
                        }
                        _a.label = 2;
                    case 2: return [2 /*return*/];
                }
            });
        });
    };
    SerpInjectionBase.prototype.injectImage = function () {
        var _this = this;
        return this.createElement('img', function (img) { return __awaiter(_this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = img;
                        return [4 /*yield*/, this.getExtensionFilePath("assets/images/serp/inject-".concat(this.INJECT_TYPE, "-icon.png"))];
                    case 1:
                        _a.src = _b.sent();
                        img.style.margin = "0";
                        img.style.float = "left";
                        return [2 /*return*/];
                }
            });
        }); });
    };
    SerpInjectionBase.prototype.injectText = function (meta) {
        var _this = this;
        return this.createElement('span', function (span) { return __awaiter(_this, void 0, void 0, function () {
            var cashBackText;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.constructMerchantCtaString(meta, false, runtime_message_types_1.RuntimeMessageTypes.ConstructRewardString)];
                    case 1:
                        cashBackText = _a.sent();
                        span.style.fontFamily = 'Helvetica, Arial, sans-serif';
                        span.style.fontSize = '14px';
                        span.style.marginLeft = '3px';
                        span.style.marginRight = '3px';
                        span.style.color = 'red';
                        span.style.display = 'inline-block';
                        span.style.textDecoration = 'none !important';
                        span.style.float = 'left';
                        span.innerHTML = data_utils_1.DataUtils.getSafeHtml(cashBackText);
                        return [2 /*return*/];
                }
            });
        }); });
    };
    return SerpInjectionBase;
}(content_injection_base_1.ContentInjectionBase));
exports.SerpInjectionBase = SerpInjectionBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.SerpInjection)] = SerpInjectionBase;

},{"../../enums/content-injection-type":5,"../../enums/runtime-message-types":9,"../../models/runtime-message":17,"../../utils/data-utils":18,"./content-injection-base":22}],34:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SliderAllBase = void 0;
var runtime_message_types_1 = require("../../enums/runtime-message-types");
var runtime_message_1 = require("../../models/runtime-message");
var merchant_injection_base_1 = require("./merchant-injection-base");
// @todo CXP-2242 Should this be different for Conquest
var slider_positioner_1 = require("../injections/slider/slider-positioner");
var data_utils_1 = require("../../utils/data-utils");
var SliderAllBase = /** @class */ (function (_super) {
    __extends(SliderAllBase, _super);
    function SliderAllBase(params) {
        var _this = _super.call(this, params) || this;
        _this.CLASS = {
            hidden: 'hidden',
            primaryDark: 'primary-dark',
        };
        _this.SELECTORS_ALL_BASE = {
            cta: '#cta',
            slider: '#slider',
            dismiss: '.dismiss',
            dismissLink: '#interaction .dismiss',
            secondaryContent: '#secondary-content',
            terms: '#terms',
            termsSpecialTerms: '#popup_special_terms',
            termsFullTerms: '#popup_full_terms_and_conditions',
            termsOpen: '#open',
            termsClose: '#close',
            termsIndividual: '#individual-terms',
            termsIndividualContainer: '#individual-terms-container',
        };
        _this.logImpression();
        return _this;
    }
    Object.defineProperty(SliderAllBase.prototype, "cta", {
        get: function () { return this.getElement(this.SELECTORS_ALL_BASE.cta); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(SliderAllBase.prototype, "slider", {
        get: function () { return this.getElement(this.SELECTORS_ALL_BASE.slider); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(SliderAllBase.prototype, "couponCount", {
        get: function () { var _a; return (_a = this.data.merchant.coupons) === null || _a === void 0 ? void 0 : _a.length; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(SliderAllBase.prototype, "isApplyCoupons", {
        get: function () { return this.isCheckout && this.data.merchant.hasMerchantScript && (this.data.merchant.couponApplyEnabled || this.data.memberIsTester); },
        enumerable: false,
        configurable: true
    });
    SliderAllBase.prototype.show = function () {
        var _this = this;
        // Wait for more things to be loaded on the page to keep the animation from being choppy.
        // It also makes the slider feel separate from the rest of the page.
        var ANIMATION_DELAY = 1000;
        setTimeout(function () {
            _this.slider.classList.add('slide');
            setTimeout(function () {
                _this.positioner.check();
            }, ANIMATION_DELAY);
        }, ANIMATION_DELAY);
    };
    SliderAllBase.prototype.logImpression = function () {
        // In the current code, this seems to fire regardless of the slider type: activation, view coupons, or apply coupons. Is that correct?
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.LogImpression, this.data.tabId));
        // Don't show slider when user is deep into the site
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.SetActivationInjected, { tabId: this.data.tabId }));
    };
    SliderAllBase.prototype.dismiss = function () {
        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.DismissActivation, { tabId: this.data.tabId }));
        this.hide();
    };
    SliderAllBase.prototype.hide = function () {
        this.slider.classList.remove('slide');
    };
    SliderAllBase.prototype.onUIConstructed = function () {
        this.positioner = new slider_positioner_1.SliderPositioner(this.slider, this.shadowId);
    };
    SliderAllBase.prototype.setTerms = function () {
        var _a;
        return __awaiter(this, void 0, void 0, function () {
            var elSecondaryContent, elIndTermsContainer, elTermsInd, elSpecialTerms, textSpecial, elOpen, _b, elClose, _c, elFullTerms, storePageUrl_1, _d, _e, _f, _i, _g, term;
            var _this = this;
            return __generator(this, function (_h) {
                switch (_h.label) {
                    case 0:
                        if (!(((_a = this.terms) === null || _a === void 0 ? void 0 : _a.length) > 0)) return [3 /*break*/, 5];
                        elSecondaryContent = this.getElement(this.SELECTORS_ALL_BASE.secondaryContent);
                        elSecondaryContent.classList.remove(this.CLASS.hidden);
                        elIndTermsContainer = this.getElement(this.SELECTORS_ALL_BASE.termsIndividualContainer);
                        elIndTermsContainer.hidden = true;
                        elTermsInd = this.getElement(this.SELECTORS_ALL_BASE.termsIndividual);
                        elSpecialTerms = this.getElement(this.SELECTORS_ALL_BASE.termsSpecialTerms);
                        return [4 /*yield*/, this.getLocalizedString("popup_special_terms")];
                    case 1:
                        textSpecial = _h.sent();
                        elSpecialTerms.textContent = textSpecial;
                        elOpen = this.getElement(this.SELECTORS_ALL_BASE.termsOpen);
                        _b = elOpen;
                        return [4 /*yield*/, this.getLocalizedString("open")];
                    case 2:
                        _b.textContent = _h.sent();
                        elOpen.addEventListener('click', function () { _this.toggleOpenClosed(); });
                        elClose = this.getElement(this.SELECTORS_ALL_BASE.termsClose);
                        _c = elClose;
                        return [4 /*yield*/, this.getLocalizedString("close")];
                    case 3:
                        _c.textContent = _h.sent();
                        elClose.hidden = true;
                        elClose.addEventListener('click', function () { _this.toggleOpenClosed(); });
                        elFullTerms = this.getElement(this.SELECTORS_ALL_BASE.termsFullTerms);
                        storePageUrl_1 = this.data.merchant.storePageUrl;
                        elFullTerms.addEventListener('click', function () {
                            _this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.OpenSiteTab, storePageUrl_1));
                        });
                        _d = elFullTerms;
                        _f = (_e = data_utils_1.DataUtils).getSafeHtml;
                        return [4 /*yield*/, this.getLocalizedString("popup_full_terms_and_conditions")];
                    case 4:
                        _d.innerHTML = _f.apply(_e, [_h.sent()]);
                        for (_i = 0, _g = this.terms; _i < _g.length; _i++) {
                            term = _g[_i];
                            this.setIndividualTerms(term, elTermsInd);
                        }
                        _h.label = 5;
                    case 5: return [2 /*return*/];
                }
            });
        });
    };
    SliderAllBase.prototype.setIndividualTerms = function (term, elTermsInd) {
        var _this = this;
        elTermsInd.appendChild(this.createElement('div', function (elTerm) { return __awaiter(_this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                elTerm.classList.add('term');
                elTerm.appendChild(this.createElement('span', function (elTermText) {
                    elTermText.classList.add('term-text');
                    elTermText.innerHTML = data_utils_1.DataUtils.getSafeHtml(term.description);
                }));
                elTerm.appendChild(this.createElement('div', function (elReward) {
                    elReward.classList.add('reward');
                    elReward.classList.add(_this.CLASS.primaryDark);
                    elReward.innerHTML = data_utils_1.DataUtils.getSafeHtml(term.rewardString, false);
                }));
                return [2 /*return*/];
            });
        }); }));
    };
    SliderAllBase.prototype.toggleOpenClosed = function () {
        var elClose = this.getElement(this.SELECTORS_ALL_BASE.termsClose);
        var elOpen = this.getElement(this.SELECTORS_ALL_BASE.termsOpen);
        var elIndTermsContainer = this.getElement(this.SELECTORS_ALL_BASE.termsIndividualContainer);
        var closeElementHidden2 = elClose.hidden;
        elClose.hidden = !closeElementHidden2;
        elOpen.hidden = closeElementHidden2;
        elIndTermsContainer.hidden = !closeElementHidden2;
    };
    SliderAllBase.prototype.autoDismissActivated = function () {
        return __awaiter(this, void 0, void 0, function () {
            var AUTO_DISMISS_ACTIVATED_TIMEOUT;
            var _this = this;
            return __generator(this, function (_a) {
                AUTO_DISMISS_ACTIVATED_TIMEOUT = 5000;
                setTimeout(function () {
                    var termsCloseElement = _this.getElement(_this.SELECTORS_ALL_BASE.termsClose);
                    if (termsCloseElement.hidden) {
                        _this.hide();
                    }
                }, AUTO_DISMISS_ACTIVATED_TIMEOUT);
                return [2 /*return*/];
            });
        });
    };
    return SliderAllBase;
}(merchant_injection_base_1.MerchantInjectionBase));
exports.SliderAllBase = SliderAllBase;

},{"../../enums/runtime-message-types":9,"../../models/runtime-message":17,"../../utils/data-utils":18,"../injections/slider/slider-positioner":36,"./merchant-injection-base":31}],35:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SliderBase = void 0;
var content_injection_type_1 = require("../../../enums/content-injection-type");
var redirect_context_1 = require("../../../enums/redirect-context");
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var slider_type_1 = require("../../../enums/slider-type");
var url_types_1 = require("../../../enums/url-types");
var runtime_message_1 = require("../../../models/runtime-message");
var slider_all_base_1 = require("../slider-all-base");
var data_utils_1 = require("../../../utils/data-utils");
var SliderBase = /** @class */ (function (_super) {
    __extends(SliderBase, _super);
    function SliderBase(params) {
        var _this = _super.call(this, params) || this;
        _this.REWARDS_ACTIVATED = 'rewards-activated';
        _this.SELECTORS = {
            x: '#x-close-button',
            cta: '#cta',
            and: '#and',
            logo: '#logo',
            slider: '#slider',
            dismiss: '.dismiss',
            dismissLink: '#interaction .dismiss',
        };
        _this.setElements();
        _this.initEventHandlers();
        return _this;
    }
    SliderBase.prototype.setElements = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setLogo()];
                    case 1:
                        _a.sent();
                        return [4 /*yield*/, this.setCTA()];
                    case 2:
                        _a.sent();
                        return [4 /*yield*/, this.setAnd()];
                    case 3:
                        _a.sent();
                        return [4 /*yield*/, this.setDismiss()];
                    case 4:
                        _a.sent();
                        if (this.data.activated && this.data.urlType !== url_types_1.UrlTypes.Checkout) {
                            this.showActivated();
                        }
                        this.show();
                        if (this.data.activated && (this.data.type !== slider_type_1.SliderType.Coupons && this.data.urlType !== url_types_1.UrlTypes.Checkout)) {
                            this.showActivated();
                        }
                        this.terms = this.data.merchant.displayTerms;
                        this.setTerms();
                        this.onUIConstructed();
                        return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.setLogo = function () {
        return __awaiter(this, void 0, void 0, function () {
            var img, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        img = this.getElement(this.SELECTORS.logo);
                        img.onerror = function () { img.parentElement.remove(); };
                        _a = img;
                        return [4 /*yield*/, this.getImageFilePath('slider-logo.svg')];
                    case 1:
                        _a.src = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.setCTA = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setCTAText()];
                    case 1:
                        _a.sent();
                        this.cta.onclick = function () { _this.onInteraction(); };
                        return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.setCTAText = function () {
        var _a, _b;
        return __awaiter(this, void 0, void 0, function () {
            var count, cta, message, reward, couponWorker, args;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        // Special Discover Offer case when we use the custom copyText instead of standard slider text
                        if ((_b = (_a = this.data.merchant) === null || _a === void 0 ? void 0 : _a.placement) === null || _b === void 0 ? void 0 : _b.copyText) {
                            this.cta.innerHTML = data_utils_1.DataUtils.getSafeHtml(this.data.merchant.placement.copyText, false);
                            return [2 /*return*/];
                        }
                        if (!(this.data.type === slider_type_1.SliderType.Activation)) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.constructCtaString(runtime_message_types_1.RuntimeMessageTypes.ConstructActivateString)];
                    case 1:
                        cta = _c.sent();
                        return [3 /*break*/, 6];
                    case 2:
                        if (!(this.data.type === slider_type_1.SliderType.Coupons)) return [3 /*break*/, 6];
                        return [4 /*yield*/, this.constructCtaString(runtime_message_types_1.RuntimeMessageTypes.ConstructActivateString, true)];
                    case 3:
                        reward = _c.sent();
                        return [4 /*yield*/, this.waitForWindowInstance('CouponWorker')];
                    case 4:
                        couponWorker = _c.sent();
                        if (this.isApplyCoupons && couponWorker.initialElementsCheckPassed) {
                            count = couponWorker.dedupeCoupons().length;
                            message = count === 1 ? 'applyCoupon' : 'applyCoupons';
                            if (!this.data.activated) {
                                message += 'AndReward';
                            }
                            this.couponWorkerInitialElementsCheckPassed = true;
                        }
                        else {
                            count = this.couponCount;
                            if (!this.data.memberId && !count) {
                                cta = reward;
                            }
                            else {
                                message = count === 1 ? 'showCoupon' : 'showCoupons';
                                if (this.shouldAddReward()) {
                                    message += 'AndReward';
                                }
                            }
                        }
                        if (!!cta) return [3 /*break*/, 6];
                        args = this.constructCTAArgs(message, reward, count);
                        return [4 /*yield*/, this.getLocalizedString.apply(this, args)];
                    case 5:
                        cta = _c.sent();
                        _c.label = 6;
                    case 6:
                        this.cta.innerHTML = data_utils_1.DataUtils.getSafeHtml(cta, false);
                        return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.shouldAddReward = function () {
        var shouldAddReward = !!this.data.merchant.reward.amount
            && (this.data.urlType === url_types_1.UrlTypes.Checkout
                || (!this.data.merchant.couponApplyEnabled && !this.data.activated)
                || !this.data.activated);
        return shouldAddReward;
    };
    SliderBase.prototype.constructCTAArgs = function (message, reward, count) {
        var args = [message];
        if (count > 1) {
            args.push(count.toString());
        }
        args.push(reward);
        return args;
    };
    SliderBase.prototype.setAnd = function () {
        var _a;
        return __awaiter(this, void 0, void 0, function () {
            var and, couponCount, _b, _c, _d, _e, _f, _g;
            return __generator(this, function (_h) {
                switch (_h.label) {
                    case 0:
                        and = this.getElement(this.SELECTORS.and);
                        couponCount = (_a = this.data.merchant.coupons) === null || _a === void 0 ? void 0 : _a.length;
                        if (!(this.data.type === slider_type_1.SliderType.Activation && this.data.urlType !== url_types_1.UrlTypes.Checkout && !this.data.activated && couponCount)) return [3 /*break*/, 5];
                        if (!(couponCount === 1)) return [3 /*break*/, 2];
                        _b = and;
                        _d = (_c = data_utils_1.DataUtils).getSafeHtml;
                        return [4 /*yield*/, this.getLocalizedString('slider_and_coupon')];
                    case 1:
                        _b.innerHTML = _d.apply(_c, [_h.sent(), false]);
                        return [3 /*break*/, 4];
                    case 2:
                        _e = and;
                        _g = (_f = data_utils_1.DataUtils).getSafeHtml;
                        return [4 /*yield*/, this.getLocalizedString('slider_and_coupons', this.couponCount.toString())];
                    case 3:
                        _e.innerHTML = _g.apply(_f, [_h.sent(), false]);
                        _h.label = 4;
                    case 4:
                        and.classList.remove('hidden');
                        return [3 /*break*/, 6];
                    case 5:
                        this.cta.classList.add('no-and');
                        _h.label = 6;
                    case 6: return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.setDismiss = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.setX();
                        _a = this.getElement(this.SELECTORS.dismissLink);
                        return [4 /*yield*/, this.getLocalizedString('remindMeLater')];
                    case 1:
                        _a.innerText = _b.sent();
                        this.getElements(this.SELECTORS.dismiss).forEach(function (a) {
                            a.onclick = function () { _this.dismiss(); };
                        });
                        return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.initEventHandlers = function () {
        var _this = this;
        document.addEventListener(this.REWARDS_ACTIVATED, function (evt) {
            // don't show the activated slider if the user clicked to show coupons. MTJ-TODO
            //if (!this.showingCoupons) {
            if (evt.detail.client === _this.data.client) {
                _this.data.activated = true;
                _this.showActivated();
            }
            //}
        });
    };
    SliderBase.prototype.showActivated = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        // We've activated and injected, effectively "confirming activation."
                        // Mark the tab injection state accordingly.
                        this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.SetActivationConfirmed, { tabId: this.data.tabId }));
                        return [4 /*yield*/, this.setCTAText()];
                    case 1:
                        _a.sent();
                        this.cta.classList.add('activated');
                        this.getElement(this.SELECTORS.dismissLink).classList.add('hidden');
                        this.getElement(this.BASE_SELECTORS.x).onclick = function () { _this.hide(); }; // reset so we don't log the dismissed event 
                        if (!this.slider.classList.contains('slide')) {
                            this.slider.classList.add('slide');
                            this.autoDismissActivated();
                        }
                        return [2 /*return*/];
                }
            });
        });
    };
    SliderBase.prototype.onInteraction = function (redirectContext) {
        var _this = this;
        if (redirectContext === void 0) { redirectContext = redirect_context_1.RedirectContext.Default; }
        if (!this.data.activated) {
            this.activate(redirectContext);
        }
        if (this.data.type === slider_type_1.SliderType.Coupons) {
            this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.SetActivationConfirmed, { tabId: this.data.tabId }));
            var injection = this.isApplyCoupons && this.couponWorkerInitialElementsCheckPassed ? content_injection_type_1.ContentInjectionType.ApplyCoupons : content_injection_type_1.ContentInjectionType.ViewCoupons;
            this.sendExtensionMessage(new runtime_message_1.RuntimeMessage(runtime_message_types_1.RuntimeMessageTypes.InjectContent, {
                type: injection,
                tabId: this.data.tabId,
                data: this.data
            }));
            this.slider.classList.add('hidden');
            this.hide();
        }
        else {
            setTimeout(function () {
                _this.hide();
            }, 500);
        }
    };
    return SliderBase;
}(slider_all_base_1.SliderAllBase));
exports.SliderBase = SliderBase;
window["Prdg_".concat(content_injection_type_1.ContentInjectionType.Slider)] = SliderBase;

},{"../../../enums/content-injection-type":5,"../../../enums/redirect-context":8,"../../../enums/runtime-message-types":9,"../../../enums/slider-type":10,"../../../enums/url-types":11,"../../../models/runtime-message":17,"../../../utils/data-utils":18,"../slider-all-base":34}],36:[function(require,module,exports){
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SliderPositioner = void 0;
var SliderPositioner = /** @class */ (function () {
    function SliderPositioner(slider, shadowContainerId) {
        this.rechecks = 0;
        this.slider = slider;
        this.shadowContainerId = shadowContainerId;
    }
    SliderPositioner.prototype.check = function () {
        return __awaiter(this, void 0, void 0, function () {
            var bounds, coveringEl;
            var _this = this;
            return __generator(this, function (_a) {
                bounds = this.slider.getBoundingClientRect();
                coveringEl = this.getCoveringElement(bounds);
                if (coveringEl) {
                    this.move(bounds);
                    setTimeout(function () {
                        _this.check();
                        _this.rechecks = 0;
                    }, 500);
                }
                else if (this.rechecks < 5) {
                    // Keep checking a few times. Sometimes other sliders or whatever show up late and cover.
                    setTimeout(function () {
                        _this.check();
                    }, 5000);
                    this.rechecks++;
                }
                return [2 /*return*/];
            });
        });
    };
    SliderPositioner.prototype.getCoveringElement = function (bounds) {
        var coveringEl;
        // Get the left and right points
        var horizontalPoints = [
            bounds.left + (0.1 * bounds.width),
            bounds.right - (0.1 * bounds.width)
        ];
        // Get the top and bottom points
        var verticalPoints = [
            bounds.top + (0.1 * bounds.height),
            bounds.bottom - (0.1 * bounds.height)
        ];
        // See if there is a different element above this one
        for (var x = 0; x < horizontalPoints.length; x++) {
            for (var y = 0; y < verticalPoints.length; y++) {
                var el = document.elementFromPoint(horizontalPoints[x], verticalPoints[y]);
                if (el && el.id !== this.shadowContainerId) {
                    coveringEl = el;
                    break;
                }
            }
            if (coveringEl) {
                break;
            }
        }
        return coveringEl;
    };
    SliderPositioner.prototype.move = function (bounds) {
        // If the slider starts at the top of the page, move it down. Otherwise up.
        if (bounds.top < (screen.height / 2)) {
            this.slider.style.top = "".concat(bounds.top + bounds.height + 20, "px");
        }
        else {
            this.slider.style.bottom = 'auto';
            this.slider.style.top = "".concat(bounds.top - bounds.height - 20, "px");
        }
    };
    return SliderPositioner;
}());
exports.SliderPositioner = SliderPositioner;

},{}],37:[function(require,module,exports){
"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewCouponsBase = void 0;
var runtime_message_types_1 = require("../../../enums/runtime-message-types");
var data_utils_1 = require("../../../utils/data-utils");
var coupon_injection_base_1 = require("../coupon-injection-base");
var view_coupons_log_item_1 = require("../../../models/content-injection/logging/view-coupons-log-item");
var ViewCouponsBase = /** @class */ (function (_super) {
    __extends(ViewCouponsBase, _super);
    function ViewCouponsBase(params) {
        var _this = _super.call(this, params) || this;
        _this.SELECTORS = {
            coupon: '.coupon',
            coupons: '#coupons',
            noCoupons: '#no-coupons',
            couponCode: '.coupon-code',
            clientLogo: '#client-logo',
            viewCoupons: '#view-coupons',
            couponCopied: '.coupon-copied',
            merchantLogo: '#merchant-logo',
            couponInteraction: '.coupon-interaction',
            merchantLogoContainer: '#merchant-logo-container'
        };
        _this.setElements();
        _this.getWorker();
        return _this;
    }
    ViewCouponsBase.prototype.getWorker = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = this;
                        return [4 /*yield*/, this.waitForWindowInstance('CouponWorker')];
                    case 1:
                        _a.couponWorker = _b.sent();
                        this.data.merchant.coupons = this.couponWorker.dedupeCoupons();
                        this.logItem.couponsAvailable = this.data.merchant.coupons.length;
                        if (this.couponWorker.initialElementsCheckFailed) {
                            this.logItem.trackingCouponDetails.set("errors", { "message": "Initial elements check failed." });
                        }
                        return [2 /*return*/];
                }
            });
        });
    };
    ViewCouponsBase.prototype.setElements = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.setMerchantLogo()];
                    case 1:
                        _a.sent();
                        if (!this.data.merchant.coupons.length) return [3 /*break*/, 3];
                        return [4 /*yield*/, this.setCoupons()];
                    case 2:
                        _a.sent();
                        return [3 /*break*/, 5];
                    case 3: return [4 /*yield*/, this.setNoCoupons()];
                    case 4:
                        _a.sent();
                        _a.label = 5;
                    case 5: return [4 /*yield*/, this.setClientLogo()];
                    case 6:
                        _a.sent();
                        return [4 /*yield*/, this.setX()];
                    case 7:
                        _a.sent();
                        this.setDismissClicks();
                        this.onUIConstructed();
                        return [2 /*return*/];
                }
            });
        });
    };
    ViewCouponsBase.prototype.setMerchantLogo = function () {
        return __awaiter(this, void 0, void 0, function () {
            var el;
            var _this = this;
            return __generator(this, function (_a) {
                el = this.getElement(this.SELECTORS.merchantLogo);
                el.src = this.data.merchant.img || '';
                el.addEventListener('error', function () {
                    var container = _this.getElement(_this.SELECTORS.merchantLogoContainer);
                    container.removeChild(el);
                    container.appendChild(_this.createElement('h3', function (span) { return __awaiter(_this, void 0, void 0, function () {
                        var _a;
                        return __generator(this, function (_b) {
                            switch (_b.label) {
                                case 0:
                                    _a = span;
                                    return [4 /*yield*/, this.getLocalizedString('merchantCoupons', this.data.merchant.name)];
                                case 1:
                                    _a.innerText = _b.sent();
                                    return [2 /*return*/];
                            }
                        });
                    }); }));
                });
                return [2 /*return*/];
            });
        });
    };
    ViewCouponsBase.prototype.setCoupons = function () {
        var _a;
        return __awaiter(this, void 0, void 0, function () {
            var copied, coupons;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0: return [4 /*yield*/, this.getLocalizedString('copied')];
                    case 1:
                        copied = _b.sent();
                        coupons = this.getElement(this.SELECTORS.coupons);
                        (_a = this.data.merchant.coupons) === null || _a === void 0 ? void 0 : _a.forEach(function (coupon, index) {
                            coupons.appendChild(_this.createElement('div', function (elCoupon) {
                                var code = coupon.code;
                                elCoupon.className = 'coupon';
                                elCoupon.appendChild(_this.createElement('div', function (text) {
                                    text.className = 'coupon-text';
                                    text.innerText = coupon.description;
                                }));
                                elCoupon.appendChild(_this.createElement('div', function (interaction) {
                                    interaction.className = 'coupon-interaction';
                                    interaction.appendChild(_this.createElement('span', function (elCode) {
                                        elCode.className = 'coupon-code';
                                        elCode.innerText = code;
                                    }));
                                    interaction.appendChild(_this.createElement('span', function (elCopied) { return __awaiter(_this, void 0, void 0, function () {
                                        return __generator(this, function (_a) {
                                            elCopied.className = 'coupon-copied opaque';
                                            elCopied.innerText = copied;
                                            return [2 /*return*/];
                                        });
                                    }); }));
                                }));
                                elCoupon.onclick = function () { _this.onInteraction({ index: index, code: code }); };
                            }));
                        });
                        return [2 /*return*/];
                }
            });
        });
    };
    ViewCouponsBase.prototype.setNoCoupons = function () {
        return __awaiter(this, void 0, void 0, function () {
            var el, cta, plus, bonus, bottom;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        el = this.getElement(this.SELECTORS.noCoupons);
                        return [4 /*yield*/, this.constructCtaString(runtime_message_types_1.RuntimeMessageTypes.ConstructActivateString)];
                    case 1:
                        cta = _a.sent();
                        return [4 /*yield*/, this.getLocalizedString('joinBonusOfferLoggedOutStart')];
                    case 2:
                        plus = _a.sent();
                        return [4 /*yield*/, this.getLocalizedString('joinBonusOfferLoggedOutMiddle')];
                    case 3:
                        bonus = _a.sent();
                        return [4 /*yield*/, this.getLocalizedString('joinBonusOfferLoggedOutEnd')];
                    case 4:
                        bottom = _a.sent();
                        el.innerHTML = data_utils_1.DataUtils.getSafeHtml("<b>".concat(cta, "</b><br />").concat(plus, " <b>").concat(bonus, "</b> ").concat(bottom), false);
                        el.classList.remove('hidden');
                        return [2 /*return*/];
                }
            });
        });
    };
    ViewCouponsBase.prototype.setClientLogo = function () {
        return __awaiter(this, void 0, void 0, function () {
            var img, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        img = this.getElement(this.SELECTORS.clientLogo);
                        img.onerror = function () { img.remove(); };
                        _a = img;
                        return [4 /*yield*/, this.getImageFilePath('logo-dark.svg')];
                    case 1:
                        _a.src = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    ViewCouponsBase.prototype.dismiss = function () {
        this.hide();
    };
    ViewCouponsBase.prototype.hide = function () {
        this.getElement(this.SELECTORS.viewCoupons).classList.add('slide');
    };
    ViewCouponsBase.prototype.onInteraction = function (detail) {
        var el = this.getElements(this.SELECTORS.coupon)[detail.index];
        var interaction = el.querySelector(this.SELECTORS.couponInteraction);
        var code = interaction.querySelector(this.SELECTORS.couponCode);
        var copied = interaction.querySelector(this.SELECTORS.couponCopied);
        interaction.classList.add('active');
        code.classList.add('opaque');
        copied.classList.remove('opaque');
        data_utils_1.DataUtils.copyTextToClipboard(detail.code);
        this.logItem.sliderClicked = 1;
        this.logItem.couponsCopied++;
        setTimeout(function () {
            interaction.classList.remove('active');
            code.classList.remove('opaque');
            copied.classList.add('opaque');
        }, 2000);
    };
    ViewCouponsBase.prototype.constructLogItem = function () {
        return new view_coupons_log_item_1.ViewCouponsLogItem(this.data);
    };
    return ViewCouponsBase;
}(coupon_injection_base_1.CouponInjectionBase));
exports.ViewCouponsBase = ViewCouponsBase;

},{"../../../enums/runtime-message-types":9,"../../../models/content-injection/logging/view-coupons-log-item":16,"../../../utils/data-utils":18,"../coupon-injection-base":23}],38:[function(require,module,exports){
/*! @license DOMPurify 3.2.2 | (c) Cure53 and other contributors | Released under the Apache license 2.0 and Mozilla Public License 2.0 | github.com/cure53/DOMPurify/blob/3.2.2/LICENSE */

(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
  typeof define === 'function' && define.amd ? define(factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, global.DOMPurify = factory());
})(this, (function () { 'use strict';

  const {
    entries,
    setPrototypeOf,
    isFrozen,
    getPrototypeOf,
    getOwnPropertyDescriptor
  } = Object;
  let {
    freeze,
    seal,
    create
  } = Object; // eslint-disable-line import/no-mutable-exports
  let {
    apply,
    construct
  } = typeof Reflect !== 'undefined' && Reflect;
  if (!freeze) {
    freeze = function freeze(x) {
      return x;
    };
  }
  if (!seal) {
    seal = function seal(x) {
      return x;
    };
  }
  if (!apply) {
    apply = function apply(fun, thisValue, args) {
      return fun.apply(thisValue, args);
    };
  }
  if (!construct) {
    construct = function construct(Func, args) {
      return new Func(...args);
    };
  }
  const arrayForEach = unapply(Array.prototype.forEach);
  const arrayPop = unapply(Array.prototype.pop);
  const arrayPush = unapply(Array.prototype.push);
  const stringToLowerCase = unapply(String.prototype.toLowerCase);
  const stringToString = unapply(String.prototype.toString);
  const stringMatch = unapply(String.prototype.match);
  const stringReplace = unapply(String.prototype.replace);
  const stringIndexOf = unapply(String.prototype.indexOf);
  const stringTrim = unapply(String.prototype.trim);
  const objectHasOwnProperty = unapply(Object.prototype.hasOwnProperty);
  const regExpTest = unapply(RegExp.prototype.test);
  const typeErrorCreate = unconstruct(TypeError);
  /**
   * Creates a new function that calls the given function with a specified thisArg and arguments.
   *
   * @param func - The function to be wrapped and called.
   * @returns A new function that calls the given function with a specified thisArg and arguments.
   */
  function unapply(func) {
    return function (thisArg) {
      for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
        args[_key - 1] = arguments[_key];
      }
      return apply(func, thisArg, args);
    };
  }
  /**
   * Creates a new function that constructs an instance of the given constructor function with the provided arguments.
   *
   * @param func - The constructor function to be wrapped and called.
   * @returns A new function that constructs an instance of the given constructor function with the provided arguments.
   */
  function unconstruct(func) {
    return function () {
      for (var _len2 = arguments.length, args = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
        args[_key2] = arguments[_key2];
      }
      return construct(func, args);
    };
  }
  /**
   * Add properties to a lookup table
   *
   * @param set - The set to which elements will be added.
   * @param array - The array containing elements to be added to the set.
   * @param transformCaseFunc - An optional function to transform the case of each element before adding to the set.
   * @returns The modified set with added elements.
   */
  function addToSet(set, array) {
    let transformCaseFunc = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : stringToLowerCase;
    if (setPrototypeOf) {
      // Make 'in' and truthy checks like Boolean(set.constructor)
      // independent of any properties defined on Object.prototype.
      // Prevent prototype setters from intercepting set as a this value.
      setPrototypeOf(set, null);
    }
    let l = array.length;
    while (l--) {
      let element = array[l];
      if (typeof element === 'string') {
        const lcElement = transformCaseFunc(element);
        if (lcElement !== element) {
          // Config presets (e.g. tags.js, attrs.js) are immutable.
          if (!isFrozen(array)) {
            array[l] = lcElement;
          }
          element = lcElement;
        }
      }
      set[element] = true;
    }
    return set;
  }
  /**
   * Clean up an array to harden against CSPP
   *
   * @param array - The array to be cleaned.
   * @returns The cleaned version of the array
   */
  function cleanArray(array) {
    for (let index = 0; index < array.length; index++) {
      const isPropertyExist = objectHasOwnProperty(array, index);
      if (!isPropertyExist) {
        array[index] = null;
      }
    }
    return array;
  }
  /**
   * Shallow clone an object
   *
   * @param object - The object to be cloned.
   * @returns A new object that copies the original.
   */
  function clone(object) {
    const newObject = create(null);
    for (const [property, value] of entries(object)) {
      const isPropertyExist = objectHasOwnProperty(object, property);
      if (isPropertyExist) {
        if (Array.isArray(value)) {
          newObject[property] = cleanArray(value);
        } else if (value && typeof value === 'object' && value.constructor === Object) {
          newObject[property] = clone(value);
        } else {
          newObject[property] = value;
        }
      }
    }
    return newObject;
  }
  /**
   * This method automatically checks if the prop is function or getter and behaves accordingly.
   *
   * @param object - The object to look up the getter function in its prototype chain.
   * @param prop - The property name for which to find the getter function.
   * @returns The getter function found in the prototype chain or a fallback function.
   */
  function lookupGetter(object, prop) {
    while (object !== null) {
      const desc = getOwnPropertyDescriptor(object, prop);
      if (desc) {
        if (desc.get) {
          return unapply(desc.get);
        }
        if (typeof desc.value === 'function') {
          return unapply(desc.value);
        }
      }
      object = getPrototypeOf(object);
    }
    function fallbackValue() {
      return null;
    }
    return fallbackValue;
  }

  const html$1 = freeze(['a', 'abbr', 'acronym', 'address', 'area', 'article', 'aside', 'audio', 'b', 'bdi', 'bdo', 'big', 'blink', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'content', 'data', 'datalist', 'dd', 'decorator', 'del', 'details', 'dfn', 'dialog', 'dir', 'div', 'dl', 'dt', 'element', 'em', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html', 'i', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'main', 'map', 'mark', 'marquee', 'menu', 'menuitem', 'meter', 'nav', 'nobr', 'ol', 'optgroup', 'option', 'output', 'p', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'section', 'select', 'shadow', 'small', 'source', 'spacer', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr']);
  // SVG
  const svg$1 = freeze(['svg', 'a', 'altglyph', 'altglyphdef', 'altglyphitem', 'animatecolor', 'animatemotion', 'animatetransform', 'circle', 'clippath', 'defs', 'desc', 'ellipse', 'filter', 'font', 'g', 'glyph', 'glyphref', 'hkern', 'image', 'line', 'lineargradient', 'marker', 'mask', 'metadata', 'mpath', 'path', 'pattern', 'polygon', 'polyline', 'radialgradient', 'rect', 'stop', 'style', 'switch', 'symbol', 'text', 'textpath', 'title', 'tref', 'tspan', 'view', 'vkern']);
  const svgFilters = freeze(['feBlend', 'feColorMatrix', 'feComponentTransfer', 'feComposite', 'feConvolveMatrix', 'feDiffuseLighting', 'feDisplacementMap', 'feDistantLight', 'feDropShadow', 'feFlood', 'feFuncA', 'feFuncB', 'feFuncG', 'feFuncR', 'feGaussianBlur', 'feImage', 'feMerge', 'feMergeNode', 'feMorphology', 'feOffset', 'fePointLight', 'feSpecularLighting', 'feSpotLight', 'feTile', 'feTurbulence']);
  // List of SVG elements that are disallowed by default.
  // We still need to know them so that we can do namespace
  // checks properly in case one wants to add them to
  // allow-list.
  const svgDisallowed = freeze(['animate', 'color-profile', 'cursor', 'discard', 'font-face', 'font-face-format', 'font-face-name', 'font-face-src', 'font-face-uri', 'foreignobject', 'hatch', 'hatchpath', 'mesh', 'meshgradient', 'meshpatch', 'meshrow', 'missing-glyph', 'script', 'set', 'solidcolor', 'unknown', 'use']);
  const mathMl$1 = freeze(['math', 'menclose', 'merror', 'mfenced', 'mfrac', 'mglyph', 'mi', 'mlabeledtr', 'mmultiscripts', 'mn', 'mo', 'mover', 'mpadded', 'mphantom', 'mroot', 'mrow', 'ms', 'mspace', 'msqrt', 'mstyle', 'msub', 'msup', 'msubsup', 'mtable', 'mtd', 'mtext', 'mtr', 'munder', 'munderover', 'mprescripts']);
  // Similarly to SVG, we want to know all MathML elements,
  // even those that we disallow by default.
  const mathMlDisallowed = freeze(['maction', 'maligngroup', 'malignmark', 'mlongdiv', 'mscarries', 'mscarry', 'msgroup', 'mstack', 'msline', 'msrow', 'semantics', 'annotation', 'annotation-xml', 'mprescripts', 'none']);
  const text = freeze(['#text']);

  const html = freeze(['accept', 'action', 'align', 'alt', 'autocapitalize', 'autocomplete', 'autopictureinpicture', 'autoplay', 'background', 'bgcolor', 'border', 'capture', 'cellpadding', 'cellspacing', 'checked', 'cite', 'class', 'clear', 'color', 'cols', 'colspan', 'controls', 'controlslist', 'coords', 'crossorigin', 'datetime', 'decoding', 'default', 'dir', 'disabled', 'disablepictureinpicture', 'disableremoteplayback', 'download', 'draggable', 'enctype', 'enterkeyhint', 'face', 'for', 'headers', 'height', 'hidden', 'high', 'href', 'hreflang', 'id', 'inputmode', 'integrity', 'ismap', 'kind', 'label', 'lang', 'list', 'loading', 'loop', 'low', 'max', 'maxlength', 'media', 'method', 'min', 'minlength', 'multiple', 'muted', 'name', 'nonce', 'noshade', 'novalidate', 'nowrap', 'open', 'optimum', 'pattern', 'placeholder', 'playsinline', 'popover', 'popovertarget', 'popovertargetaction', 'poster', 'preload', 'pubdate', 'radiogroup', 'readonly', 'rel', 'required', 'rev', 'reversed', 'role', 'rows', 'rowspan', 'spellcheck', 'scope', 'selected', 'shape', 'size', 'sizes', 'span', 'srclang', 'start', 'src', 'srcset', 'step', 'style', 'summary', 'tabindex', 'title', 'translate', 'type', 'usemap', 'valign', 'value', 'width', 'wrap', 'xmlns', 'slot']);
  const svg = freeze(['accent-height', 'accumulate', 'additive', 'alignment-baseline', 'amplitude', 'ascent', 'attributename', 'attributetype', 'azimuth', 'basefrequency', 'baseline-shift', 'begin', 'bias', 'by', 'class', 'clip', 'clippathunits', 'clip-path', 'clip-rule', 'color', 'color-interpolation', 'color-interpolation-filters', 'color-profile', 'color-rendering', 'cx', 'cy', 'd', 'dx', 'dy', 'diffuseconstant', 'direction', 'display', 'divisor', 'dur', 'edgemode', 'elevation', 'end', 'exponent', 'fill', 'fill-opacity', 'fill-rule', 'filter', 'filterunits', 'flood-color', 'flood-opacity', 'font-family', 'font-size', 'font-size-adjust', 'font-stretch', 'font-style', 'font-variant', 'font-weight', 'fx', 'fy', 'g1', 'g2', 'glyph-name', 'glyphref', 'gradientunits', 'gradienttransform', 'height', 'href', 'id', 'image-rendering', 'in', 'in2', 'intercept', 'k', 'k1', 'k2', 'k3', 'k4', 'kerning', 'keypoints', 'keysplines', 'keytimes', 'lang', 'lengthadjust', 'letter-spacing', 'kernelmatrix', 'kernelunitlength', 'lighting-color', 'local', 'marker-end', 'marker-mid', 'marker-start', 'markerheight', 'markerunits', 'markerwidth', 'maskcontentunits', 'maskunits', 'max', 'mask', 'media', 'method', 'mode', 'min', 'name', 'numoctaves', 'offset', 'operator', 'opacity', 'order', 'orient', 'orientation', 'origin', 'overflow', 'paint-order', 'path', 'pathlength', 'patterncontentunits', 'patterntransform', 'patternunits', 'points', 'preservealpha', 'preserveaspectratio', 'primitiveunits', 'r', 'rx', 'ry', 'radius', 'refx', 'refy', 'repeatcount', 'repeatdur', 'restart', 'result', 'rotate', 'scale', 'seed', 'shape-rendering', 'slope', 'specularconstant', 'specularexponent', 'spreadmethod', 'startoffset', 'stddeviation', 'stitchtiles', 'stop-color', 'stop-opacity', 'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit', 'stroke-opacity', 'stroke', 'stroke-width', 'style', 'surfacescale', 'systemlanguage', 'tabindex', 'tablevalues', 'targetx', 'targety', 'transform', 'transform-origin', 'text-anchor', 'text-decoration', 'text-rendering', 'textlength', 'type', 'u1', 'u2', 'unicode', 'values', 'viewbox', 'visibility', 'version', 'vert-adv-y', 'vert-origin-x', 'vert-origin-y', 'width', 'word-spacing', 'wrap', 'writing-mode', 'xchannelselector', 'ychannelselector', 'x', 'x1', 'x2', 'xmlns', 'y', 'y1', 'y2', 'z', 'zoomandpan']);
  const mathMl = freeze(['accent', 'accentunder', 'align', 'bevelled', 'close', 'columnsalign', 'columnlines', 'columnspan', 'denomalign', 'depth', 'dir', 'display', 'displaystyle', 'encoding', 'fence', 'frame', 'height', 'href', 'id', 'largeop', 'length', 'linethickness', 'lspace', 'lquote', 'mathbackground', 'mathcolor', 'mathsize', 'mathvariant', 'maxsize', 'minsize', 'movablelimits', 'notation', 'numalign', 'open', 'rowalign', 'rowlines', 'rowspacing', 'rowspan', 'rspace', 'rquote', 'scriptlevel', 'scriptminsize', 'scriptsizemultiplier', 'selection', 'separator', 'separators', 'stretchy', 'subscriptshift', 'supscriptshift', 'symmetric', 'voffset', 'width', 'xmlns']);
  const xml = freeze(['xlink:href', 'xml:id', 'xlink:title', 'xml:space', 'xmlns:xlink']);

  // eslint-disable-next-line unicorn/better-regex
  const MUSTACHE_EXPR = seal(/\{\{[\w\W]*|[\w\W]*\}\}/gm); // Specify template detection regex for SAFE_FOR_TEMPLATES mode
  const ERB_EXPR = seal(/<%[\w\W]*|[\w\W]*%>/gm);
  const TMPLIT_EXPR = seal(/\${[\w\W]*}/gm);
  const DATA_ATTR = seal(/^data-[\-\w.\u00B7-\uFFFF]/); // eslint-disable-line no-useless-escape
  const ARIA_ATTR = seal(/^aria-[\-\w]+$/); // eslint-disable-line no-useless-escape
  const IS_ALLOWED_URI = seal(/^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i // eslint-disable-line no-useless-escape
  );
  const IS_SCRIPT_OR_DATA = seal(/^(?:\w+script|data):/i);
  const ATTR_WHITESPACE = seal(/[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g // eslint-disable-line no-control-regex
  );
  const DOCTYPE_NAME = seal(/^html$/i);
  const CUSTOM_ELEMENT = seal(/^[a-z][.\w]*(-[.\w]+)+$/i);

  var EXPRESSIONS = /*#__PURE__*/Object.freeze({
    __proto__: null,
    ARIA_ATTR: ARIA_ATTR,
    ATTR_WHITESPACE: ATTR_WHITESPACE,
    CUSTOM_ELEMENT: CUSTOM_ELEMENT,
    DATA_ATTR: DATA_ATTR,
    DOCTYPE_NAME: DOCTYPE_NAME,
    ERB_EXPR: ERB_EXPR,
    IS_ALLOWED_URI: IS_ALLOWED_URI,
    IS_SCRIPT_OR_DATA: IS_SCRIPT_OR_DATA,
    MUSTACHE_EXPR: MUSTACHE_EXPR,
    TMPLIT_EXPR: TMPLIT_EXPR
  });

  /* eslint-disable @typescript-eslint/indent */
  // https://developer.mozilla.org/en-US/docs/Web/API/Node/nodeType
  const NODE_TYPE = {
    element: 1,
    attribute: 2,
    text: 3,
    cdataSection: 4,
    entityReference: 5,
    // Deprecated
    entityNode: 6,
    // Deprecated
    progressingInstruction: 7,
    comment: 8,
    document: 9,
    documentType: 10,
    documentFragment: 11,
    notation: 12 // Deprecated
  };
  const getGlobal = function getGlobal() {
    return typeof window === 'undefined' ? null : window;
  };
  /**
   * Creates a no-op policy for internal use only.
   * Don't export this function outside this module!
   * @param trustedTypes The policy factory.
   * @param purifyHostElement The Script element used to load DOMPurify (to determine policy name suffix).
   * @return The policy created (or null, if Trusted Types
   * are not supported or creating the policy failed).
   */
  const _createTrustedTypesPolicy = function _createTrustedTypesPolicy(trustedTypes, purifyHostElement) {
    if (typeof trustedTypes !== 'object' || typeof trustedTypes.createPolicy !== 'function') {
      return null;
    }
    // Allow the callers to control the unique policy name
    // by adding a data-tt-policy-suffix to the script element with the DOMPurify.
    // Policy creation with duplicate names throws in Trusted Types.
    let suffix = null;
    const ATTR_NAME = 'data-tt-policy-suffix';
    if (purifyHostElement && purifyHostElement.hasAttribute(ATTR_NAME)) {
      suffix = purifyHostElement.getAttribute(ATTR_NAME);
    }
    const policyName = 'dompurify' + (suffix ? '#' + suffix : '');
    try {
      return trustedTypes.createPolicy(policyName, {
        createHTML(html) {
          return html;
        },
        createScriptURL(scriptUrl) {
          return scriptUrl;
        }
      });
    } catch (_) {
      // Policy creation failed (most likely another DOMPurify script has
      // already run). Skip creating the policy, as this will only cause errors
      // if TT are enforced.
      console.warn('TrustedTypes policy ' + policyName + ' could not be created.');
      return null;
    }
  };
  const _createHooksMap = function _createHooksMap() {
    return {
      afterSanitizeAttributes: [],
      afterSanitizeElements: [],
      afterSanitizeShadowDOM: [],
      beforeSanitizeAttributes: [],
      beforeSanitizeElements: [],
      beforeSanitizeShadowDOM: [],
      uponSanitizeAttribute: [],
      uponSanitizeElement: [],
      uponSanitizeShadowNode: []
    };
  };
  function createDOMPurify() {
    let window = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : getGlobal();
    const DOMPurify = root => createDOMPurify(root);
    DOMPurify.version = '3.2.2';
    DOMPurify.removed = [];
    if (!window || !window.document || window.document.nodeType !== NODE_TYPE.document) {
      // Not running in a browser, provide a factory function
      // so that you can pass your own Window
      DOMPurify.isSupported = false;
      return DOMPurify;
    }
    let {
      document
    } = window;
    const originalDocument = document;
    const currentScript = originalDocument.currentScript;
    const {
      DocumentFragment,
      HTMLTemplateElement,
      Node,
      Element,
      NodeFilter,
      NamedNodeMap = window.NamedNodeMap || window.MozNamedAttrMap,
      HTMLFormElement,
      DOMParser,
      trustedTypes
    } = window;
    const ElementPrototype = Element.prototype;
    const cloneNode = lookupGetter(ElementPrototype, 'cloneNode');
    const remove = lookupGetter(ElementPrototype, 'remove');
    const getNextSibling = lookupGetter(ElementPrototype, 'nextSibling');
    const getChildNodes = lookupGetter(ElementPrototype, 'childNodes');
    const getParentNode = lookupGetter(ElementPrototype, 'parentNode');
    // As per issue #47, the web-components registry is inherited by a
    // new document created via createHTMLDocument. As per the spec
    // (http://w3c.github.io/webcomponents/spec/custom/#creating-and-passing-registries)
    // a new empty registry is used when creating a template contents owner
    // document, so we use that as our parent document to ensure nothing
    // is inherited.
    if (typeof HTMLTemplateElement === 'function') {
      const template = document.createElement('template');
      if (template.content && template.content.ownerDocument) {
        document = template.content.ownerDocument;
      }
    }
    let trustedTypesPolicy;
    let emptyHTML = '';
    const {
      implementation,
      createNodeIterator,
      createDocumentFragment,
      getElementsByTagName
    } = document;
    const {
      importNode
    } = originalDocument;
    let hooks = _createHooksMap();
    /**
     * Expose whether this browser supports running the full DOMPurify.
     */
    DOMPurify.isSupported = typeof entries === 'function' && typeof getParentNode === 'function' && implementation && implementation.createHTMLDocument !== undefined;
    const {
      MUSTACHE_EXPR,
      ERB_EXPR,
      TMPLIT_EXPR,
      DATA_ATTR,
      ARIA_ATTR,
      IS_SCRIPT_OR_DATA,
      ATTR_WHITESPACE,
      CUSTOM_ELEMENT
    } = EXPRESSIONS;
    let {
      IS_ALLOWED_URI: IS_ALLOWED_URI$1
    } = EXPRESSIONS;
    /**
     * We consider the elements and attributes below to be safe. Ideally
     * don't add any new ones but feel free to remove unwanted ones.
     */
    /* allowed element names */
    let ALLOWED_TAGS = null;
    const DEFAULT_ALLOWED_TAGS = addToSet({}, [...html$1, ...svg$1, ...svgFilters, ...mathMl$1, ...text]);
    /* Allowed attribute names */
    let ALLOWED_ATTR = null;
    const DEFAULT_ALLOWED_ATTR = addToSet({}, [...html, ...svg, ...mathMl, ...xml]);
    /*
     * Configure how DOMPurify should handle custom elements and their attributes as well as customized built-in elements.
     * @property {RegExp|Function|null} tagNameCheck one of [null, regexPattern, predicate]. Default: `null` (disallow any custom elements)
     * @property {RegExp|Function|null} attributeNameCheck one of [null, regexPattern, predicate]. Default: `null` (disallow any attributes not on the allow list)
     * @property {boolean} allowCustomizedBuiltInElements allow custom elements derived from built-ins if they pass CUSTOM_ELEMENT_HANDLING.tagNameCheck. Default: `false`.
     */
    let CUSTOM_ELEMENT_HANDLING = Object.seal(create(null, {
      tagNameCheck: {
        writable: true,
        configurable: false,
        enumerable: true,
        value: null
      },
      attributeNameCheck: {
        writable: true,
        configurable: false,
        enumerable: true,
        value: null
      },
      allowCustomizedBuiltInElements: {
        writable: true,
        configurable: false,
        enumerable: true,
        value: false
      }
    }));
    /* Explicitly forbidden tags (overrides ALLOWED_TAGS/ADD_TAGS) */
    let FORBID_TAGS = null;
    /* Explicitly forbidden attributes (overrides ALLOWED_ATTR/ADD_ATTR) */
    let FORBID_ATTR = null;
    /* Decide if ARIA attributes are okay */
    let ALLOW_ARIA_ATTR = true;
    /* Decide if custom data attributes are okay */
    let ALLOW_DATA_ATTR = true;
    /* Decide if unknown protocols are okay */
    let ALLOW_UNKNOWN_PROTOCOLS = false;
    /* Decide if self-closing tags in attributes are allowed.
     * Usually removed due to a mXSS issue in jQuery 3.0 */
    let ALLOW_SELF_CLOSE_IN_ATTR = true;
    /* Output should be safe for common template engines.
     * This means, DOMPurify removes data attributes, mustaches and ERB
     */
    let SAFE_FOR_TEMPLATES = false;
    /* Output should be safe even for XML used within HTML and alike.
     * This means, DOMPurify removes comments when containing risky content.
     */
    let SAFE_FOR_XML = true;
    /* Decide if document with <html>... should be returned */
    let WHOLE_DOCUMENT = false;
    /* Track whether config is already set on this instance of DOMPurify. */
    let SET_CONFIG = false;
    /* Decide if all elements (e.g. style, script) must be children of
     * document.body. By default, browsers might move them to document.head */
    let FORCE_BODY = false;
    /* Decide if a DOM `HTMLBodyElement` should be returned, instead of a html
     * string (or a TrustedHTML object if Trusted Types are supported).
     * If `WHOLE_DOCUMENT` is enabled a `HTMLHtmlElement` will be returned instead
     */
    let RETURN_DOM = false;
    /* Decide if a DOM `DocumentFragment` should be returned, instead of a html
     * string  (or a TrustedHTML object if Trusted Types are supported) */
    let RETURN_DOM_FRAGMENT = false;
    /* Try to return a Trusted Type object instead of a string, return a string in
     * case Trusted Types are not supported  */
    let RETURN_TRUSTED_TYPE = false;
    /* Output should be free from DOM clobbering attacks?
     * This sanitizes markups named with colliding, clobberable built-in DOM APIs.
     */
    let SANITIZE_DOM = true;
    /* Achieve full DOM Clobbering protection by isolating the namespace of named
     * properties and JS variables, mitigating attacks that abuse the HTML/DOM spec rules.
     *
     * HTML/DOM spec rules that enable DOM Clobbering:
     *   - Named Access on Window (§7.3.3)
     *   - DOM Tree Accessors (§3.1.5)
     *   - Form Element Parent-Child Relations (§4.10.3)
     *   - Iframe srcdoc / Nested WindowProxies (§4.8.5)
     *   - HTMLCollection (§4.2.10.2)
     *
     * Namespace isolation is implemented by prefixing `id` and `name` attributes
     * with a constant string, i.e., `user-content-`
     */
    let SANITIZE_NAMED_PROPS = false;
    const SANITIZE_NAMED_PROPS_PREFIX = 'user-content-';
    /* Keep element content when removing element? */
    let KEEP_CONTENT = true;
    /* If a `Node` is passed to sanitize(), then performs sanitization in-place instead
     * of importing it into a new Document and returning a sanitized copy */
    let IN_PLACE = false;
    /* Allow usage of profiles like html, svg and mathMl */
    let USE_PROFILES = {};
    /* Tags to ignore content of when KEEP_CONTENT is true */
    let FORBID_CONTENTS = null;
    const DEFAULT_FORBID_CONTENTS = addToSet({}, ['annotation-xml', 'audio', 'colgroup', 'desc', 'foreignobject', 'head', 'iframe', 'math', 'mi', 'mn', 'mo', 'ms', 'mtext', 'noembed', 'noframes', 'noscript', 'plaintext', 'script', 'style', 'svg', 'template', 'thead', 'title', 'video', 'xmp']);
    /* Tags that are safe for data: URIs */
    let DATA_URI_TAGS = null;
    const DEFAULT_DATA_URI_TAGS = addToSet({}, ['audio', 'video', 'img', 'source', 'image', 'track']);
    /* Attributes safe for values like "javascript:" */
    let URI_SAFE_ATTRIBUTES = null;
    const DEFAULT_URI_SAFE_ATTRIBUTES = addToSet({}, ['alt', 'class', 'for', 'id', 'label', 'name', 'pattern', 'placeholder', 'role', 'summary', 'title', 'value', 'style', 'xmlns']);
    const MATHML_NAMESPACE = 'http://www.w3.org/1998/Math/MathML';
    const SVG_NAMESPACE = 'http://www.w3.org/2000/svg';
    const HTML_NAMESPACE = 'http://www.w3.org/1999/xhtml';
    /* Document namespace */
    let NAMESPACE = HTML_NAMESPACE;
    let IS_EMPTY_INPUT = false;
    /* Allowed XHTML+XML namespaces */
    let ALLOWED_NAMESPACES = null;
    const DEFAULT_ALLOWED_NAMESPACES = addToSet({}, [MATHML_NAMESPACE, SVG_NAMESPACE, HTML_NAMESPACE], stringToString);
    let MATHML_TEXT_INTEGRATION_POINTS = addToSet({}, ['mi', 'mo', 'mn', 'ms', 'mtext']);
    let HTML_INTEGRATION_POINTS = addToSet({}, ['annotation-xml']);
    // Certain elements are allowed in both SVG and HTML
    // namespace. We need to specify them explicitly
    // so that they don't get erroneously deleted from
    // HTML namespace.
    const COMMON_SVG_AND_HTML_ELEMENTS = addToSet({}, ['title', 'style', 'font', 'a', 'script']);
    /* Parsing of strict XHTML documents */
    let PARSER_MEDIA_TYPE = null;
    const SUPPORTED_PARSER_MEDIA_TYPES = ['application/xhtml+xml', 'text/html'];
    const DEFAULT_PARSER_MEDIA_TYPE = 'text/html';
    let transformCaseFunc = null;
    /* Keep a reference to config to pass to hooks */
    let CONFIG = null;
    /* Ideally, do not touch anything below this line */
    /* ______________________________________________ */
    const formElement = document.createElement('form');
    const isRegexOrFunction = function isRegexOrFunction(testValue) {
      return testValue instanceof RegExp || testValue instanceof Function;
    };
    /**
     * _parseConfig
     *
     * @param cfg optional config literal
     */
    // eslint-disable-next-line complexity
    const _parseConfig = function _parseConfig() {
      let cfg = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (CONFIG && CONFIG === cfg) {
        return;
      }
      /* Shield configuration object from tampering */
      if (!cfg || typeof cfg !== 'object') {
        cfg = {};
      }
      /* Shield configuration object from prototype pollution */
      cfg = clone(cfg);
      PARSER_MEDIA_TYPE =
      // eslint-disable-next-line unicorn/prefer-includes
      SUPPORTED_PARSER_MEDIA_TYPES.indexOf(cfg.PARSER_MEDIA_TYPE) === -1 ? DEFAULT_PARSER_MEDIA_TYPE : cfg.PARSER_MEDIA_TYPE;
      // HTML tags and attributes are not case-sensitive, converting to lowercase. Keeping XHTML as is.
      transformCaseFunc = PARSER_MEDIA_TYPE === 'application/xhtml+xml' ? stringToString : stringToLowerCase;
      /* Set configuration parameters */
      ALLOWED_TAGS = objectHasOwnProperty(cfg, 'ALLOWED_TAGS') ? addToSet({}, cfg.ALLOWED_TAGS, transformCaseFunc) : DEFAULT_ALLOWED_TAGS;
      ALLOWED_ATTR = objectHasOwnProperty(cfg, 'ALLOWED_ATTR') ? addToSet({}, cfg.ALLOWED_ATTR, transformCaseFunc) : DEFAULT_ALLOWED_ATTR;
      ALLOWED_NAMESPACES = objectHasOwnProperty(cfg, 'ALLOWED_NAMESPACES') ? addToSet({}, cfg.ALLOWED_NAMESPACES, stringToString) : DEFAULT_ALLOWED_NAMESPACES;
      URI_SAFE_ATTRIBUTES = objectHasOwnProperty(cfg, 'ADD_URI_SAFE_ATTR') ? addToSet(clone(DEFAULT_URI_SAFE_ATTRIBUTES), cfg.ADD_URI_SAFE_ATTR, transformCaseFunc) : DEFAULT_URI_SAFE_ATTRIBUTES;
      DATA_URI_TAGS = objectHasOwnProperty(cfg, 'ADD_DATA_URI_TAGS') ? addToSet(clone(DEFAULT_DATA_URI_TAGS), cfg.ADD_DATA_URI_TAGS, transformCaseFunc) : DEFAULT_DATA_URI_TAGS;
      FORBID_CONTENTS = objectHasOwnProperty(cfg, 'FORBID_CONTENTS') ? addToSet({}, cfg.FORBID_CONTENTS, transformCaseFunc) : DEFAULT_FORBID_CONTENTS;
      FORBID_TAGS = objectHasOwnProperty(cfg, 'FORBID_TAGS') ? addToSet({}, cfg.FORBID_TAGS, transformCaseFunc) : {};
      FORBID_ATTR = objectHasOwnProperty(cfg, 'FORBID_ATTR') ? addToSet({}, cfg.FORBID_ATTR, transformCaseFunc) : {};
      USE_PROFILES = objectHasOwnProperty(cfg, 'USE_PROFILES') ? cfg.USE_PROFILES : false;
      ALLOW_ARIA_ATTR = cfg.ALLOW_ARIA_ATTR !== false; // Default true
      ALLOW_DATA_ATTR = cfg.ALLOW_DATA_ATTR !== false; // Default true
      ALLOW_UNKNOWN_PROTOCOLS = cfg.ALLOW_UNKNOWN_PROTOCOLS || false; // Default false
      ALLOW_SELF_CLOSE_IN_ATTR = cfg.ALLOW_SELF_CLOSE_IN_ATTR !== false; // Default true
      SAFE_FOR_TEMPLATES = cfg.SAFE_FOR_TEMPLATES || false; // Default false
      SAFE_FOR_XML = cfg.SAFE_FOR_XML !== false; // Default true
      WHOLE_DOCUMENT = cfg.WHOLE_DOCUMENT || false; // Default false
      RETURN_DOM = cfg.RETURN_DOM || false; // Default false
      RETURN_DOM_FRAGMENT = cfg.RETURN_DOM_FRAGMENT || false; // Default false
      RETURN_TRUSTED_TYPE = cfg.RETURN_TRUSTED_TYPE || false; // Default false
      FORCE_BODY = cfg.FORCE_BODY || false; // Default false
      SANITIZE_DOM = cfg.SANITIZE_DOM !== false; // Default true
      SANITIZE_NAMED_PROPS = cfg.SANITIZE_NAMED_PROPS || false; // Default false
      KEEP_CONTENT = cfg.KEEP_CONTENT !== false; // Default true
      IN_PLACE = cfg.IN_PLACE || false; // Default false
      IS_ALLOWED_URI$1 = cfg.ALLOWED_URI_REGEXP || IS_ALLOWED_URI;
      NAMESPACE = cfg.NAMESPACE || HTML_NAMESPACE;
      MATHML_TEXT_INTEGRATION_POINTS = cfg.MATHML_TEXT_INTEGRATION_POINTS || MATHML_TEXT_INTEGRATION_POINTS;
      HTML_INTEGRATION_POINTS = cfg.HTML_INTEGRATION_POINTS || HTML_INTEGRATION_POINTS;
      CUSTOM_ELEMENT_HANDLING = cfg.CUSTOM_ELEMENT_HANDLING || {};
      if (cfg.CUSTOM_ELEMENT_HANDLING && isRegexOrFunction(cfg.CUSTOM_ELEMENT_HANDLING.tagNameCheck)) {
        CUSTOM_ELEMENT_HANDLING.tagNameCheck = cfg.CUSTOM_ELEMENT_HANDLING.tagNameCheck;
      }
      if (cfg.CUSTOM_ELEMENT_HANDLING && isRegexOrFunction(cfg.CUSTOM_ELEMENT_HANDLING.attributeNameCheck)) {
        CUSTOM_ELEMENT_HANDLING.attributeNameCheck = cfg.CUSTOM_ELEMENT_HANDLING.attributeNameCheck;
      }
      if (cfg.CUSTOM_ELEMENT_HANDLING && typeof cfg.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements === 'boolean') {
        CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements = cfg.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements;
      }
      if (SAFE_FOR_TEMPLATES) {
        ALLOW_DATA_ATTR = false;
      }
      if (RETURN_DOM_FRAGMENT) {
        RETURN_DOM = true;
      }
      /* Parse profile info */
      if (USE_PROFILES) {
        ALLOWED_TAGS = addToSet({}, text);
        ALLOWED_ATTR = [];
        if (USE_PROFILES.html === true) {
          addToSet(ALLOWED_TAGS, html$1);
          addToSet(ALLOWED_ATTR, html);
        }
        if (USE_PROFILES.svg === true) {
          addToSet(ALLOWED_TAGS, svg$1);
          addToSet(ALLOWED_ATTR, svg);
          addToSet(ALLOWED_ATTR, xml);
        }
        if (USE_PROFILES.svgFilters === true) {
          addToSet(ALLOWED_TAGS, svgFilters);
          addToSet(ALLOWED_ATTR, svg);
          addToSet(ALLOWED_ATTR, xml);
        }
        if (USE_PROFILES.mathMl === true) {
          addToSet(ALLOWED_TAGS, mathMl$1);
          addToSet(ALLOWED_ATTR, mathMl);
          addToSet(ALLOWED_ATTR, xml);
        }
      }
      /* Merge configuration parameters */
      if (cfg.ADD_TAGS) {
        if (ALLOWED_TAGS === DEFAULT_ALLOWED_TAGS) {
          ALLOWED_TAGS = clone(ALLOWED_TAGS);
        }
        addToSet(ALLOWED_TAGS, cfg.ADD_TAGS, transformCaseFunc);
      }
      if (cfg.ADD_ATTR) {
        if (ALLOWED_ATTR === DEFAULT_ALLOWED_ATTR) {
          ALLOWED_ATTR = clone(ALLOWED_ATTR);
        }
        addToSet(ALLOWED_ATTR, cfg.ADD_ATTR, transformCaseFunc);
      }
      if (cfg.ADD_URI_SAFE_ATTR) {
        addToSet(URI_SAFE_ATTRIBUTES, cfg.ADD_URI_SAFE_ATTR, transformCaseFunc);
      }
      if (cfg.FORBID_CONTENTS) {
        if (FORBID_CONTENTS === DEFAULT_FORBID_CONTENTS) {
          FORBID_CONTENTS = clone(FORBID_CONTENTS);
        }
        addToSet(FORBID_CONTENTS, cfg.FORBID_CONTENTS, transformCaseFunc);
      }
      /* Add #text in case KEEP_CONTENT is set to true */
      if (KEEP_CONTENT) {
        ALLOWED_TAGS['#text'] = true;
      }
      /* Add html, head and body to ALLOWED_TAGS in case WHOLE_DOCUMENT is true */
      if (WHOLE_DOCUMENT) {
        addToSet(ALLOWED_TAGS, ['html', 'head', 'body']);
      }
      /* Add tbody to ALLOWED_TAGS in case tables are permitted, see #286, #365 */
      if (ALLOWED_TAGS.table) {
        addToSet(ALLOWED_TAGS, ['tbody']);
        delete FORBID_TAGS.tbody;
      }
      if (cfg.TRUSTED_TYPES_POLICY) {
        if (typeof cfg.TRUSTED_TYPES_POLICY.createHTML !== 'function') {
          throw typeErrorCreate('TRUSTED_TYPES_POLICY configuration option must provide a "createHTML" hook.');
        }
        if (typeof cfg.TRUSTED_TYPES_POLICY.createScriptURL !== 'function') {
          throw typeErrorCreate('TRUSTED_TYPES_POLICY configuration option must provide a "createScriptURL" hook.');
        }
        // Overwrite existing TrustedTypes policy.
        trustedTypesPolicy = cfg.TRUSTED_TYPES_POLICY;
        // Sign local variables required by `sanitize`.
        emptyHTML = trustedTypesPolicy.createHTML('');
      } else {
        // Uninitialized policy, attempt to initialize the internal dompurify policy.
        if (trustedTypesPolicy === undefined) {
          trustedTypesPolicy = _createTrustedTypesPolicy(trustedTypes, currentScript);
        }
        // If creating the internal policy succeeded sign internal variables.
        if (trustedTypesPolicy !== null && typeof emptyHTML === 'string') {
          emptyHTML = trustedTypesPolicy.createHTML('');
        }
      }
      // Prevent further manipulation of configuration.
      // Not available in IE8, Safari 5, etc.
      if (freeze) {
        freeze(cfg);
      }
      CONFIG = cfg;
    };
    /* Keep track of all possible SVG and MathML tags
     * so that we can perform the namespace checks
     * correctly. */
    const ALL_SVG_TAGS = addToSet({}, [...svg$1, ...svgFilters, ...svgDisallowed]);
    const ALL_MATHML_TAGS = addToSet({}, [...mathMl$1, ...mathMlDisallowed]);
    /**
     * @param element a DOM element whose namespace is being checked
     * @returns Return false if the element has a
     *  namespace that a spec-compliant parser would never
     *  return. Return true otherwise.
     */
    const _checkValidNamespace = function _checkValidNamespace(element) {
      let parent = getParentNode(element);
      // In JSDOM, if we're inside shadow DOM, then parentNode
      // can be null. We just simulate parent in this case.
      if (!parent || !parent.tagName) {
        parent = {
          namespaceURI: NAMESPACE,
          tagName: 'template'
        };
      }
      const tagName = stringToLowerCase(element.tagName);
      const parentTagName = stringToLowerCase(parent.tagName);
      if (!ALLOWED_NAMESPACES[element.namespaceURI]) {
        return false;
      }
      if (element.namespaceURI === SVG_NAMESPACE) {
        // The only way to switch from HTML namespace to SVG
        // is via <svg>. If it happens via any other tag, then
        // it should be killed.
        if (parent.namespaceURI === HTML_NAMESPACE) {
          return tagName === 'svg';
        }
        // The only way to switch from MathML to SVG is via`
        // svg if parent is either <annotation-xml> or MathML
        // text integration points.
        if (parent.namespaceURI === MATHML_NAMESPACE) {
          return tagName === 'svg' && (parentTagName === 'annotation-xml' || MATHML_TEXT_INTEGRATION_POINTS[parentTagName]);
        }
        // We only allow elements that are defined in SVG
        // spec. All others are disallowed in SVG namespace.
        return Boolean(ALL_SVG_TAGS[tagName]);
      }
      if (element.namespaceURI === MATHML_NAMESPACE) {
        // The only way to switch from HTML namespace to MathML
        // is via <math>. If it happens via any other tag, then
        // it should be killed.
        if (parent.namespaceURI === HTML_NAMESPACE) {
          return tagName === 'math';
        }
        // The only way to switch from SVG to MathML is via
        // <math> and HTML integration points
        if (parent.namespaceURI === SVG_NAMESPACE) {
          return tagName === 'math' && HTML_INTEGRATION_POINTS[parentTagName];
        }
        // We only allow elements that are defined in MathML
        // spec. All others are disallowed in MathML namespace.
        return Boolean(ALL_MATHML_TAGS[tagName]);
      }
      if (element.namespaceURI === HTML_NAMESPACE) {
        // The only way to switch from SVG to HTML is via
        // HTML integration points, and from MathML to HTML
        // is via MathML text integration points
        if (parent.namespaceURI === SVG_NAMESPACE && !HTML_INTEGRATION_POINTS[parentTagName]) {
          return false;
        }
        if (parent.namespaceURI === MATHML_NAMESPACE && !MATHML_TEXT_INTEGRATION_POINTS[parentTagName]) {
          return false;
        }
        // We disallow tags that are specific for MathML
        // or SVG and should never appear in HTML namespace
        return !ALL_MATHML_TAGS[tagName] && (COMMON_SVG_AND_HTML_ELEMENTS[tagName] || !ALL_SVG_TAGS[tagName]);
      }
      // For XHTML and XML documents that support custom namespaces
      if (PARSER_MEDIA_TYPE === 'application/xhtml+xml' && ALLOWED_NAMESPACES[element.namespaceURI]) {
        return true;
      }
      // The code should never reach this place (this means
      // that the element somehow got namespace that is not
      // HTML, SVG, MathML or allowed via ALLOWED_NAMESPACES).
      // Return false just in case.
      return false;
    };
    /**
     * _forceRemove
     *
     * @param node a DOM node
     */
    const _forceRemove = function _forceRemove(node) {
      arrayPush(DOMPurify.removed, {
        element: node
      });
      try {
        // eslint-disable-next-line unicorn/prefer-dom-node-remove
        getParentNode(node).removeChild(node);
      } catch (_) {
        remove(node);
      }
    };
    /**
     * _removeAttribute
     *
     * @param name an Attribute name
     * @param element a DOM node
     */
    const _removeAttribute = function _removeAttribute(name, element) {
      try {
        arrayPush(DOMPurify.removed, {
          attribute: element.getAttributeNode(name),
          from: element
        });
      } catch (_) {
        arrayPush(DOMPurify.removed, {
          attribute: null,
          from: element
        });
      }
      element.removeAttribute(name);
      // We void attribute values for unremovable "is" attributes
      if (name === 'is') {
        if (RETURN_DOM || RETURN_DOM_FRAGMENT) {
          try {
            _forceRemove(element);
          } catch (_) {}
        } else {
          try {
            element.setAttribute(name, '');
          } catch (_) {}
        }
      }
    };
    /**
     * _initDocument
     *
     * @param dirty - a string of dirty markup
     * @return a DOM, filled with the dirty markup
     */
    const _initDocument = function _initDocument(dirty) {
      /* Create a HTML document */
      let doc = null;
      let leadingWhitespace = null;
      if (FORCE_BODY) {
        dirty = '<remove></remove>' + dirty;
      } else {
        /* If FORCE_BODY isn't used, leading whitespace needs to be preserved manually */
        const matches = stringMatch(dirty, /^[\r\n\t ]+/);
        leadingWhitespace = matches && matches[0];
      }
      if (PARSER_MEDIA_TYPE === 'application/xhtml+xml' && NAMESPACE === HTML_NAMESPACE) {
        // Root of XHTML doc must contain xmlns declaration (see https://www.w3.org/TR/xhtml1/normative.html#strict)
        dirty = '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>' + dirty + '</body></html>';
      }
      const dirtyPayload = trustedTypesPolicy ? trustedTypesPolicy.createHTML(dirty) : dirty;
      /*
       * Use the DOMParser API by default, fallback later if needs be
       * DOMParser not work for svg when has multiple root element.
       */
      if (NAMESPACE === HTML_NAMESPACE) {
        try {
          doc = new DOMParser().parseFromString(dirtyPayload, PARSER_MEDIA_TYPE);
        } catch (_) {}
      }
      /* Use createHTMLDocument in case DOMParser is not available */
      if (!doc || !doc.documentElement) {
        doc = implementation.createDocument(NAMESPACE, 'template', null);
        try {
          doc.documentElement.innerHTML = IS_EMPTY_INPUT ? emptyHTML : dirtyPayload;
        } catch (_) {
          // Syntax error if dirtyPayload is invalid xml
        }
      }
      const body = doc.body || doc.documentElement;
      if (dirty && leadingWhitespace) {
        body.insertBefore(document.createTextNode(leadingWhitespace), body.childNodes[0] || null);
      }
      /* Work on whole document or just its body */
      if (NAMESPACE === HTML_NAMESPACE) {
        return getElementsByTagName.call(doc, WHOLE_DOCUMENT ? 'html' : 'body')[0];
      }
      return WHOLE_DOCUMENT ? doc.documentElement : body;
    };
    /**
     * Creates a NodeIterator object that you can use to traverse filtered lists of nodes or elements in a document.
     *
     * @param root The root element or node to start traversing on.
     * @return The created NodeIterator
     */
    const _createNodeIterator = function _createNodeIterator(root) {
      return createNodeIterator.call(root.ownerDocument || root, root,
      // eslint-disable-next-line no-bitwise
      NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_COMMENT | NodeFilter.SHOW_TEXT | NodeFilter.SHOW_PROCESSING_INSTRUCTION | NodeFilter.SHOW_CDATA_SECTION, null);
    };
    /**
     * _isClobbered
     *
     * @param element element to check for clobbering attacks
     * @return true if clobbered, false if safe
     */
    const _isClobbered = function _isClobbered(element) {
      return element instanceof HTMLFormElement && (typeof element.nodeName !== 'string' || typeof element.textContent !== 'string' || typeof element.removeChild !== 'function' || !(element.attributes instanceof NamedNodeMap) || typeof element.removeAttribute !== 'function' || typeof element.setAttribute !== 'function' || typeof element.namespaceURI !== 'string' || typeof element.insertBefore !== 'function' || typeof element.hasChildNodes !== 'function');
    };
    /**
     * Checks whether the given object is a DOM node.
     *
     * @param value object to check whether it's a DOM node
     * @return true is object is a DOM node
     */
    const _isNode = function _isNode(value) {
      return typeof Node === 'function' && value instanceof Node;
    };
    function _executeHooks(hooks, currentNode, data) {
      arrayForEach(hooks, hook => {
        hook.call(DOMPurify, currentNode, data, CONFIG);
      });
    }
    /**
     * _sanitizeElements
     *
     * @protect nodeName
     * @protect textContent
     * @protect removeChild
     * @param currentNode to check for permission to exist
     * @return true if node was killed, false if left alive
     */
    const _sanitizeElements = function _sanitizeElements(currentNode) {
      let content = null;
      /* Execute a hook if present */
      _executeHooks(hooks.beforeSanitizeElements, currentNode, null);
      /* Check if element is clobbered or can clobber */
      if (_isClobbered(currentNode)) {
        _forceRemove(currentNode);
        return true;
      }
      /* Now let's check the element's type and name */
      const tagName = transformCaseFunc(currentNode.nodeName);
      /* Execute a hook if present */
      _executeHooks(hooks.uponSanitizeElement, currentNode, {
        tagName,
        allowedTags: ALLOWED_TAGS
      });
      /* Detect mXSS attempts abusing namespace confusion */
      if (currentNode.hasChildNodes() && !_isNode(currentNode.firstElementChild) && regExpTest(/<[/\w]/g, currentNode.innerHTML) && regExpTest(/<[/\w]/g, currentNode.textContent)) {
        _forceRemove(currentNode);
        return true;
      }
      /* Remove any occurrence of processing instructions */
      if (currentNode.nodeType === NODE_TYPE.progressingInstruction) {
        _forceRemove(currentNode);
        return true;
      }
      /* Remove any kind of possibly harmful comments */
      if (SAFE_FOR_XML && currentNode.nodeType === NODE_TYPE.comment && regExpTest(/<[/\w]/g, currentNode.data)) {
        _forceRemove(currentNode);
        return true;
      }
      /* Remove element if anything forbids its presence */
      if (!ALLOWED_TAGS[tagName] || FORBID_TAGS[tagName]) {
        /* Check if we have a custom element to handle */
        if (!FORBID_TAGS[tagName] && _isBasicCustomElement(tagName)) {
          if (CUSTOM_ELEMENT_HANDLING.tagNameCheck instanceof RegExp && regExpTest(CUSTOM_ELEMENT_HANDLING.tagNameCheck, tagName)) {
            return false;
          }
          if (CUSTOM_ELEMENT_HANDLING.tagNameCheck instanceof Function && CUSTOM_ELEMENT_HANDLING.tagNameCheck(tagName)) {
            return false;
          }
        }
        /* Keep content except for bad-listed elements */
        if (KEEP_CONTENT && !FORBID_CONTENTS[tagName]) {
          const parentNode = getParentNode(currentNode) || currentNode.parentNode;
          const childNodes = getChildNodes(currentNode) || currentNode.childNodes;
          if (childNodes && parentNode) {
            const childCount = childNodes.length;
            for (let i = childCount - 1; i >= 0; --i) {
              const childClone = cloneNode(childNodes[i], true);
              childClone.__removalCount = (currentNode.__removalCount || 0) + 1;
              parentNode.insertBefore(childClone, getNextSibling(currentNode));
            }
          }
        }
        _forceRemove(currentNode);
        return true;
      }
      /* Check whether element has a valid namespace */
      if (currentNode instanceof Element && !_checkValidNamespace(currentNode)) {
        _forceRemove(currentNode);
        return true;
      }
      /* Make sure that older browsers don't get fallback-tag mXSS */
      if ((tagName === 'noscript' || tagName === 'noembed' || tagName === 'noframes') && regExpTest(/<\/no(script|embed|frames)/i, currentNode.innerHTML)) {
        _forceRemove(currentNode);
        return true;
      }
      /* Sanitize element content to be template-safe */
      if (SAFE_FOR_TEMPLATES && currentNode.nodeType === NODE_TYPE.text) {
        /* Get the element's text content */
        content = currentNode.textContent;
        arrayForEach([MUSTACHE_EXPR, ERB_EXPR, TMPLIT_EXPR], expr => {
          content = stringReplace(content, expr, ' ');
        });
        if (currentNode.textContent !== content) {
          arrayPush(DOMPurify.removed, {
            element: currentNode.cloneNode()
          });
          currentNode.textContent = content;
        }
      }
      /* Execute a hook if present */
      _executeHooks(hooks.afterSanitizeElements, currentNode, null);
      return false;
    };
    /**
     * _isValidAttribute
     *
     * @param lcTag Lowercase tag name of containing element.
     * @param lcName Lowercase attribute name.
     * @param value Attribute value.
     * @return Returns true if `value` is valid, otherwise false.
     */
    // eslint-disable-next-line complexity
    const _isValidAttribute = function _isValidAttribute(lcTag, lcName, value) {
      /* Make sure attribute cannot clobber */
      if (SANITIZE_DOM && (lcName === 'id' || lcName === 'name') && (value in document || value in formElement)) {
        return false;
      }
      /* Allow valid data-* attributes: At least one character after "-"
          (https://html.spec.whatwg.org/multipage/dom.html#embedding-custom-non-visible-data-with-the-data-*-attributes)
          XML-compatible (https://html.spec.whatwg.org/multipage/infrastructure.html#xml-compatible and http://www.w3.org/TR/xml/#d0e804)
          We don't need to check the value; it's always URI safe. */
      if (ALLOW_DATA_ATTR && !FORBID_ATTR[lcName] && regExpTest(DATA_ATTR, lcName)) ; else if (ALLOW_ARIA_ATTR && regExpTest(ARIA_ATTR, lcName)) ; else if (!ALLOWED_ATTR[lcName] || FORBID_ATTR[lcName]) {
        if (
        // First condition does a very basic check if a) it's basically a valid custom element tagname AND
        // b) if the tagName passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
        // and c) if the attribute name passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.attributeNameCheck
        _isBasicCustomElement(lcTag) && (CUSTOM_ELEMENT_HANDLING.tagNameCheck instanceof RegExp && regExpTest(CUSTOM_ELEMENT_HANDLING.tagNameCheck, lcTag) || CUSTOM_ELEMENT_HANDLING.tagNameCheck instanceof Function && CUSTOM_ELEMENT_HANDLING.tagNameCheck(lcTag)) && (CUSTOM_ELEMENT_HANDLING.attributeNameCheck instanceof RegExp && regExpTest(CUSTOM_ELEMENT_HANDLING.attributeNameCheck, lcName) || CUSTOM_ELEMENT_HANDLING.attributeNameCheck instanceof Function && CUSTOM_ELEMENT_HANDLING.attributeNameCheck(lcName)) ||
        // Alternative, second condition checks if it's an `is`-attribute, AND
        // the value passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
        lcName === 'is' && CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements && (CUSTOM_ELEMENT_HANDLING.tagNameCheck instanceof RegExp && regExpTest(CUSTOM_ELEMENT_HANDLING.tagNameCheck, value) || CUSTOM_ELEMENT_HANDLING.tagNameCheck instanceof Function && CUSTOM_ELEMENT_HANDLING.tagNameCheck(value))) ; else {
          return false;
        }
        /* Check value is safe. First, is attr inert? If so, is safe */
      } else if (URI_SAFE_ATTRIBUTES[lcName]) ; else if (regExpTest(IS_ALLOWED_URI$1, stringReplace(value, ATTR_WHITESPACE, ''))) ; else if ((lcName === 'src' || lcName === 'xlink:href' || lcName === 'href') && lcTag !== 'script' && stringIndexOf(value, 'data:') === 0 && DATA_URI_TAGS[lcTag]) ; else if (ALLOW_UNKNOWN_PROTOCOLS && !regExpTest(IS_SCRIPT_OR_DATA, stringReplace(value, ATTR_WHITESPACE, ''))) ; else if (value) {
        return false;
      } else ;
      return true;
    };
    /**
     * _isBasicCustomElement
     * checks if at least one dash is included in tagName, and it's not the first char
     * for more sophisticated checking see https://github.com/sindresorhus/validate-element-name
     *
     * @param tagName name of the tag of the node to sanitize
     * @returns Returns true if the tag name meets the basic criteria for a custom element, otherwise false.
     */
    const _isBasicCustomElement = function _isBasicCustomElement(tagName) {
      return tagName !== 'annotation-xml' && stringMatch(tagName, CUSTOM_ELEMENT);
    };
    /**
     * _sanitizeAttributes
     *
     * @protect attributes
     * @protect nodeName
     * @protect removeAttribute
     * @protect setAttribute
     *
     * @param currentNode to sanitize
     */
    const _sanitizeAttributes = function _sanitizeAttributes(currentNode) {
      /* Execute a hook if present */
      _executeHooks(hooks.beforeSanitizeAttributes, currentNode, null);
      const {
        attributes
      } = currentNode;
      /* Check if we have attributes; if not we might have a text node */
      if (!attributes) {
        return;
      }
      const hookEvent = {
        attrName: '',
        attrValue: '',
        keepAttr: true,
        allowedAttributes: ALLOWED_ATTR,
        forceKeepAttr: undefined
      };
      let l = attributes.length;
      /* Go backwards over all attributes; safely remove bad ones */
      while (l--) {
        const attr = attributes[l];
        const {
          name,
          namespaceURI,
          value: attrValue
        } = attr;
        const lcName = transformCaseFunc(name);
        let value = name === 'value' ? attrValue : stringTrim(attrValue);
        /* Execute a hook if present */
        hookEvent.attrName = lcName;
        hookEvent.attrValue = value;
        hookEvent.keepAttr = true;
        hookEvent.forceKeepAttr = undefined; // Allows developers to see this is a property they can set
        _executeHooks(hooks.uponSanitizeAttribute, currentNode, hookEvent);
        value = hookEvent.attrValue;
        /* Full DOM Clobbering protection via namespace isolation,
         * Prefix id and name attributes with `user-content-`
         */
        if (SANITIZE_NAMED_PROPS && (lcName === 'id' || lcName === 'name')) {
          // Remove the attribute with this value
          _removeAttribute(name, currentNode);
          // Prefix the value and later re-create the attribute with the sanitized value
          value = SANITIZE_NAMED_PROPS_PREFIX + value;
        }
        /* Work around a security issue with comments inside attributes */
        if (SAFE_FOR_XML && regExpTest(/((--!?|])>)|<\/(style|title)/i, value)) {
          _removeAttribute(name, currentNode);
          continue;
        }
        /* Did the hooks approve of the attribute? */
        if (hookEvent.forceKeepAttr) {
          continue;
        }
        /* Remove attribute */
        _removeAttribute(name, currentNode);
        /* Did the hooks approve of the attribute? */
        if (!hookEvent.keepAttr) {
          continue;
        }
        /* Work around a security issue in jQuery 3.0 */
        if (!ALLOW_SELF_CLOSE_IN_ATTR && regExpTest(/\/>/i, value)) {
          _removeAttribute(name, currentNode);
          continue;
        }
        /* Sanitize attribute content to be template-safe */
        if (SAFE_FOR_TEMPLATES) {
          arrayForEach([MUSTACHE_EXPR, ERB_EXPR, TMPLIT_EXPR], expr => {
            value = stringReplace(value, expr, ' ');
          });
        }
        /* Is `value` valid for this attribute? */
        const lcTag = transformCaseFunc(currentNode.nodeName);
        if (!_isValidAttribute(lcTag, lcName, value)) {
          continue;
        }
        /* Handle attributes that require Trusted Types */
        if (trustedTypesPolicy && typeof trustedTypes === 'object' && typeof trustedTypes.getAttributeType === 'function') {
          if (namespaceURI) ; else {
            switch (trustedTypes.getAttributeType(lcTag, lcName)) {
              case 'TrustedHTML':
                {
                  value = trustedTypesPolicy.createHTML(value);
                  break;
                }
              case 'TrustedScriptURL':
                {
                  value = trustedTypesPolicy.createScriptURL(value);
                  break;
                }
            }
          }
        }
        /* Handle invalid data-* attribute set by try-catching it */
        try {
          if (namespaceURI) {
            currentNode.setAttributeNS(namespaceURI, name, value);
          } else {
            /* Fallback to setAttribute() for browser-unrecognized namespaces e.g. "x-schema". */
            currentNode.setAttribute(name, value);
          }
          if (_isClobbered(currentNode)) {
            _forceRemove(currentNode);
          } else {
            arrayPop(DOMPurify.removed);
          }
        } catch (_) {}
      }
      /* Execute a hook if present */
      _executeHooks(hooks.afterSanitizeAttributes, currentNode, null);
    };
    /**
     * _sanitizeShadowDOM
     *
     * @param fragment to iterate over recursively
     */
    const _sanitizeShadowDOM = function _sanitizeShadowDOM(fragment) {
      let shadowNode = null;
      const shadowIterator = _createNodeIterator(fragment);
      /* Execute a hook if present */
      _executeHooks(hooks.beforeSanitizeShadowDOM, fragment, null);
      while (shadowNode = shadowIterator.nextNode()) {
        /* Execute a hook if present */
        _executeHooks(hooks.uponSanitizeShadowNode, shadowNode, null);
        /* Sanitize tags and elements */
        if (_sanitizeElements(shadowNode)) {
          continue;
        }
        /* Deep shadow DOM detected */
        if (shadowNode.content instanceof DocumentFragment) {
          _sanitizeShadowDOM(shadowNode.content);
        }
        /* Check attributes, sanitize if necessary */
        _sanitizeAttributes(shadowNode);
      }
      /* Execute a hook if present */
      _executeHooks(hooks.afterSanitizeShadowDOM, fragment, null);
    };
    // eslint-disable-next-line complexity
    DOMPurify.sanitize = function (dirty) {
      let cfg = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
      let body = null;
      let importedNode = null;
      let currentNode = null;
      let returnNode = null;
      /* Make sure we have a string to sanitize.
        DO NOT return early, as this will return the wrong type if
        the user has requested a DOM object rather than a string */
      IS_EMPTY_INPUT = !dirty;
      if (IS_EMPTY_INPUT) {
        dirty = '<!-->';
      }
      /* Stringify, in case dirty is an object */
      if (typeof dirty !== 'string' && !_isNode(dirty)) {
        if (typeof dirty.toString === 'function') {
          dirty = dirty.toString();
          if (typeof dirty !== 'string') {
            throw typeErrorCreate('dirty is not a string, aborting');
          }
        } else {
          throw typeErrorCreate('toString is not a function');
        }
      }
      /* Return dirty HTML if DOMPurify cannot run */
      if (!DOMPurify.isSupported) {
        return dirty;
      }
      /* Assign config vars */
      if (!SET_CONFIG) {
        _parseConfig(cfg);
      }
      /* Clean up removed elements */
      DOMPurify.removed = [];
      /* Check if dirty is correctly typed for IN_PLACE */
      if (typeof dirty === 'string') {
        IN_PLACE = false;
      }
      if (IN_PLACE) {
        /* Do some early pre-sanitization to avoid unsafe root nodes */
        if (dirty.nodeName) {
          const tagName = transformCaseFunc(dirty.nodeName);
          if (!ALLOWED_TAGS[tagName] || FORBID_TAGS[tagName]) {
            throw typeErrorCreate('root node is forbidden and cannot be sanitized in-place');
          }
        }
      } else if (dirty instanceof Node) {
        /* If dirty is a DOM element, append to an empty document to avoid
           elements being stripped by the parser */
        body = _initDocument('<!---->');
        importedNode = body.ownerDocument.importNode(dirty, true);
        if (importedNode.nodeType === NODE_TYPE.element && importedNode.nodeName === 'BODY') {
          /* Node is already a body, use as is */
          body = importedNode;
        } else if (importedNode.nodeName === 'HTML') {
          body = importedNode;
        } else {
          // eslint-disable-next-line unicorn/prefer-dom-node-append
          body.appendChild(importedNode);
        }
      } else {
        /* Exit directly if we have nothing to do */
        if (!RETURN_DOM && !SAFE_FOR_TEMPLATES && !WHOLE_DOCUMENT &&
        // eslint-disable-next-line unicorn/prefer-includes
        dirty.indexOf('<') === -1) {
          return trustedTypesPolicy && RETURN_TRUSTED_TYPE ? trustedTypesPolicy.createHTML(dirty) : dirty;
        }
        /* Initialize the document to work on */
        body = _initDocument(dirty);
        /* Check we have a DOM node from the data */
        if (!body) {
          return RETURN_DOM ? null : RETURN_TRUSTED_TYPE ? emptyHTML : '';
        }
      }
      /* Remove first element node (ours) if FORCE_BODY is set */
      if (body && FORCE_BODY) {
        _forceRemove(body.firstChild);
      }
      /* Get node iterator */
      const nodeIterator = _createNodeIterator(IN_PLACE ? dirty : body);
      /* Now start iterating over the created document */
      while (currentNode = nodeIterator.nextNode()) {
        /* Sanitize tags and elements */
        if (_sanitizeElements(currentNode)) {
          continue;
        }
        /* Shadow DOM detected, sanitize it */
        if (currentNode.content instanceof DocumentFragment) {
          _sanitizeShadowDOM(currentNode.content);
        }
        /* Check attributes, sanitize if necessary */
        _sanitizeAttributes(currentNode);
      }
      /* If we sanitized `dirty` in-place, return it. */
      if (IN_PLACE) {
        return dirty;
      }
      /* Return sanitized string or DOM */
      if (RETURN_DOM) {
        if (RETURN_DOM_FRAGMENT) {
          returnNode = createDocumentFragment.call(body.ownerDocument);
          while (body.firstChild) {
            // eslint-disable-next-line unicorn/prefer-dom-node-append
            returnNode.appendChild(body.firstChild);
          }
        } else {
          returnNode = body;
        }
        if (ALLOWED_ATTR.shadowroot || ALLOWED_ATTR.shadowrootmode) {
          /*
            AdoptNode() is not used because internal state is not reset
            (e.g. the past names map of a HTMLFormElement), this is safe
            in theory but we would rather not risk another attack vector.
            The state that is cloned by importNode() is explicitly defined
            by the specs.
          */
          returnNode = importNode.call(originalDocument, returnNode, true);
        }
        return returnNode;
      }
      let serializedHTML = WHOLE_DOCUMENT ? body.outerHTML : body.innerHTML;
      /* Serialize doctype if allowed */
      if (WHOLE_DOCUMENT && ALLOWED_TAGS['!doctype'] && body.ownerDocument && body.ownerDocument.doctype && body.ownerDocument.doctype.name && regExpTest(DOCTYPE_NAME, body.ownerDocument.doctype.name)) {
        serializedHTML = '<!DOCTYPE ' + body.ownerDocument.doctype.name + '>\n' + serializedHTML;
      }
      /* Sanitize final string template-safe */
      if (SAFE_FOR_TEMPLATES) {
        arrayForEach([MUSTACHE_EXPR, ERB_EXPR, TMPLIT_EXPR], expr => {
          serializedHTML = stringReplace(serializedHTML, expr, ' ');
        });
      }
      return trustedTypesPolicy && RETURN_TRUSTED_TYPE ? trustedTypesPolicy.createHTML(serializedHTML) : serializedHTML;
    };
    DOMPurify.setConfig = function () {
      let cfg = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      _parseConfig(cfg);
      SET_CONFIG = true;
    };
    DOMPurify.clearConfig = function () {
      CONFIG = null;
      SET_CONFIG = false;
    };
    DOMPurify.isValidAttribute = function (tag, attr, value) {
      /* Initialize shared config vars if necessary. */
      if (!CONFIG) {
        _parseConfig({});
      }
      const lcTag = transformCaseFunc(tag);
      const lcName = transformCaseFunc(attr);
      return _isValidAttribute(lcTag, lcName, value);
    };
    DOMPurify.addHook = function (entryPoint, hookFunction) {
      if (typeof hookFunction !== 'function') {
        return;
      }
      arrayPush(hooks[entryPoint], hookFunction);
    };
    DOMPurify.removeHook = function (entryPoint) {
      return arrayPop(hooks[entryPoint]);
    };
    DOMPurify.removeHooks = function (entryPoint) {
      hooks[entryPoint] = [];
    };
    DOMPurify.removeAllHooks = function () {
      hooks = _createHooksMap();
    };
    return DOMPurify;
  }
  var purify = createDOMPurify();

  return purify;

}));


},{}]},{},[2]);
