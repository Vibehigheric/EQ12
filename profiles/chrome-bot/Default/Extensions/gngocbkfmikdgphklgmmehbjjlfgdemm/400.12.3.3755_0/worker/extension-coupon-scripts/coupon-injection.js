(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BestCouponResult = void 0;
const coupon_result_1 = require("./coupon-result");
class BestCouponResult extends coupon_result_1.CouponResult {
    constructor(cr) {
        super(cr.couponCode, cr.total, cr.savings, cr.extCode);
    }
}
exports.BestCouponResult = BestCouponResult;

},{"./coupon-result":3}],2:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponInjection = void 0;
const coupon_result_1 = require("./coupon-result");
const coupon_worker_api_1 = require("./coupon-worker-api");
const coupon_worker_async_1 = require("./coupon-worker-async");
const coupon_worker_1 = require("./coupon-worker");
const coupon_worker_factory_1 = require("./coupon-worker-factory");
const coupon_worker_state_1 = require("./coupon-worker-state");
const coupon_worker_types_1 = require("./coupon-worker-types");
const coupon_worker_json_1 = require("./coupon-worker-json");
class CouponInjection {
    static init(elementIds, customFuncs) {
        window['Prdg']['CouponInjection'].elementIds = elementIds;
        window['Prdg']['CouponInjection'].customFuncs = customFuncs;
    }
}
exports.CouponInjection = CouponInjection;
CouponInjection.elementIds = null;
CouponInjection.customFuncs = null;
CouponInjection.CouponResult = coupon_result_1.CouponResult;
CouponInjection.ApiCouponWorker = coupon_worker_api_1.ApiCouponWorker;
CouponInjection.AsyncCouponWorker = coupon_worker_async_1.AsyncCouponWorker;
CouponInjection.JsonCouponWorker = coupon_worker_json_1.JsonCouponWorker;
CouponInjection.CouponWorkerBase = coupon_worker_1.CouponWorker;
CouponInjection.CouponWorkerFactory = coupon_worker_factory_1.CouponWorkerFactory;
CouponInjection.CouponWorkerState = coupon_worker_state_1.CouponWorkerState;
CouponInjection.CouponWorkerTypes = coupon_worker_types_1.CouponWorkerTypes;
window['Prdg'] = window['Prdg'] || {};
window['Prdg']['CouponInjection'] = CouponInjection;

},{"./coupon-result":3,"./coupon-worker":10,"./coupon-worker-api":4,"./coupon-worker-async":5,"./coupon-worker-factory":6,"./coupon-worker-json":7,"./coupon-worker-state":8,"./coupon-worker-types":9}],3:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponResult = void 0;
class CouponResult {
    constructor(couponCode, total, savings, extCode) {
        this.total = total;
        this.extCode = extCode;
        this.message = savings > 0 ? 'success' : 'failure';
        this.couponCode = couponCode;
        this.savings = savings;
    }
}
exports.CouponResult = CouponResult;

},{}],4:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiCouponWorker = void 0;
const coupon_worker_1 = require("./coupon-worker");
const coupon_worker_state_1 = require("./coupon-worker-state");
const coupon_result_1 = require("./coupon-result");
class ApiCouponWorker extends coupon_worker_1.CouponWorker {
    constructor(extensionId, extCode, elementIds, customFuncs = null) {
        super(extensionId, extCode, elementIds, customFuncs);
        this.state = null;
    }
    applyPromoCode(code, dom) {
        return this.merchantWorker.applyPromoCode(code, this.state.originalTotal);
    }
    save(couponCode, currentTotal) {
        var dom;
        if (currentTotal.total) {
            dom = currentTotal.dom;
            currentTotal = currentTotal.total;
        }
        else {
            currentTotal = currentTotal;
        }
        var savings = this.state.originalTotal - currentTotal;
        var result = new coupon_result_1.CouponResult(couponCode, currentTotal, savings, this.extCode);
        this.broadcastCouponResult(result);
        this.state.results.push(result);
        if (dom)
            return dom;
    }
    // if there is a coupon already applied when the tester begins, we want to remove it and get a true bassline
    // for the original total
    async preRemove(dom) {
        try {
            var total;
            dom = await this.merchantWorker.removeCoupon(dom);
            if (this.merchantWorker.calculateTotal) {
                total = await this.merchantWorker.calculateTotal(dom);
            }
            else {
                total = await this.calculateTotal(dom);
            }
            total = await this.getTotalAsCorrectType(total);
            this.state.originalTotal = total;
            this.broadcastInitialTotal(this.extCode, total);
            return dom;
        }
        catch (x) {
            throw 'APICouponWorker.preProcess()';
        }
    }
    async tryPreRemove(dom) {
        if (this.state.preRemove) {
            try {
                await this.preRemove(dom);
                return dom;
            }
            catch (x) {
                throw x;
            }
        }
        else {
            return dom;
        }
    }
    async processFinalResult(dom) {
        var bestSavingsResult = this.getBestSavingsResult(this.state);
        var logCouponResults = new CustomEvent('logCouponResults', { detail: { couponResults: this.state.results, extCode: this.extCode } });
        document.dispatchEvent(logCouponResults);
        // success, let's apply the max coupon code
        var showFinalResult = null;
        var finalTotal = null;
        if (bestSavingsResult && bestSavingsResult.savings > 0) {
            dom = await this.merchantWorker.removeCoupon(dom);
            dom = await this.applyPromoCode(bestSavingsResult.couponCode, dom);
            if (this.merchantWorker.calculateTotal) {
                finalTotal = await this.merchantWorker.calculateTotal(dom);
            }
            else {
                finalTotal = await this.calculateTotal(dom);
            }
            finalTotal = await this.getTotalAsCorrectType(finalTotal);
            showFinalResult = this.sendFinalResult(bestSavingsResult, showFinalResult, finalTotal);
        }
        else {
            finalTotal = this.calculateTotal();
            showFinalResult = new CustomEvent("showFinalResult", { "detail": { "success": false, "total": finalTotal, extCode: this.extCode, 'shouldRefresh': true } });
            document.dispatchEvent(showFinalResult);
            await this.merchantWorker.removeCoupon();
        }
    }
    sendFinalResult(bestSavingsResult, showFinalResult, finalTotal) {
        var amount = bestSavingsResult.savings.toFixed(2);
        showFinalResult = new CustomEvent("showFinalResult", { "detail": { "couponCode": bestSavingsResult.couponCode, "amount": amount, "total": finalTotal, "success": true, extCode: this.extCode, 'shouldRefresh': true } });
        document.dispatchEvent(showFinalResult);
        return showFinalResult;
    }
    async process(couponCodes, dom) {
        if (!this.state) {
            this.state = new coupon_worker_state_1.CouponWorkerState();
        }
        if (this.state.currentIndex === couponCodes.length) {
            await this.processFinalResult(dom);
        }
        else {
            if (this.state.currentIndex > couponCodes.length - 1) {
                browserApi.runtime.sendMessage(this.extensionId, {
                    action: "LogError",
                    description: err,
                    merchant: "http://" + document.domain
                });
                var err = "Merchant: " + document.domain + ": error: No 'currentCoupon'.";
                console.error(err);
            }
            else {
                try {
                    var coupon = couponCodes[this.state.currentIndex];
                    dom = await this.tryPreRemove(dom);
                    dom = await this.merchantWorker.removeCoupon(dom);
                    var startProcessCoupon = new CustomEvent("startProcessCoupon", { "detail": { "coupon": coupon, extCode: this.extCode } });
                    document.dispatchEvent(startProcessCoupon);
                    dom = await this.applyPromoCode(coupon, dom);
                    var total;
                    if (this.merchantWorker.calculateTotal) {
                        total = await this.merchantWorker.calculateTotal(dom);
                    }
                    else {
                        total = await this.calculateTotal(dom);
                    }
                    total = await this.getTotalAsCorrectType(total);
                    this.save(coupon, total);
                }
                catch (x) {
                    var logMerchantPageError = null;
                    console.log("failing in api process, heres the error: ", x);
                    // We don't want our new C@C error paradigm to catch any/all errors, just the ones with an errorMessage type "hardFail"
                    if (x && x.type === "hardFail") {
                        logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": x.error, "type": "loudFail", extCode: this.extCode } });
                        document.dispatchEvent(logMerchantPageError);
                    }
                    // if something else caused an error, let's log it silently but keep going as it probably did not affect C@C experience"
                    else {
                        console.log(x);
                        logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": x.error, "type": "silentFail", extCode: this.extCode } });
                        document.dispatchEvent(logMerchantPageError);
                    }
                }
                finally {
                    if (this.state.preRemove) {
                        this.state.preRemove = false;
                    }
                    this.state.currentIndex++;
                    await this.process(couponCodes, dom);
                }
            }
        }
    }
    async getTotalAsCorrectType(total) {
        // Might not be a promise, but if it's just a number or object, it doesn't hurt to resolve().
        // might be many ways 12.50, "12.50", {total:12.50}, {total:"12.50"}, or any of those wrapped in a promise.
        let self = this;
        return new Promise((res) => {
            Promise.resolve(total)
                .then(function (value) {
                if (!isNaN(parseFloat(value))) {
                    res(parseFloat(value));
                }
                else if (value.total && !isNaN(parseFloat(value.total))) {
                    res(parseFloat(value.total));
                }
                else {
                    var errMsg = "getTotalAsCorrectType was unable to process correct type.";
                    var logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": errMsg, "type": "silentFail", extCode: self.extCode } });
                    document.dispatchEvent(logMerchantPageError);
                    res(-1);
                }
            });
        });
    }
}
exports.ApiCouponWorker = ApiCouponWorker;

},{"./coupon-result":3,"./coupon-worker":10,"./coupon-worker-state":8}],5:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AsyncCouponWorker = void 0;
const coupon_worker_1 = require("./coupon-worker");
const coupon_worker_state_1 = require("./coupon-worker-state");
const coupon_result_1 = require("./coupon-result");
class AsyncCouponWorker extends coupon_worker_1.CouponWorker {
    constructor(extensionId, extCode, elementIds, customFuncs = null) {
        super(extensionId, extCode, elementIds, customFuncs);
        this.state = null;
    }
    applyPromoCode(code) {
        return this.merchantWorker.applyPromoCode(code, this.state.originalTotal);
    }
    save(couponCode, currentTotal) {
        var savings = this.state.originalTotal - currentTotal;
        var result = new coupon_result_1.CouponResult(couponCode, currentTotal, savings, this.extCode);
        this.broadcastCouponResult(result);
        this.state.results.push(result);
    }
    // if there is a coupon already applied when the tester begins, we want to remove it and get a true bassline
    // for the original total
    async preRemove() {
        this.broadcastInitialTotal(this.extCode, await this.merchantWorker.calculateTotal());
        try {
            await this.merchantWorker.removeCoupon();
            if (this.merchantWorker.calculateTotal) {
                this.state.originalTotal = await this.merchantWorker.calculateTotal();
            }
            else {
                this.state.originalTotal = await this.calculateTotal();
            }
        }
        catch (x) {
            throw 'AsyncCouponWorker.preProcess()';
        }
    }
    async processFinalResult() {
        var bestSavingsResult = this.getBestSavingsResult(this.state);
        var logCouponResults = new CustomEvent('logCouponResults', { detail: { couponResults: this.state.results, extCode: this.extCode } });
        document.dispatchEvent(logCouponResults);
        // success, let's apply the max coupon code
        var showFinalResult = null;
        if (bestSavingsResult && bestSavingsResult.savings > 0) {
            try {
                await this.merchantWorker.removeCoupon();
            }
            finally {
                await this.applyPromoCode(bestSavingsResult.couponCode);
                var finalTotal;
                if (this.merchantWorker.calculateTotal) {
                    finalTotal = await this.merchantWorker.calculateTotal();
                }
                else {
                    finalTotal = await this.calculateTotal();
                }
                var amount = bestSavingsResult.savings.toFixed(2);
                showFinalResult = new CustomEvent("showFinalResult", { "detail": { "couponCode": bestSavingsResult.couponCode, "amount": amount, "total": finalTotal, "success": true, extCode: this.extCode } });
                document.dispatchEvent(showFinalResult);
            }
        }
        else {
            var finalTotal;
            if (this.merchantWorker.calculateTotal) {
                finalTotal = await this.merchantWorker.calculateTotal();
            }
            else {
                finalTotal = await this.calculateTotal();
            }
            showFinalResult = new CustomEvent("showFinalResult", { "detail": { "success": false, "total": finalTotal, extCode: this.extCode } });
            document.dispatchEvent(showFinalResult);
            await this.merchantWorker.removeCoupon();
        }
    }
    async process(couponCodes) {
        if (!this.state) {
            this.state = new coupon_worker_state_1.CouponWorkerState();
        }
        if (this.state.currentIndex === couponCodes.length) {
            await this.processFinalResult();
        }
        else {
            if (this.state.currentIndex > couponCodes.length - 1) {
                browserApi.runtime.sendMessage(this.extensionId, {
                    action: "LogError",
                    description: err,
                    merchant: "http://" + document.domain
                });
                var err = "Merchant: " + document.domain + ": error: No 'currentCoupon'.";
                console.error(err);
            }
            else {
                try {
                    var coupon = couponCodes[this.state.currentIndex];
                    if (this.state.preRemove) {
                        await this.preRemove();
                    }
                    await this.merchantWorker.removeCoupon();
                    var startProcessCoupon = new CustomEvent("startProcessCoupon", { "detail": { "coupon": coupon, extCode: this.extCode } });
                    document.dispatchEvent(startProcessCoupon);
                    await this.applyPromoCode(coupon);
                    var currentTotal;
                    if (this.merchantWorker.calculateTotal) {
                        currentTotal = await this.merchantWorker.calculateTotal();
                    }
                    else {
                        currentTotal = await this.calculateTotal();
                    }
                    this.save(coupon, currentTotal);
                }
                catch (x) {
                    var logMerchantPageError = null;
                    console.log("failing in async process, heres the error: ", x);
                    // We don't want our new C@C error paradigm to catch any/all errors, just the ones with an errorMessage type "hardFail"
                    if (x && x.type === "hardFail") {
                        logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": x.error, "type": "loudFail", extCode: this.extCode } });
                        document.dispatchEvent(logMerchantPageError);
                    }
                    // if something else caused an error, let's log it silently but keep going as it probably did not affect C@C experience"
                    else {
                        console.log(x);
                        logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": x.error, "type": "silentFail", extCode: this.extCode } });
                        document.dispatchEvent(logMerchantPageError);
                    }
                    this.broadcastError(this.extCode, x);
                }
                finally {
                    if (this.state.preRemove) {
                        this.state.preRemove = false;
                    }
                    this.state.currentIndex++;
                    await this.process(couponCodes);
                }
            }
        }
    }
}
exports.AsyncCouponWorker = AsyncCouponWorker;

},{"./coupon-result":3,"./coupon-worker":10,"./coupon-worker-state":8}],6:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponWorkerFactory = void 0;
const coupon_worker_types_1 = require("./coupon-worker-types");
const coupon_worker_async_1 = require("./coupon-worker-async");
const coupon_worker_api_1 = require("./coupon-worker-api");
class CouponWorkerFactory {
    static construct(merchantWorker, extensionId, extCode, elementIds, customFuncs) {
        var couponWorker = null;
        switch (merchantWorker.testerType) {
            case coupon_worker_types_1.CouponWorkerTypes.async:
                couponWorker = new coupon_worker_async_1.AsyncCouponWorker(extensionId, extCode, elementIds, customFuncs);
                break;
            case coupon_worker_types_1.CouponWorkerTypes.api:
                couponWorker = new coupon_worker_api_1.ApiCouponWorker(extensionId, extCode, elementIds, customFuncs);
                break;
        }
        couponWorker.init(merchantWorker);
        return couponWorker;
    }
}
exports.CouponWorkerFactory = CouponWorkerFactory;

},{"./coupon-worker-api":4,"./coupon-worker-async":5,"./coupon-worker-types":9}],7:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JsonCouponWorker = void 0;
const coupon_worker_1 = require("./coupon-worker");
const merchant_1 = require("./merchant");
const coupon_worker_state_1 = require("./coupon-worker-state");
const coupon_result_1 = require("./coupon-result");
const constants_1 = require("./processors/instructions/constants");
const final_coupon_result_1 = require("./final-coupon-result");
class JsonCouponWorker extends coupon_worker_1.CouponWorker {
    constructor(merchantDefinition, extensionId, extCode) {
        super(extensionId, extCode, null);
        this.isTotalChanged = false;
        this.extCode = extCode;
        this.merchant = new merchant_1.Merchant(merchantDefinition);
        this.extensionId = extensionId;
    }
    async checkInitialElementsJson() {
        let iecResult = await this.merchant.checkInitialElements();
        // TODO: Once sliders are updated, we can send back the full object if we want, or at least a cleaner object, 
        // and possibly a clearer result for doNotApply (sending back passed=false for now, so that we go to 'View Coupons')
        if (iecResult.passed === false && !iecResult.doNotApply) {
            let errMessage = "";
            errMessage = iecResult.preCheckFailed ? ` Precheck failed ` : errMessage;
            errMessage = iecResult.missingElements ? errMessage += `Missing Elements: ${iecResult.missingElements} ` : errMessage;
            errMessage = iecResult.message ? errMessage += ` ${iecResult.message} ` : errMessage;
            this.broadcastError(this.extCode, errMessage);
        }
        var e = new CustomEvent('initialElementsChecked', { "detail": { "extCode": this.extCode, "passed": iecResult.passed } });
        document.dispatchEvent(e);
    }
    async applyPromoCode(code) {
        if (this.merchant.definition.rateLimit) {
            await new Promise(resolve => setTimeout(resolve, this.merchant.definition.rateLimit));
        }
        await this.applyOrRemovePromoCode(code);
    }
    async removePromoCode() {
        if (!this.merchant.definition.stackable) {
            await this.applyOrRemovePromoCode();
        }
    }
    // if there is a parameter/code, then apply(), else remove()
    async applyOrRemovePromoCode(code) {
        let isApply = code ? true : false;
        let self = this;
        self.isTotalChanged = false;
        let observer;
        let isApi = this.isApi(isApply);
        if (!isApi) {
            // setup MutationObserver   
            observer = new MutationObserver(function (mutationRecords, me) {
                self.isTotalChanged = true;
                me.disconnect();
            });
            observer.observe(document.querySelector(self.merchant.selectors.cartTotal), {
                childList: true,
                subtree: true,
                characterDataOldValue: true
            });
        }
        try {
            // Either of these calls include a waitFor with appropriate 'isFinished()'
            if (isApply) {
                await this.merchant.applyCoupon(code /*, this.state.originalTotal*/);
            }
            else {
                await this.merchant.removeCoupon();
            }
        }
        catch (e) {
            // First waitFor never caught apply or remove finished, but it's been 4 seconds, let's move on.
        }
        if (observer) {
            // Apply or Remove has happened, but it often takes a few seconds for the cartTotal to update. 
            // Wait for MO (isTotalChanged) or 4 seconds.. whichever is first.
            if (!self.isTotalChanged) {
                // function to pass to second waitFor
                var fnIsTotalChanged = function () {
                    return self.isTotalChanged;
                };
                try {
                    let additionalPollCount = 8;
                    if (this.merchant.definition.additionalPollCount || this.merchant.definition.additionalPollCount === 0) {
                        additionalPollCount = this.merchant.definition.additionalPollCount;
                    }
                    await this.merchant.waitFor(fnIsTotalChanged, additionalPollCount);
                }
                catch (e) {
                    // Second waitFor never caught isTotalChanged, but it's been 4 seconds, let's move on.
                }
            }
            observer.disconnect();
        }
        return;
    }
    // Need to know if Api so we know weather to use Mutation Observer.
    isApi(isApply) {
        let isApi = false;
        let applyOrRemoveJson;
        if (isApply) {
            applyOrRemoveJson = this.merchant.definition.applyCoupon;
        }
        else {
            applyOrRemoveJson = this.merchant.definition.removeCoupon;
        }
        // Look at array of keys first two levels...
        // Only 2 levels as assuming Async does not break anything, but we wait will a few extra seconds. 
        // if an http call is 3 levels deep it might be a mix of Async and Api and we actually would want to use MO and wait.
        for (var key in applyOrRemoveJson) {
            if (constants_1.Constants.HTTP_TERMS.includes(key)) {
                isApi = true;
            }
            else {
                for (var innerKey in applyOrRemoveJson[key]) {
                    if (constants_1.Constants.HTTP_TERMS.includes(innerKey)) {
                        isApi = true;
                    }
                }
            }
        }
        return isApi;
    }
    async processFinalResult() {
        // bestSavingsResult is a copy of the bestSavings item for non-stackable, but edited for stackable.
        var bestSavingsResult;
        if (this.merchant.definition.stackable) {
            bestSavingsResult = this.getBestSavingsResultStackable(this.state);
        }
        else {
            bestSavingsResult = this.getBestSavingsResult(this.state);
        }
        var logCouponResults = new CustomEvent('logCouponResults', { detail: { couponResults: this.state.results, extCode: this.extCode } });
        document.dispatchEvent(logCouponResults);
        // success, let's apply the max coupon code
        var showFinalResult = null;
        if (bestSavingsResult && bestSavingsResult.savings > 0) {
            try {
                await this.removePromoCode();
            }
            finally {
                if (!this.merchant.definition.stackable) {
                    await this.applyPromoCode(bestSavingsResult.couponCode);
                }
                const finalTotal = await this.merchant.calculateTotal();
                const amount = bestSavingsResult.savings.toFixed(2);
                //  FinalCouponResult can not implment CouponResult because it may or may not have a coupon code, and the coupon code is required in the constructor for CouponResult
                let finalResultDetail = new final_coupon_result_1.FinalCouponResult(true, finalTotal, this.extCode);
                finalResultDetail.amount = amount;
                if (bestSavingsResult.couponCodes) {
                    finalResultDetail.couponCodes = bestSavingsResult.couponCodes;
                }
                else {
                    finalResultDetail.couponCode = bestSavingsResult.couponCode;
                }
                if (this.merchant.definition.shouldRefresh) {
                    finalResultDetail.shouldRefresh = true;
                }
                showFinalResult = new CustomEvent("showFinalResult", { "detail": finalResultDetail });
                document.dispatchEvent(showFinalResult);
            }
        }
        else {
            var finalTotal = await this.merchant.calculateTotal();
            let finalResultDetail = new final_coupon_result_1.FinalCouponResult(false, finalTotal, this.extCode);
            showFinalResult = new CustomEvent("showFinalResult", { "detail": finalResultDetail });
            document.dispatchEvent(showFinalResult);
            await this.removePromoCode();
        }
    }
    // if there is a coupon already applied when the tester begins, we want to remove it and get a true bassline
    // for the original total
    async preRemove() {
        const initialTotal = await this.merchant.calculateTotal();
        this.merchant.log('Initial total:', initialTotal);
        this.broadcastInitialTotal(this.extCode, initialTotal);
        try {
            await this.removePromoCode();
            this.state.originalTotal = await this.merchant.calculateTotal();
            this.state.previousTotal = this.state.originalTotal;
        }
        catch (x) {
            throw 'JSONCouponWorker.preProcess()';
        }
    }
    save(couponCode, currentTotal) {
        var savings;
        if (this.merchant.definition.stackable) {
            savings = this.state.previousTotal - currentTotal;
            this.state.previousTotal = currentTotal;
        }
        else {
            savings = this.state.originalTotal - currentTotal;
        }
        var result = new coupon_result_1.CouponResult(couponCode, currentTotal, savings, this.extCode);
        this.broadcastCouponResult(result);
        this.state.results.push(result);
    }
    async preCheckInitialElements() {
        await this.merchant.preCheckInitialElements();
    }
    async process(couponCodes, dom) {
        if (!this.state) {
            this.state = new coupon_worker_state_1.CouponWorkerState();
        }
        if (this.state.currentIndex === couponCodes.length) {
            await this.processFinalResult();
        }
        else {
            if (this.state.currentIndex > couponCodes.length - 1) {
                browserApi.runtime.sendMessage(this.extensionId, {
                    action: "LogError",
                    description: err,
                    merchant: "http://" + document.domain
                });
                var err = "Merchant: " + document.domain + ": error: No 'currentCoupon'.";
                console.error(err);
            }
            else {
                try {
                    var coupon = couponCodes[this.state.currentIndex];
                    if (this.state.preRemove) {
                        await this.preRemove();
                    }
                    else {
                        await this.removePromoCode();
                    }
                    var startProcessCoupon = new CustomEvent("startProcessCoupon", { "detail": { "coupon": coupon, extCode: this.extCode } });
                    document.dispatchEvent(startProcessCoupon);
                    await this.applyPromoCode(coupon);
                    var currentTotal = await this.merchant.calculateTotal();
                    this.save(coupon, currentTotal);
                }
                catch (x) {
                    var logMerchantPageError = null;
                    console.log("failing in json process, heres the error: ", x);
                    // We don't want our new C@C error paradigm to catch any/all errors, just the ones with an errorMessage type "hardFail"
                    if (x && x.type === "hardFail") {
                        logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": x.error, "type": "loudFail", extCode: this.extCode } });
                        document.dispatchEvent(logMerchantPageError);
                    }
                    // if something else caused an error, let's log it silently but keep going as it probably did not affect C@C experience"
                    else {
                        console.log(x);
                        logMerchantPageError = new CustomEvent("logMerchantPageError", { "detail": { "errorMessage": x ? x.error : '', "type": "silentFail", extCode: this.extCode } });
                        document.dispatchEvent(logMerchantPageError);
                    }
                    this.broadcastError(this.extCode, x);
                }
                finally {
                    if (this.state.preRemove) {
                        this.state.preRemove = false;
                    }
                    this.state.currentIndex++;
                    await this.process(couponCodes, null);
                }
            }
        }
    }
}
exports.JsonCouponWorker = JsonCouponWorker;

},{"./coupon-result":3,"./coupon-worker":10,"./coupon-worker-state":8,"./final-coupon-result":11,"./merchant":17,"./processors/instructions/constants":33}],8:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponWorkerState = void 0;
class CouponWorkerState {
    constructor() {
        this.results = [];
        this.preRemove = true;
        this.initialized = false;
        this.currentIndex = 0;
        this.couponNumber = 0;
        this.reloadCounter = 0;
        this.testedCoupons = [];
        this.originalTotal = null;
        this.previousTotal = null;
    }
}
exports.CouponWorkerState = CouponWorkerState;

},{}],9:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponWorkerTypes = void 0;
var CouponWorkerTypes;
(function (CouponWorkerTypes) {
    CouponWorkerTypes[CouponWorkerTypes["async"] = 1] = "async";
    CouponWorkerTypes[CouponWorkerTypes["postback"] = 2] = "postback";
    CouponWorkerTypes[CouponWorkerTypes["api"] = 3] = "api";
    CouponWorkerTypes[CouponWorkerTypes["json"] = 4] = "json";
})(CouponWorkerTypes = exports.CouponWorkerTypes || (exports.CouponWorkerTypes = {}));

},{}],10:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponWorker = void 0;
const best_coupon_result_1 = require("./best-coupon-result");
class CouponWorker {
    constructor(extensionId, extCode, elementIds, customFuncs = null) {
        this.customFuncs = null;
        this.extCode = null;
        this.elementIds = null;
        this.extensionId = null;
        this.merchantWorker = null;
        this.extCode = extCode;
        this.elementIds = elementIds;
        this.extensionId = extensionId;
        this.customFuncs = customFuncs;
    }
    broadcastCouponResult(result) {
        var saveCouponResult = new CustomEvent('saveCouponResult', { "detail": result });
        document.dispatchEvent(saveCouponResult);
    }
    getBestSavingsResult(workerState) {
        var result = null;
        workerState.results.forEach(r => {
            if (!result || r.savings > result.savings) {
                result = new best_coupon_result_1.BestCouponResult(r);
            }
        });
        return result;
    }
    getBestSavingsResultStackable(workerState) {
        var bestResult = null;
        let savingsCount = workerState.results.filter(r => r.savings).length;
        if (savingsCount > 1) {
            bestResult = new best_coupon_result_1.BestCouponResult(workerState.results[0]);
            let totalSavings = 0;
            bestResult.couponCodes = [];
            workerState.results.forEach(r => {
                if (r && r.savings) {
                    totalSavings += r.savings;
                    bestResult.couponCodes.push(r.couponCode);
                }
            });
            bestResult.savings = totalSavings;
        }
        else {
            bestResult = this.getBestSavingsResult(workerState);
        }
        return bestResult;
    }
    init(merchantWorker) {
        this.merchantWorker = merchantWorker;
        this.checkInitialState(this.extCode);
    }
    hideMerchantOverlay() {
        if (typeof this.merchantWorker['hideMerchantOverlay'] === 'function') {
            this.merchantWorker['hideMerchantOverlay']();
        }
    }
    revertMerchantOverlay() {
        if (this.merchantWorker && typeof this.merchantWorker['revertMerchantOverlay'] === 'function') {
            this.merchantWorker['revertMerchantOverlay']();
        }
    }
    showProgress(percent) {
        var updateProgressBar = new CustomEvent('updateProgressBar', { "detail": { percent: percent, extCode: this.extCode } });
        document.dispatchEvent(updateProgressBar);
    }
    calculateTotal(el) {
        var totalDiv = el || $(this.elementIds.bagTotalId);
        var total = -1;
        var totalText = null;
        if (totalDiv.length > 0) {
            totalText = $.trim(totalDiv.text()).replace(/,/g, '');
            totalText = $.trim(totalText).match(/\d+[\.\d{0,3}]/g);
            if (totalText.length == 1)
                totalText = totalText[0];
            else
                totalText = totalText[0] + totalText[1];
            total = parseFloat(totalText);
        }
        return total;
    }
    calculateTotalAsync(el = null, dom) {
        return new Promise((res) => {
            var total = this.calculateTotal(el);
            res(total);
        });
    }
    checkCouponError(fnCouponHasError) {
        return new Promise((res) => {
            setTimeout(() => {
                res(fnCouponHasError());
            }, 2000);
        });
    }
    // Merchants often have multiple variations of elements of the same selector. These should be used selectively.
    getFirst(selector, fnCondition) {
        var elements = $(selector);
        var first = null;
        for (var i = 0; i < elements.length; i++) {
            var el = elements.eq(i);
            if (fnCondition(el)) {
                first = el;
                break;
            }
        }
        return first;
    }
    getFirstVisible(selector) {
        return this.getFirst(selector, function (el) {
            return el.is(':visible');
        });
    }
    // Cross-browser supported event triggering method. element = plain JS element, not JQuery-wrapped.
    triggerEvent(element, eventName) {
        var evt = document.createEvent('HTMLEvents');
        evt.initEvent(eventName, true, false);
        element.dispatchEvent(evt);
    }
    // React-specific logic. Call this if simple calling val('') on an input does not register for a merchant using React.
    // element = plain JS element, not JQuery-wrapped.
    setReactCouponCode(element, code) {
        var setter = Object.getOwnPropertyDescriptor(window['HTMLInputElement'].prototype, 'value').set;
        setter.call(element, code);
    }
    addGlobalCSS(css, elementId) {
        var head = document.head || document.getElementsByTagName('head')[0];
        var style = document.createElement('style');
        style.type = 'text/css';
        style.dataset.extid = elementId;
        if (style.styleSheet) {
            style.styleSheet.cssText = css;
        }
        else {
            style.appendChild(document.createTextNode(css));
        }
        head.appendChild(style);
    }
    removeGlobalCSS(elementId) {
        document.querySelectorAll('style[data-extid=' + elementId + ']').forEach(function (el) { el.remove(); });
    }
    broadcastInitialTotal(extCode, total) {
        var e = new CustomEvent('initialTotal', { "detail": { "extCode": extCode, "total": total } });
        document.dispatchEvent(e);
    }
    waitFor(fn) {
        return new Promise((res, rej) => {
            var loopCount = 0;
            var pollMaxCount = 12;
            var pollInterval = 500;
            (function poll() {
                if (fn(loopCount)) {
                    res();
                }
                else {
                    if (loopCount === pollMaxCount) {
                        // We can end up in here, 2 different ways. 
                        // # 1 when something is never found. (For example site changes, and Initial Element Check is failing)
                        // # 2 waitfor certain coupons get applied (or removed) and have abnormal behavior.
                        //     (For example, rare Gap coupon that doesn't result in an error message or a valid code/remove button)
                        rej(`*CI function didn't complete, but pollMaxCount is hit :` + fn.name);
                    }
                    else {
                        loopCount++;
                        setTimeout(poll, pollInterval);
                    }
                }
            })();
        });
    }
    waitForRemoveCoupon(fnIsRemoveFinished) {
        return new Promise(async (res, rej) => {
            try {
                await this.waitFor(fnIsRemoveFinished);
                res();
            }
            catch (x) {
                rej({
                    type: "waitFor remove",
                    action: "removeCoupon()",
                    error: "couponRemoveId not found"
                });
            }
        });
    }
    waitForApplyPromoCode(code, fnIsApplyFinished) {
        return new Promise(async (res, rej) => {
            try {
                await this.waitFor(fnIsApplyFinished);
                res();
            }
            catch (x) {
                rej({
                    action: "applyPromoCode(code)",
                    message: "Coupon code " + code,
                    type: "waitFor apply",
                    error: "error in waitForApplyPromoCode"
                });
            }
        });
    }
    broadcastError(extCode, message) {
        var e = new CustomEvent('couponInjectionError', { "detail": { "extCode": extCode, "message": message } });
        document.dispatchEvent(e);
    }
    async checkInitialElements(extCode) {
        var self = this;
        if (this.customFuncs && typeof this.customFuncs.checkInitialElements === 'function') {
            try {
                await this.waitFor(this.customFuncs.checkInitialElements);
                var e = new CustomEvent('initialElementsChecked', { "detail": { "extCode": extCode, "passed": true } });
                document.dispatchEvent(e);
            }
            catch (x) {
                var logMessage = "checkInitialElements Failed : customFuncs===true;";
                if (x) {
                    console.log(logMessage, x.toString());
                }
                else {
                    console.log(logMessage);
                }
                var e = new CustomEvent('initialElementsChecked', { "detail": { "extCode": extCode, "passed": false } });
                document.dispatchEvent(e);
                var missingValue = '';
                if (typeof this.customFuncs.getMissingElements === 'function') {
                    missingValue = this.customFuncs.getMissingElements();
                }
                this.broadcastError(extCode, 'Initial elements check failed. Missing: ' + missing);
            }
        }
        else {
            var elInput, elButton, elRemove, elDoNotApplyCoupons;
            var check = function () {
                elInput = $(self.elementIds.couponApplyId).length > 0;
                elButton = $(self.elementIds.couponApplyButtonId).length > 0 || $(self.elementIds.couponApplyButtonSelector).length > 0;
                elRemove = $(self.elementIds.couponRemoveId).length > 0;
                elDoNotApplyCoupons = $(self.elementIds.doNotApplyCouponsId).length > 0;
                return elRemove || elDoNotApplyCoupons || (elInput && elButton);
            };
            try {
                await this.waitFor(check);
                var e = new CustomEvent('initialElementsChecked', { "detail": { "extCode": extCode, "passed": !elDoNotApplyCoupons } });
                document.dispatchEvent(e);
            }
            catch (x) {
                var logMessage = "checkInitialElements Failed : customFuncs===false;";
                if (x) {
                    console.log(logMessage, x.toString());
                }
                else {
                    console.log(logMessage);
                }
                var e = new CustomEvent('initialElementsChecked', { "detail": { "extCode": extCode, "passed": false } });
                document.dispatchEvent(e);
                if (!elDoNotApplyCoupons) {
                    var missing = [];
                    var elements = { couponInput: elInput, applyCoupon: elButton, removeCoupon: elRemove };
                    for (var k in elements) {
                        if (!elements[k]) {
                            missing.push(k);
                        }
                    }
                    this.broadcastError(extCode, 'Initial elements check failed. Missing: ' + missing.toString());
                }
            }
        }
    }
    checkInitialCoupon(extCode) {
        // TODO
    }
    checkInitialState(extCode) {
        setTimeout(async () => {
            await this.checkInitialElements(extCode);
            this.checkInitialCoupon(extCode);
        }, 1000);
    }
}
exports.CouponWorker = CouponWorker;

},{"./best-coupon-result":1}],11:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinalCouponResult = void 0;
class FinalCouponResult {
    constructor(success, total, extCode) {
        this.success = success;
        this.total = total;
        this.extCode = extCode;
    }
}
exports.FinalCouponResult = FinalCouponResult;

},{}],12:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });

},{}],13:[function(require,module,exports){
arguments[4][12][0].apply(exports,arguments)
},{"dup":12}],14:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InitialElementsCheckResult = void 0;
class InitialElementsCheckResult {
}
exports.InitialElementsCheckResult = InitialElementsCheckResult;

},{}],15:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MerchantDefinition = void 0;
class MerchantDefinition {
}
exports.MerchantDefinition = MerchantDefinition;

},{}],16:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MerchantSelectors = void 0;
class MerchantSelectors {
}
exports.MerchantSelectors = MerchantSelectors;

},{}],17:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Merchant = void 0;
const winnower_1 = require("./processors/instructions/winnower");
class Merchant {
    constructor(definition) {
        this._log = () => { };
        this.selectors = definition.selectors;
        this.definition = definition;
        this._vars = definition.vars || {};
    }
    get dom() { return this._dom || document; }
    log(message, arg) {
        if (this._log) {
            this._log(message, arg);
        }
    }
    setLog(log) {
        this._log = log;
    }
    parseVars(vars) {
        Object.keys(vars).forEach(k => {
            this._vars[k] = this.parseSelector(vars[k]);
        });
    }
    async processInstruction(instruction, data) {
        let key = Object.keys(instruction)[0];
        if (key === 'vars') {
            this.parseVars(instruction[key]);
            delete instruction[key];
            await winnower_1.InstructionWinnower.processInstruction(this, instruction, data);
        }
        else {
            await winnower_1.InstructionWinnower.processInstruction(this, instruction, data);
        }
    }
    async processQueryInstruction(instruction) {
        await this.processInstruction(instruction);
        let result = this.queryResult;
        this.queryResult = null;
        return result;
    }
    parseSelector(value) {
        let isVar = value.startsWith('var(');
        let isSelector = value.startsWith('selector(');
        if (isVar || isSelector) {
            let arg = value.substring(value.indexOf('(') + 1, value.indexOf(')'));
            let result;
            if (isVar) {
                result = this._vars[arg];
            }
            else {
                result = (this.definition.selectors && this.definition.selectors[arg]) || arg;
            }
            if (!result) {
                this.log(`issue with parseSelector() no result for value:${value}`);
            }
            else {
                return result;
            }
        }
        else
            return value;
    }
    async defaultRemoveCoupon() {
        await this.processInstruction({
            'if:visible:selector(couponRemove)': {
                'click:selector(couponRemove)': {
                    'wait-for:!visible:selector(couponRemove)': true
                }
            }
        });
    }
    async removeCoupon() {
        if (this.definition.removeCoupon) {
            await this.processInstruction(this.definition.removeCoupon);
        }
        else {
            await this.defaultRemoveCoupon();
        }
    }
    // 7.0 regex to remove everything but numeric digits and decimal. Version 6.0 and less only stripped $
    // 8.0 adding check for "." or ",", otherwise add a decimal
    parseTotalText(value) {
        try {
            var priceText = value.trim().replace(/[^0-9\.]/g, "");
            if (!priceText) {
                this.log(`nothing in price text. inputString:${value}`);
            }
            if (priceText.indexOf(".") === -1 && priceText.indexOf(",") === -1) {
                let centLocation = priceText.length - 2;
                priceText = priceText.substring(0, centLocation) + "." + priceText.substring(centLocation);
            }
            return parseFloat(priceText);
        }
        catch (e) {
            this.log(`err in parseFloat. inputString:${value}`);
            return -1;
        }
    }
    defaultCalculateTotal() {
        var el = this.dom.querySelector(this.definition.selectors.cartTotal);
        var total = -1;
        if (el) {
            return this.parseTotalText(el.innerText);
        }
        return total;
    }
    async calculateTotal() {
        if (this.definition.calculateTotal) {
            let result = await this.processQueryInstruction(this.definition.calculateTotal);
            if (typeof result !== 'number') {
                return this.parseTotalText(result.toString());
            }
            else {
                return result;
            }
        }
        else {
            return this.defaultCalculateTotal();
        }
    }
    async defaultApplyCoupon(code) {
        await this.processInstruction({
            'apply:selector(couponInput)': {
                'click:selector(couponApply)': {
                    'wait-for:couponApplied': true
                }
            }
        }, code);
    }
    async applyCoupon(code) {
        this._dom = null;
        if (this.definition.applyCoupon) {
            await this.processInstruction(this.definition.applyCoupon, code);
        }
        else {
            await this.defaultApplyCoupon(code);
        }
    }
    waitFor(fn, pollMaxCount = 8) {
        return new Promise(async (res, rej) => {
            let loopCount = 0;
            let pollInterval = 500;
            let poll = async () => {
                try {
                    if (await fn(loopCount)) {
                        res();
                    }
                    else {
                        if (loopCount === pollMaxCount) {
                            rej();
                        }
                        else {
                            loopCount++;
                            setTimeout(async () => { await poll(); }, pollInterval);
                        }
                    }
                }
                catch (x) {
                    rej();
                }
            };
            await poll();
        });
    }
    async preCheckInitialElements() {
        await this.processInstruction(this.definition.preCheckInitialElements);
    }
    async checkInitialElements() {
        let iecResult = {
            passed: false
        };
        if (this.definition.preCheckInitialElements) {
            try {
                await this.preCheckInitialElements();
            }
            catch (x) {
                iecResult.passed = false;
                iecResult.preCheckFailed = true;
                if (x) {
                    iecResult.message = x.toString();
                }
                return iecResult;
            }
        }
        if (typeof this.definition.shouldCheckInitialElements === 'undefined' || this.definition.shouldCheckInitialElements === true) {
            try {
                var elInput, elButton, elRemove, elCartTotal, elDoNotApplyCoupons;
                await this.waitFor(() => {
                    // we need to reset the DOM everytime we waitFor in order to be able to check against the current document object.
                    this.setDom(document);
                    elInput = this.dom.querySelectorAll(this.selectors.couponInput).length > 0;
                    elButton = this.dom.querySelectorAll(this.selectors.couponApply).length > 0;
                    elRemove = this.dom.querySelectorAll(this.selectors.couponRemove).length > 0;
                    elCartTotal = this.dom.querySelectorAll(this.selectors.cartTotal).length > 0;
                    elDoNotApplyCoupons = this.dom.querySelectorAll(this.selectors.doNotApply).length > 0;
                    if (elDoNotApplyCoupons) {
                        iecResult.passed = false;
                        iecResult.doNotApply = true;
                        return iecResult;
                    }
                    else if (elCartTotal && (elRemove || (elInput && elButton))) {
                        iecResult.passed = true;
                        return iecResult;
                    }
                });
            }
            catch (x) {
                // waitFor rejected based on error or nothing found.
                let missing = [];
                var elements = { couponInput: elInput, applyCoupon: elButton, removeCoupon: elRemove, cartTotal: elCartTotal };
                for (var k in elements) {
                    if (!elements[k]) {
                        missing.push(k);
                    }
                }
                iecResult.passed = false;
                iecResult.missingElements = missing.toString();
                if (x) {
                    iecResult.message = x.toString();
                }
            }
        }
        else {
            // shouldCheckInitialElements is false, counts as a pass
            iecResult.passed = true;
        }
        // actual return for this method is here if elements found inside waitFor.
        return iecResult;
    }
    setQueryResult(result) {
        this.queryResult = result;
    }
    setDom(dom) {
        this._dom = dom;
    }
    setVar(name, value) {
        this._vars[name] = value;
    }
    getVar(name) {
        return this._vars[name];
    }
}
exports.Merchant = Merchant;

},{"./processors/instructions/winnower":54}],18:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProcessorBase = void 0;
const string_variable_arg_details_1 = require("./models/string-variable-arg-details");
class ProcessorBase {
    constructor(merchant) {
        this.merchant = merchant;
    }
    getTime() {
        return (new Date()).getTime().toString();
    }
    replace(value, begin, replacement, end) {
        let before = value.substring(0, begin);
        let after = value.substring(end);
        return before + replacement + after;
    }
    replaceCall(value) {
        let details = new string_variable_arg_details_1.StringVariableArgDetails(value, '[call:');
        let callValue = this[details.arg]();
        return this.replace(value, details.begin, callValue, details.end);
    }
    replaceCode(value, code) {
        if (code) {
            let start = value.indexOf('[code]');
            return value.substring(0, start) + code + value.substring(start + 6);
        }
        else {
            console.error('Coupon code missing from replaceCode call.');
            return "";
        }
    }
    replaceSession(value) {
        let details = new string_variable_arg_details_1.StringVariableArgDetails(value, '[session:');
        let item = sessionStorage.getItem(details.arg);
        return this.replace(value, details.begin, item, details.end);
    }
    replaceVariable(value) {
        let details = new string_variable_arg_details_1.StringVariableArgDetails(value, '[var:');
        let variable = this.merchant.getVar(details.arg);
        return this.replace(value, details.begin, variable, details.end);
    }
    replaceData(target, data) {
        if (target) {
            return this.parseJson(target, data);
        }
        else {
            return data;
        }
    }
    parseString(value, data) {
        if (value === null && data && typeof (data) === "string") {
            return data;
        }
        else if (typeof value === 'string') {
            let replacees = ['[call:', '[code]', '[session:', '[var:', '[data]'];
            while (replacees.some(r => value.includes(r))) {
                let replacee = replacees.find(r => value.includes(r));
                switch (replacee) {
                    case '[call:':
                        value = this.replaceCall(value);
                        break;
                    case '[code]':
                        value = this.replaceCode(value, data);
                        break;
                    case '[session:':
                        value = this.replaceSession(value);
                        break;
                    case '[var:':
                        value = this.replaceVariable(value);
                        break;
                    case '[data]':
                        value = this.replaceData(value, data);
                        break;
                }
            }
        }
        return value;
    }
    parseJson(target, data) {
        let path = this.checkForJsonPath(target);
        let result = "";
        // in case json comes in as a string, we need to to try to parse
        try {
            data = JSON.parse(data);
        }
        catch (e) {
            // we just want to tryParse, if not, we don't want to do anything, as it may already be a JSON object
            // unless it's just a plain string, then return
            if (typeof (data) === "string") {
                return data;
            }
        }
        // TODO handle arrays
        let pathKeys = [];
        if (path.includes('.')) {
            pathKeys = path.split('.');
        }
        else {
            pathKeys.push(path);
        }
        if (pathKeys.length > 0) {
            for (let i = 0; i < pathKeys.length; i++) {
                if (pathKeys[i].includes('[')) {
                    // if an array is hardcoded into data string like "...:[data].promotions[0].coupon.UUID"
                    let pathKeySplit = pathKeys[i].split('[');
                    let objPathKey = pathKeySplit[0];
                    let objPathIndexLength = pathKeySplit[1].indexOf(']'); // in case index > 1 digit
                    let objPathIndex = parseInt(pathKeySplit[1].substring(0, objPathIndexLength));
                    data = data[objPathKey][objPathIndex];
                }
                else {
                    // normal flow
                    data = data[pathKeys[i]];
                }
            }
        }
        else {
            return null;
        }
        result = data;
        return result.toString();
    }
    checkForJsonPath(instruction) {
        let dataPath = "";
        if (instruction.includes('[data]')) {
            let configSections = instruction.split('[data].');
            dataPath = configSections[1];
        }
        else if (instruction.includes('.')) {
            dataPath = instruction;
        }
        else {
            dataPath = 'data';
        }
        return dataPath;
    }
}
exports.ProcessorBase = ProcessorBase;

},{"./models/string-variable-arg-details":56}],19:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApplyCompleteConditionProcessor = void 0;
const base_1 = require("../base");
const coupon_applied_1 = require("./coupon-applied");
const coupon_has_error_1 = require("./coupon-has-error");
class ApplyCompleteConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process() {
        let applied = new coupon_applied_1.CouponAppliedConditionProcessor(this.merchant);
        let hasError = new coupon_has_error_1.CouponHasErrorConditionProcessor(this.merchant);
        return applied.process() || hasError.process();
    }
}
exports.ApplyCompleteConditionProcessor = ApplyCompleteConditionProcessor;

},{"../base":18,"./coupon-applied":20,"./coupon-has-error":21}],20:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponAppliedConditionProcessor = void 0;
const base_1 = require("../base");
const conditional_1 = require("../instructions/conditional");
class CouponAppliedConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process() {
        let condition = this.merchant.definition.couponApplied || 'visible:selector(error)||visible:selector(couponRemove)';
        let processor = new conditional_1.ConditionalInstructionProcessor(this.merchant, condition, null);
        return await processor.processCondition(condition);
    }
}
exports.CouponAppliedConditionProcessor = CouponAppliedConditionProcessor;

},{"../base":18,"../instructions/conditional":32}],21:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CouponHasErrorConditionProcessor = void 0;
const base_1 = require("../base");
const factory_1 = require("./factory");
class CouponHasErrorConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process() {
        let condition = this.merchant.definition.couponHasError || 'visible:selector(error)';
        let processor = factory_1.ConditionProcessorFactory.construct(this.merchant, condition);
        return processor.process();
    }
}
exports.CouponHasErrorConditionProcessor = CouponHasErrorConditionProcessor;

},{"../base":18,"./factory":23}],22:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExistsConditionProcessor = void 0;
const base_1 = require("../base");
class ExistsConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        if (target.startsWith('selector('))
            target = this.merchant.parseSelector(target);
        return !!this.merchant.dom.querySelector(target);
    }
}
exports.ExistsConditionProcessor = ExistsConditionProcessor;

},{"../base":18}],23:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConditionProcessorFactory = void 0;
const visibility_1 = require("./visibility");
const coupon_applied_1 = require("./coupon-applied");
const coupon_has_error_1 = require("./coupon-has-error");
const apply_complete_1 = require("./apply-complete");
const session_1 = require("./session");
const exists_1 = require("./exists");
const has_json_path_1 = require("./has-json-path");
class ConditionProcessorFactory {
    static construct(merchant, conditionState) {
        let processor = null;
        switch (conditionState) {
            case 'visible':
                processor = new visibility_1.VisibilityConditionProcessor(merchant);
                break;
            case 'couponApplied':
                processor = new coupon_applied_1.CouponAppliedConditionProcessor(merchant);
                break;
            case 'couponHasError':
                processor = new coupon_has_error_1.CouponHasErrorConditionProcessor(merchant);
                break;
            case 'applyComplete':
                processor = new apply_complete_1.ApplyCompleteConditionProcessor(merchant);
                break;
            case 'session':
                processor = new session_1.SessionConditionProcessor(merchant);
                break;
            case 'exists':
                processor = new exists_1.ExistsConditionProcessor(merchant);
                break;
            case 'hasJsonPath':
                processor = new has_json_path_1.HasJsonPathConditionProcessor(merchant);
                break;
        }
        return processor;
    }
}
exports.ConditionProcessorFactory = ConditionProcessorFactory;

},{"./apply-complete":19,"./coupon-applied":20,"./coupon-has-error":21,"./exists":22,"./has-json-path":24,"./session":26,"./visibility":27}],24:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HasJsonPathConditionProcessor = void 0;
const base_1 = require("../base");
class HasJsonPathConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, data) {
        try {
            var hasJson = !!this.parseJson(target, data);
            return hasJson;
        }
        catch (e) {
            // if the json path doesn't exist at all, it can fail.
            return false;
        }
    }
}
exports.HasJsonPathConditionProcessor = HasJsonPathConditionProcessor;

},{"../base":18}],25:[function(require,module,exports){
arguments[4][12][0].apply(exports,arguments)
},{"dup":12}],26:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionConditionProcessor = void 0;
const base_1 = require("../base");
class SessionConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        return !!sessionStorage.getItem(target);
    }
}
exports.SessionConditionProcessor = SessionConditionProcessor;

},{"../base":18}],27:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.VisibilityConditionProcessor = void 0;
const base_1 = require("../base");
class VisibilityConditionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    getFirst(selector, fnCondition) {
        let first = null;
        let elements = document.querySelectorAll(selector);
        for (let i = 0; i < elements.length; i++) {
            let el = elements[i];
            if (fnCondition(el)) {
                first = el;
                break;
            }
        }
        return first;
    }
    async process(target) {
        let selector = this.merchant.parseSelector(target);
        return !!this.getFirst(selector, (el) => {
            return !!(el.style.display !== 'none' && (el.offsetWidth || el.offsetHeight || el.getClientRects().length));
        });
    }
}
exports.VisibilityConditionProcessor = VisibilityConditionProcessor;

},{"../base":18}],28:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApplyInstructionProcessor = void 0;
const base_1 = require("../base");
class ApplyInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, code) {
        let arg = null;
        let selector = null;
        if (target.includes(':')) {
            let segments = target.split(':');
            selector = this.merchant.parseSelector(segments[0]);
            arg = segments[1];
        }
        else {
            selector = this.merchant.parseSelector(target);
        }
        let el = this.merchant.dom.querySelector(selector);
        if (arg === 'react') {
            this.reactParameter(el, code);
        }
        else {
            el.value = code;
        }
        return false;
    }
    // The merchant is using React and we need to trigger the React 'input' event for this to work.
    // Apparently react overrides the native 'value' setter.
    reactParameter(el, code) {
        var setter = Object.getOwnPropertyDescriptor(window['HTMLInputElement'].prototype, 'value').set;
        setter.call(el, code);
        var evt = this.merchant.dom.createEvent('HTMLEvents');
        evt.initEvent('input', true, false);
        el.dispatchEvent(evt);
    }
}
exports.ApplyInstructionProcessor = ApplyInstructionProcessor;

},{"../base":18}],29:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CallInstructionProcessor = void 0;
const base_1 = require("../base");
const winnower_1 = require("./winnower");
class CallInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        const instruction = this.merchant.definition[target];
        if (instruction) {
            await winnower_1.InstructionWinnower.processInstruction(this.merchant, instruction);
        }
        return false;
    }
}
exports.CallInstructionProcessor = CallInstructionProcessor;

},{"../base":18,"./winnower":54}],30:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ClickAllInstructionProcessor = void 0;
const base_1 = require("../base");
class ClickAllInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        let selector = this.merchant.parseSelector(target);
        let els = Array.from(this.merchant.dom.querySelectorAll(selector));
        els.forEach(el => {
            el.click();
        });
        return false;
    }
}
exports.ClickAllInstructionProcessor = ClickAllInstructionProcessor;

},{"../base":18}],31:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ClickInstructionProcessor = void 0;
const base_1 = require("../base");
class ClickInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        let selector = this.merchant.parseSelector(target);
        let el = this.merchant.dom.querySelector(selector);
        el.click();
        return false;
    }
}
exports.ClickInstructionProcessor = ClickInstructionProcessor;

},{"../base":18}],32:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConditionalInstructionProcessor = void 0;
const factory_1 = require("../conditions/factory");
const winnower_1 = require("./winnower");
const base_1 = require("../base");
class ConditionalInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant, condition, childInstruction, data) {
        super(merchant);
        this.data = data;
        this.condition = condition;
        this.childInstruction = childInstruction;
    }
    async processCondition(condition) {
        let isOr = condition.includes('||');
        let isAnd = condition.includes('&&');
        if (isOr || isAnd) {
            let conditions = condition.split(isOr ? '||' : '&&');
            if (isOr) {
                return (await this.processCondition(conditions[0])) || (await this.processCondition(conditions[1]));
            }
            else {
                return (await this.processCondition(conditions[0])) && (await this.processCondition(conditions[1]));
            }
        }
        else {
            let segments = condition.split(':');
            if (segments.length > 2) {
                throw `Condition invalid: ${condition}`;
            }
            else {
                let isNot = false;
                let state = segments.length === 2 ? segments[0] : condition;
                if (state.startsWith('!')) {
                    isNot = true;
                    state = state.substring(1);
                }
                let target = segments.length === 2 ? segments[1] : null;
                let processor = factory_1.ConditionProcessorFactory.construct(this.merchant, state);
                if (!processor) {
                    throw `Condition state invalid: ${state}`;
                }
                else {
                    let result = await processor.process(target, this.data);
                    return isNot ? !result : result;
                }
            }
        }
    }
    async process() {
        let resolved = false;
        resolved = await this.processCondition(this.condition);
        if (resolved) {
            await winnower_1.InstructionWinnower.processInstruction(this.merchant, this.childInstruction, this.data);
        }
        return true;
    }
}
exports.ConditionalInstructionProcessor = ConditionalInstructionProcessor;

},{"../base":18,"../conditions/factory":23,"./winnower":54}],33:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Constants = void 0;
class Constants {
}
exports.Constants = Constants;
Constants.CONDITIONAL_TERMS = ['if', 'else-if'];
Constants.HTTP_TERMS = ['http-get', 'http-post', 'http-delete', 'http-put', 'http-submit-form'];
Constants.REGULAR_TERMS = [
    'click',
    'click-all',
    'wait-for',
    'apply',
    'trigger-event',
    'set-session',
    'remove-session',
    'set-query-result',
    'set-dom',
    'query',
    'call',
    'set-values',
    'set-var',
    'set-var-with-math',
    'enable-button'
];

},{}],34:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EnableButtonInstructionProcessor = void 0;
const base_1 = require("../base");
class EnableButtonInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        let selector = this.merchant.parseSelector(target);
        let element = this.merchant.dom.querySelector(selector);
        element?.removeAttribute('disabled');
        return false;
    }
}
exports.EnableButtonInstructionProcessor = EnableButtonInstructionProcessor;

},{"../base":18}],35:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InstructionProcessorFactory = void 0;
const click_1 = require("./click");
const wait_for_1 = require("./wait-for");
const apply_1 = require("./apply");
const trigger_event_1 = require("./trigger-event");
const http_get_1 = require("./http/http-get");
const set_session_1 = require("./setter/set-session");
const http_post_1 = require("./http/http-post");
const http_delete_1 = require("./http/http-delete");
const http_put_1 = require("./http/http-put");
const set_query_result_1 = require("./setter/set-query-result");
const click_all_1 = require("./click-all");
const set_dom_1 = require("./setter/set-dom");
const remove_session_1 = require("./setter/remove-session");
const query_1 = require("./query");
const call_1 = require("./call");
const http_submit_form_1 = require("./http/http-submit-form");
const set_values_1 = require("./set-values");
const set_var_1 = require("./setter/set-var");
const set_var_with_math_1 = require("./setter/set-var-with-math");
const enable_button_1 = require("./enable-button");
class InstructionProcessorFactory {
    static construct(merchant, action) {
        let processor = null;
        switch (action) {
            case 'click':
                processor = new click_1.ClickInstructionProcessor(merchant);
                break;
            case 'click-all':
                processor = new click_all_1.ClickAllInstructionProcessor(merchant);
                break;
            case 'wait-for':
                processor = new wait_for_1.WaitForInstructionProcessor(merchant);
                break;
            case 'wait-for-double':
                processor = new wait_for_1.WaitForInstructionProcessor(merchant, 16);
                break;
            case 'apply':
                processor = new apply_1.ApplyInstructionProcessor(merchant);
                break;
            case 'trigger-event':
                processor = new trigger_event_1.TriggerEventInstructionProcessor(merchant);
                break;
            case 'http-get':
                processor = new http_get_1.HttpGetInstructionProcessor(merchant);
                break;
            case 'http-post':
                processor = new http_post_1.HttpPostInstructionProcessor(merchant);
                break;
            case 'http-delete':
                processor = new http_delete_1.HttpDeleteInstructionProcessor(merchant);
                break;
            case 'http-put':
                processor = new http_put_1.HttpPutInstructionProcessor(merchant);
                break;
            case 'set-session':
                processor = new set_session_1.SetSessionInstructionProcessor(merchant);
                break;
            case 'remove-session':
                processor = new remove_session_1.RemoveSessionInstructionProcessor(merchant);
                break;
            case 'set-query-result':
                processor = new set_query_result_1.SetQueryResultInstructionProcessor(merchant);
                break;
            case 'set-dom':
                processor = new set_dom_1.SetDomInstructionProcessor(merchant);
                break;
            case 'query':
                processor = new query_1.QueryInstructionProcessor(merchant);
                break;
            case 'call':
                processor = new call_1.CallInstructionProcessor(merchant);
                break;
            case 'http-submit-form':
                processor = new http_submit_form_1.HttpSubmitFormInstructionProcessor(merchant);
                break;
            case 'set-values':
                processor = new set_values_1.SetValuesInstructionProcessor(merchant);
                break;
            case 'set-var':
                processor = new set_var_1.SetVarInstructionProcessor(merchant);
                break;
            case 'set-var-with-math':
                processor = new set_var_with_math_1.SetVarWithMathInstructionProcessor(merchant);
                break;
            case 'enable-button':
                processor = new enable_button_1.EnableButtonInstructionProcessor(merchant);
                break;
        }
        return processor;
    }
}
exports.InstructionProcessorFactory = InstructionProcessorFactory;

},{"./apply":28,"./call":29,"./click":31,"./click-all":30,"./enable-button":34,"./http/http-delete":37,"./http/http-get":38,"./http/http-post":39,"./http/http-put":40,"./http/http-submit-form":41,"./query":44,"./set-values":45,"./setter/remove-session":46,"./setter/set-dom":47,"./setter/set-query-result":48,"./setter/set-session":49,"./setter/set-var":51,"./setter/set-var-with-math":50,"./trigger-event":52,"./wait-for":53}],36:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpInstructionProcessorBase = void 0;
const base_1 = require("../../base");
const winnower_1 = require("../winnower");
class HttpInstructionProcessorBase extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    constructRequest() {
        return new XMLHttpRequest();
    }
    processRequest(config, method, data) {
        return new Promise((res, rej) => {
            let url = this.parseString(config.url, data);
            let request = this.constructRequest();
            request.onreadystatechange = async () => {
                if (request.readyState === 4) {
                    if (request.status === 200) {
                        let response = null;
                        if (request.responseText) {
                            response = request.responseText;
                            try {
                                response = JSON.parse(response);
                            }
                            catch (x) {
                                this.merchant.log(`HTTP Error caught in onreadystatechange : `, x);
                            }
                        }
                        this.merchant.log('HTTP response: ', response);
                        res(response);
                    }
                    else {
                        this.merchant.log(`HTTP onreadystatechange not 200 status : ${request.status}  `);
                        rej();
                    }
                }
            };
            request.open(method, url, true);
            let headers = config.headers;
            if (headers) {
                Object.keys(headers).forEach(k => {
                    request.setRequestHeader(k, this.parseString(headers[k]));
                });
            }
            let body = null;
            if (config.data) {
                try {
                    body = typeof config.data === 'string' ? config.data : JSON.stringify(config.data);
                }
                catch (x) { }
                body = this.parseString(body, data);
            }
            request.send(body);
        });
    }
    async send(config, method, data) {
        let response;
        let childProcessed = false;
        try {
            response = await this.processRequest(config, method, data);
        }
        catch (x) { }
        if (response && config.success) {
            let childInstruction = config.success;
            await winnower_1.InstructionWinnower.processInstruction(this.merchant, childInstruction, response);
            childProcessed = true;
        }
        return childProcessed;
    }
    async processInstruction(config, method, data) {
        if (!config) {
            throw `Invalid HTTP config: ${JSON.stringify(config)}`;
        }
        else {
            if (typeof config.url === 'undefined')
                config.url = '';
            return await this.send(config, method, data);
        }
    }
}
exports.HttpInstructionProcessorBase = HttpInstructionProcessorBase;

},{"../../base":18,"../winnower":54}],37:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpDeleteInstructionProcessor = void 0;
const http_base_1 = require("./http-base");
class HttpDeleteInstructionProcessor extends http_base_1.HttpInstructionProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, config, data) {
        return await this.processInstruction(config, 'DELETE', data);
    }
}
exports.HttpDeleteInstructionProcessor = HttpDeleteInstructionProcessor;

},{"./http-base":36}],38:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpGetInstructionProcessor = void 0;
const http_base_1 = require("./http-base");
class HttpGetInstructionProcessor extends http_base_1.HttpInstructionProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, config, data) {
        return await this.processInstruction(config, 'GET', data);
    }
}
exports.HttpGetInstructionProcessor = HttpGetInstructionProcessor;

},{"./http-base":36}],39:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpPostInstructionProcessor = void 0;
const http_base_1 = require("./http-base");
class HttpPostInstructionProcessor extends http_base_1.HttpInstructionProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, config, data) {
        return await this.processInstruction(config, 'POST', data);
    }
}
exports.HttpPostInstructionProcessor = HttpPostInstructionProcessor;

},{"./http-base":36}],40:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpPutInstructionProcessor = void 0;
const http_base_1 = require("./http-base");
class HttpPutInstructionProcessor extends http_base_1.HttpInstructionProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, config, data) {
        return await this.processInstruction(config, 'PUT', data);
    }
}
exports.HttpPutInstructionProcessor = HttpPutInstructionProcessor;

},{"./http-base":36}],41:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpSubmitFormInstructionProcessor = void 0;
const http_base_1 = require("./http-base");
class HttpSubmitFormInstructionProcessor extends http_base_1.HttpInstructionProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, config, data) {
        let childProcessed;
        if (config && config.input) {
            const input = this.processInput(config, data);
            if (input) {
                const form = this.getForm(input);
                this.merchant.log('http-submit-form:', form);
                if (form)
                    childProcessed = await this.submit(form, config, data);
                else
                    console.error('Input parent form was not found:', config.input);
            }
            else
                console.error('Input element was not found:', config.input);
        }
        else
            console.error('Invalid SubmitFormConfig:', config);
        return childProcessed;
    }
    processInput(config, data) {
        const selector = config.input.startsWith('selector(') ? this.merchant.parseSelector(config.input) : config.input;
        const input = this.merchant.dom.querySelector(selector);
        if (input && input.nodeName === 'INPUT') {
            if (typeof config.value !== 'undefined')
                input['value'] = this.parseString(config.value, data);
        }
        return input;
    }
    getForm(el) {
        const parent = el.parentElement;
        if (parent) {
            if (parent.nodeName === 'FORM')
                return parent;
            else
                return this.getForm(parent);
        }
        else
            return null;
    }
    async submit(form, config, data) {
        const httpConfig = this.generateConfig(form, config);
        return await this.processInstruction(httpConfig, form.method, data);
    }
    generateConfig(form, config) {
        var data = this.serializeForm(form, config);
        this.merchant.log('FORM DATA:', data);
        return {
            url: form.action,
            data,
            headers: {
                'content-type': 'application/x-www-form-urlencoded'
            },
            success: config.success
        };
    }
    serializeForm(form, config) {
        let data = Array.from(form.querySelectorAll('input, select'))
            .filter(input => !!input.name)
            .map(input => `${encodeURIComponent(input.name)}=${encodeURIComponent(input.value)}`)
            .join('&');
        if (config.append && config.append.length) {
            config.append.forEach(s => {
                const el = document.querySelector(this.merchant.parseSelector(s));
                if (el && el['name']) {
                    data += `&${el['name']}=${el['value']}`;
                }
            });
        }
        return data;
    }
}
exports.HttpSubmitFormInstructionProcessor = HttpSubmitFormInstructionProcessor;

},{"./http-base":36}],42:[function(require,module,exports){
arguments[4][12][0].apply(exports,arguments)
},{"dup":12}],43:[function(require,module,exports){
arguments[4][12][0].apply(exports,arguments)
},{"dup":12}],44:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QueryInstructionProcessor = void 0;
const base_1 = require("../base");
class QueryInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    parse(segment) {
        if (segment.startsWith('attr(')) {
            const attr = segment.substring(segment.indexOf('(') + 1, segment.indexOf(')'));
            if (!this.current) {
                this.merchant.log(`Query parse: Was not able to get attr: ${attr} as selector did not find element.`);
            }
            return this.current.getAttribute(attr);
        }
        else if (segment === 'text') {
            return this.current.innerText;
        }
        else {
            let selector = segment;
            if (segment.startsWith('selector(')) {
                selector = this.merchant.parseSelector(segment);
            }
            return this.merchant.dom.querySelector(selector);
        }
    }
    async process(target) {
        const args = target.split(':');
        const name = args[0];
        const segments = args.slice(1);
        for (let i = 0; i < segments.length; i++) {
            this.current = this.parse(segments[i]);
        }
        this.merchant.setVar(name, this.current);
        return false;
    }
}
exports.QueryInstructionProcessor = QueryInstructionProcessor;

},{"../base":18}],45:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SetValuesInstructionProcessor = void 0;
const base_1 = require("../base");
class SetValuesInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, map, data) {
        Object.keys(map).forEach(k => {
            // Set all the elements with the same selector
            Array.from(document.querySelectorAll(this.parseString(k))).forEach(el => {
                el['value'] = this.parseString(map[k]);
            });
        });
        return false;
    }
}
exports.SetValuesInstructionProcessor = SetValuesInstructionProcessor;

},{"../base":18}],46:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RemoveSessionInstructionProcessor = void 0;
const base_1 = require("../../base");
class RemoveSessionInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, data) {
        sessionStorage.removeItem(target);
        return false;
    }
}
exports.RemoveSessionInstructionProcessor = RemoveSessionInstructionProcessor;

},{"../../base":18}],47:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SetDomInstructionProcessor = void 0;
const base_1 = require("../../base");
class SetDomInstructionProcessor extends base_1.ProcessorBase {
    constructParser() {
        return new DOMParser();
    }
    constructor(merchant) {
        super(merchant);
    }
    async process(target, data) {
        let html = this.parseString(target, data);
        let parser = this.constructParser();
        let dom = parser.parseFromString(html, 'text/html');
        this.merchant.setDom(dom);
        return false;
    }
}
exports.SetDomInstructionProcessor = SetDomInstructionProcessor;

},{"../../base":18}],48:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SetQueryResultInstructionProcessor = void 0;
const base_1 = require("../../base");
class SetQueryResultInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, data) {
        this.merchant.setQueryResult(this.parseString(target, data));
        return false;
    }
}
exports.SetQueryResultInstructionProcessor = SetQueryResultInstructionProcessor;

},{"../../base":18}],49:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SetSessionInstructionProcessor = void 0;
const base_1 = require("../../base");
class SetSessionInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, data) {
        // we want the first part of the target to be the key, as the second section may also have a colon (if it is looking for a var)
        let indexOfFirstColon = target.indexOf(':');
        const key = target.substring(0, indexOfFirstColon);
        const valueSection = target.substring(indexOfFirstColon + 1);
        sessionStorage.setItem(key, this.parseString(valueSection, data));
        return false;
    }
}
exports.SetSessionInstructionProcessor = SetSessionInstructionProcessor;

},{"../../base":18}],50:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SetVarWithMathInstructionProcessor = void 0;
const base_1 = require("../../base");
/*
  Some merchants have unusual numeric values on their pages. This can make calculate total complex.
  Walgreens and GlassesUSA are examples
*/
class SetVarWithMathInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    /*
    target should have 3 parts
      - the name of the variable we are 'getting' then manipulating then 'setting'
      - the mathematical operator we want to process
      - a numeric term that we want to use with the operator against the variable
    */
    async process(target) {
        const segments = target.split(':');
        let varName = segments[0];
        let operator = segments[1];
        let mathTerm = segments[2];
        let computedVar = this.merchant.getVar(varName);
        computedVar = computedVar.trim().replace(/[^0-9\.]/g, "");
        if (parseInt(computedVar) !== NaN) {
            switch (operator) {
                case "+":
                    computedVar = parseInt(computedVar) + parseInt(mathTerm);
                    break;
                case "-":
                    computedVar = parseInt(computedVar) - parseInt(mathTerm);
                    break;
                case "*":
                    computedVar = parseInt(computedVar) * parseInt(mathTerm);
                    break;
                case "/":
                    computedVar = parseInt(computedVar) / parseInt(mathTerm);
                    break;
                case "%":
                    computedVar = parseInt(computedVar) % parseInt(mathTerm);
                    break;
                default:
                    computedVar = parseInt(computedVar);
                    break;
            }
        }
        this.merchant.setVar(varName, computedVar);
        return false;
    }
}
exports.SetVarWithMathInstructionProcessor = SetVarWithMathInstructionProcessor;

},{"../../base":18}],51:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SetVarInstructionProcessor = void 0;
const base_1 = require("../../base");
class SetVarInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target, data) {
        const segments = target.split(':');
        this.merchant.setVar(segments[0], this.parseString(segments[1], data));
        return false;
    }
}
exports.SetVarInstructionProcessor = SetVarInstructionProcessor;

},{"../../base":18}],52:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TriggerEventInstructionProcessor = void 0;
const base_1 = require("../base");
class TriggerEventInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant) {
        super(merchant);
    }
    async process(target) {
        let segments = target.split(':');
        let selector = this.merchant.parseSelector(segments[0]);
        let element = this.merchant.dom.querySelector(selector);
        let event = this.merchant.dom.createEvent('HTMLEvents');
        event.initEvent(segments[1], true, false);
        element.dispatchEvent(event);
        return false;
    }
}
exports.TriggerEventInstructionProcessor = TriggerEventInstructionProcessor;

},{"../base":18}],53:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WaitForInstructionProcessor = void 0;
const base_1 = require("../base");
const conditional_1 = require("./conditional");
class WaitForInstructionProcessor extends base_1.ProcessorBase {
    constructor(merchant, waitForLoops = 8) {
        super(merchant);
        this.waitForLoops = waitForLoops;
    }
    async process(condition) {
        let processor = new conditional_1.ConditionalInstructionProcessor(this.merchant, null, null);
        await this.merchant.waitFor(async () => { return await processor.processCondition(condition); }, this.waitForLoops);
        return false;
    }
}
exports.WaitForInstructionProcessor = WaitForInstructionProcessor;

},{"../base":18,"./conditional":32}],54:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InstructionWinnower = void 0;
const conditional_1 = require("./conditional");
const factory_1 = require("./factory");
const http_base_1 = require("./http/http-base");
const constants_1 = require("./constants");
const set_values_1 = require("./set-values");
class InstructionWinnower {
    static async processInstruction(merchant, instruction, data) {
        if (typeof instruction !== 'boolean') {
            let keys = Object.keys(instruction);
            for (let i = 0; i < keys.length; i++) {
                let key = keys[i];
                let child = instruction[key];
                let startsWithTerm = constants_1.Constants.CONDITIONAL_TERMS.concat(constants_1.Constants.REGULAR_TERMS)
                    .concat(constants_1.Constants.HTTP_TERMS)
                    .some(t => key.startsWith(t));
                if (startsWithTerm) {
                    let isTwoPart = key.includes(':');
                    let term = isTwoPart ? key.substring(0, key.indexOf(':')) : key;
                    let value = isTwoPart ? key.substring(key.indexOf(':') + 1) : null;
                    if (constants_1.Constants.CONDITIONAL_TERMS.includes(term)) {
                        merchant.log('WINNOW CONDITION:', value);
                        let processor = new conditional_1.ConditionalInstructionProcessor(merchant, value, child, data);
                        await processor.process();
                    }
                    else {
                        merchant.log('INSTRUCTION:', `${term} ${value} (${JSON.stringify(data)})`);
                        let childInstructionProcessed;
                        let processor = factory_1.InstructionProcessorFactory.construct(merchant, term);
                        if (processor instanceof http_base_1.HttpInstructionProcessorBase || processor instanceof set_values_1.SetValuesInstructionProcessor) {
                            childInstructionProcessed = await processor.process(value, child, data);
                        }
                        else {
                            childInstructionProcessed = await processor.process(value, data);
                        }
                        if (!childInstructionProcessed) {
                            await this.processInstruction(merchant, child, data);
                        }
                    }
                }
            }
        }
    }
}
exports.InstructionWinnower = InstructionWinnower;

},{"./conditional":32,"./constants":33,"./factory":35,"./http/http-base":36,"./set-values":45}],55:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpConfig = void 0;
class HttpConfig {
}
exports.HttpConfig = HttpConfig;

},{}],56:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StringVariableArgDetails = void 0;
class StringVariableArgDetails {
    constructor(value, matcher) {
        this.begin = value.indexOf(matcher);
        let remainder = value.substring(value.indexOf(matcher) + matcher.length);
        this.end = this.begin + matcher.length + remainder.indexOf(']') + 1;
        this.arg = remainder.substring(0, remainder.indexOf(']'));
    }
}
exports.StringVariableArgDetails = StringVariableArgDetails;

},{}],57:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SubmitFormConfig = void 0;
class SubmitFormConfig {
}
exports.SubmitFormConfig = SubmitFormConfig;

},{}]},{},[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57]);
