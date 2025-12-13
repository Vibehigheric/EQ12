(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeepScrapeConfig = void 0;
class DeepScrapeConfig {
    constructor(dsConfig) {
        this.enabled = dsConfig.enabled &&
            (!dsConfig.partialRollout || (dsConfig.partialRollout && (Math.random() * 100 <= dsConfig.partialRollout)));
        this.waitForIntervals = dsConfig.waitForIntervals ? dsConfig.waitForIntervals : 8;
        this.pageSize = dsConfig.pageSize ? dsConfig.pageSize : 1;
        this.maxPageNumbers = dsConfig.maxPageNumbers ? dsConfig.maxPageNumbers : 1;
        this.useCursor = dsConfig.useCursor ? dsConfig.useCursor : false;
        this.cursorSelector = dsConfig.cursorSelector ? dsConfig.cursorSelector : undefined;
        this.httpConfigs = dsConfig.httpConfig;
        this.returnType = dsConfig.returnType;
        this.childHttpConfig = dsConfig.childHttpConfig ? dsConfig.childHttpConfig : undefined;
        this.parentKey = dsConfig.parentKey ? dsConfig.parentKey : undefined;
        this.childPathKey = dsConfig.childPathKey ? dsConfig.childPathKey : undefined;
        this.sendPartialResultCount = dsConfig.sendPartialResultCount ? dsConfig.sendPartialResultCount : undefined;
    }
}
exports.DeepScrapeConfig = DeepScrapeConfig;

},{}],2:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpConfig = void 0;
class HttpConfig {
    constructor(hc) {
        this.url = hc.url;
        this.method = hc.method;
        this.data = hc.data ? hc.data : undefined;
        this.headers = hc.headers ? hc.headers : undefined;
        this.success = hc.success ? hc.success : undefined;
        this.body = hc.body ? hc.body : undefined;
        this.rateLimit = hc.rateLimit ? hc.rateLimit : undefined;
    }
}
exports.HttpConfig = HttpConfig;

},{}],3:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MerchantConfig = void 0;
const order_config_set_1 = require("./order-config-set");
const log_1 = require(".././log");
const product_config_set_1 = require("./product-config-set");
const deep_scrape_config_1 = require("./deep-scrape-config");
class MerchantConfig {
    constructor(modelJson) {
        this.orderConfigSet = [];
        this.productConfigSet = [];
        if (modelJson.orders) {
            try {
                modelJson.orders.forEach(orderSet => {
                    // defined at top level, but need to push into orders, as we can mix/match orders w/ deep scraping
                    if (modelJson.pageSubType) {
                        orderSet.pageSubType = modelJson.pageSubType;
                    }
                    this.orderConfigSet.push(new order_config_set_1.OrderConfigSet(orderSet));
                });
                modelJson.products.forEach(productSet => {
                    this.productConfigSet.push(new product_config_set_1.ProductConfigSet(productSet));
                });
            }
            catch (e) {
                log_1.Log.consoleLog('Error constructing merchant config', e);
            }
        }
        if (modelJson.deepScrape) {
            this.deepScrapeConfig = new deep_scrape_config_1.DeepScrapeConfig(modelJson.deepScrape);
        }
        if (modelJson.emptyCartSelector) {
            this.emptyCartSelector = modelJson.emptyCartSelector;
        }
    }
}
exports.MerchantConfig = MerchantConfig;

},{".././log":15,"./deep-scrape-config":1,"./order-config-set":4,"./product-config-set":7}],4:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderConfigSet = void 0;
const order_level_config_item_1 = require("./order-level-config-item");
const script_json_config_1 = require("./script-json-config");
class OrderConfigSet {
    constructor(modelJson) {
        this.orderLevelConfigItems = [];
        // row is not required, only for orderhistory, amazon thankyou etc.
        if (modelJson["row"]) {
            this.orderLevelConfigItemRow = new order_level_config_item_1.OrderLevelConfigItem('row', modelJson.row);
        }
        //Keys are cartTotal, orderID, cartID        
        const keys = Object.keys(modelJson);
        keys.forEach(key => {
            if (key !== 'row' && key != 'scriptJson' && key != 'pageSubType') {
                const item = new order_level_config_item_1.OrderLevelConfigItem(key, modelJson[key]);
                this.orderLevelConfigItems.push(item);
            }
        });
        if (modelJson.scriptJson) {
            this.scriptJson = new script_json_config_1.ScriptJsonConfig(modelJson.scriptJson);
        }
        if (modelJson.isJson) {
            this.isJson = modelJson.isJson;
        }
        if (modelJson.pageSubType) {
            this.pageSubType = modelJson.pageSubType;
        }
    }
}
exports.OrderConfigSet = OrderConfigSet;

},{"./order-level-config-item":5,"./script-json-config":8}],5:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderLevelConfigItem = void 0;
const selector_config_item_1 = require("./selector-config-item");
class OrderLevelConfigItem extends selector_config_item_1.SelectorConfigItem {
    constructor(name, modelJson) {
        super(name, modelJson);
        //cartID and orderID not currency
        if (name === "cartTotal") {
            this.isCurrency = true;
        }
        else {
            this.isCurrency = false;
        }
    }
}
exports.OrderLevelConfigItem = OrderLevelConfigItem;

},{"./selector-config-item":9}],6:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProductConfigItem = void 0;
const selector_config_item_1 = require("./selector-config-item");
class ProductConfigItem extends selector_config_item_1.SelectorConfigItem {
    constructor(name, modelJson) {
        super(name, modelJson);
        // TODO 5.0 setup formatting here as done in orderConfig 
        // https://jira.prodegehq.com/browse/BTN-1670 
        // qty - numeric 
        // price - currency 
        // link - string.. etc..       
        // but better here, than factory 
        if (name === "price") {
            this.isCurrency = true;
        }
        else {
            this.isCurrency = false;
        }
        // we want to get rid of alpha/symbols, so just numbers, but we can't use Numeric DataType as it causes strange rounding issues on large numbers 
        if (name === "upc") {
            this.isLongNumericString = true;
        }
        else {
            this.isLongNumericString = false;
        }
        if (name === "qty") {
            this.isNumeric = true;
        }
        else {
            this.isNumeric = false;
        }
    }
}
exports.ProductConfigItem = ProductConfigItem;

},{"./selector-config-item":9}],7:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProductConfigSet = void 0;
const product_config_item_1 = require("./product-config-item");
const script_json_config_1 = require("./script-json-config");
class ProductConfigSet {
    constructor(modelJson) {
        this.productConfigItems = [];
        //add 'row' first as it is required
        this.productConfigItemRow = new product_config_item_1.ProductConfigItem('row', modelJson.row);
        //add other items like name,link,productid, but only the ones that are included
        const keys = Object.keys(modelJson);
        keys.forEach(key => {
            if (key !== 'row' && key != 'scriptJson') {
                const item = new product_config_item_1.ProductConfigItem(key, modelJson[key]);
                this.productConfigItems.push(item);
            }
        });
        if (modelJson.scriptJson) {
            this.scriptJson = new script_json_config_1.ScriptJsonConfig(modelJson.scriptJson);
        }
    }
}
exports.ProductConfigSet = ProductConfigSet;

},{"./product-config-item":6,"./script-json-config":8}],8:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ScriptJsonConfig = void 0;
class ScriptJsonConfig {
    constructor(scriptJson) {
        this.scriptJsonSelector = scriptJson.scriptJsonSelector;
        this.scriptJsonPreManipulator = scriptJson.scriptJsonPreManipulator;
    }
}
exports.ScriptJsonConfig = ScriptJsonConfig;

},{}],9:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SelectorConfigItem = void 0;
class SelectorConfigItem {
    constructor(name, modelJson) {
        this.name = name;
        this.selector = modelJson.selector;
        this.manipulator = modelJson.manipulator;
        this.attribute = modelJson.attribute;
        // because rows can be set to null, we need to explicitly check for ===null
        if (modelJson && (modelJson.useDefault || modelJson.useDefault === null)) {
            this.useDefault = true;
            if (modelJson.useDefault === null) {
                this.defaultValue = null;
            }
            else {
                this.defaultValue = modelJson.useDefault;
            }
        }
        if (modelJson && modelJson.useType) {
            this.useType = true;
            // keeping for now for backwards compatability. This can be removed after all Json files instances of "useType": "TRUE" or "useType": "FALSE" are gone
            if (modelJson.useType === 'FALSE') {
                this.useType = false;
            }
        }
        else {
            this.useType = false;
        }
        if (modelJson && modelJson.useUrl) {
            this.useUrl = true;
        }
        else {
            this.useUrl = false;
        }
        if (modelJson && modelJson.useFullPage) {
            this.useFullPage = true;
        }
        else {
            this.useFullPage = false;
        }
    }
}
exports.SelectorConfigItem = SelectorConfigItem;

},{}],10:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DataInsightsFactory = void 0;
const data_insights_result_1 = require("./results/data-insights-result");
const merchant_config_1 = require("./configs/merchant-config");
const log_1 = require("./log");
const order_result_1 = require("./results/order-result");
const json_script_parser_1 = require("./json-script-parser");
const deep_scraper_1 = require("./deep-scraper");
const html_parser_1 = require("./html-parser");
const scrapeMethod_1 = require("./models/scrapeMethod");
const scrapePageSource_1 = require("./models/scrapePageSource");
class DataInsightsFactory {
    constructor() {
        this.diResult = new data_insights_result_1.DataInsightsResult();
        this.sendDiResult = true;
    }
    async runDataInsightsWhenReady(siteData, modelJson, source, clientId, debugging, fullModelJson) {
        log_1.Log.consoleLog('in di runDataInsightsWhenReady()');
        this.initialSetup(siteData, modelJson, source, clientId, debugging);
        try {
            const self = this;
            let isReady = false;
            this.merchantConfig.deepScrapeConfig ? true : false;
            if (!isReady) {
                isReady = await this.initialElementCheck();
                log_1.Log.consoleLog('result of isReady after IEC', isReady);
            }
            if (isReady) {
                log_1.Log.consoleLog('All Ready, lets go...');
                self.getData(siteData.tab.url, modelJson, fullModelJson);
            }
            else {
                log_1.Log.consoleLog('was NEVER READY');
                this.diResult.generalMessage = "Page was not ready";
            }
        }
        catch (ex) {
            //errors have no enumerable objects, and thus can't be serialized
            log_1.Log.consoleLog('Error IN  FACTORY setupEventOnUnloadListener()', ex);
            this.diResult.exception = { 'exception': ex.stack };
            chrome.runtime.sendMessage({
                type: 0,
                value: this.diResult
            });
        }
    }
    async initialElementCheck() {
        let self = this;
        let orderRowTest;
        let productSelector;
        let productRowTest;
        // look for order row selector or if not (like cart page) first orderitem (like cartTotal) 
        let orderSelector = self.merchantConfig.orderConfigSet[0].orderLevelConfigItemRow ?
            self.merchantConfig.orderConfigSet[0].orderLevelConfigItemRow.selector :
            self.merchantConfig.orderConfigSet[0].orderLevelConfigItems[0].selector;
        var check = function () {
            orderRowTest = document.querySelectorAll(orderSelector).length > 0;
            if (orderRowTest) {
                if (self.merchantConfig.productConfigSet[0].productConfigItemRow) {
                    productSelector =
                        self.merchantConfig.productConfigSet[0].productConfigItemRow ?
                            self.merchantConfig.productConfigSet[0].productConfigItemRow.selector :
                            self.merchantConfig.productConfigSet[0].productConfigItemRow[0].selector;
                    productRowTest = document.querySelectorAll(productSelector).length > 0;
                    if (productRowTest) {
                        return true;
                    }
                    else {
                        return false;
                    }
                }
                else {
                    return true;
                }
            }
            else {
                return false;
            }
        };
        try {
            // for deepscraping, we are not using the initial page, thus we should jump into it, 
            // but let's give it at least 2 seconds (5 half second loops) before we hammer the server with requests, 
            // so the visual page can make all of it's required calls first.
            if (this.merchantConfig.deepScrapeConfig?.enabled && this.merchantConfig.deepScrapeConfig.waitForIntervals) {
                await this.waitFor(check, this.merchantConfig.deepScrapeConfig.waitForIntervals);
            }
            else {
                await this.waitFor(check);
            }
            // This is a temp fix for intermittent merchant issues. 
            // TODO
            // https://jira.prodegehq.com/browse/BTN-2282
            await new Promise(resolve => setTimeout(resolve, 500));
            return true;
        }
        catch (x) {
            let logMessage = "checkInitialElements Failed. ";
            if (!orderRowTest) {
                logMessage += "Did not find first item or row order selector:" + orderSelector;
            }
            else if (!productRowTest) {
                logMessage += "Did not find first item or row product selector:" + productSelector;
            }
            else {
                logMessage += "Something went wrong in IEC";
            }
            let runAnyway = false;
            if (self.merchantConfig.deepScrapeConfig?.enabled) {
                logMessage += ", but deepScrape so go for it anyway.";
                runAnyway = true;
            }
            if (self.merchantConfig.orderConfigSet.some(orderConfigSet => orderConfigSet.scriptJson)) {
                logMessage += ", but is jsonConfig so go for it anyway.";
                runAnyway = true;
            }
            if (x) {
                log_1.Log.consoleLog(logMessage, x.toString());
            }
            else {
                log_1.Log.consoleLog(logMessage);
            }
            if (runAnyway) {
                return true;
            }
            return false;
        }
    }
    async waitFor(fn, pollMaxCount = 12) {
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
                            log_1.Log.consoleLog(`not quite ready yet... loopCount ${loopCount + 1}`);
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
    // TODO Remove after 10.0 Release
    setupEventOnUnloadListener(siteData, modelJson, source, clientId, debugging) {
        this.initialSetup(siteData, modelJson, source, clientId, debugging);
        try {
            const self = this;
            if (source !== "scriptTesterPopupButton") {
                log_1.Log.consoleLog('setup beforeunload event in dataInightsFactory');
                window.addEventListener('beforeunload', function (e) {
                    log_1.Log.consoleLog('window beforeunload CAUGHT event in dataInightsFactory .');
                    self.getData(siteData.tab.url, modelJson);
                });
            }
            else {
                //Only used by CouponScriptTester - on Popup Button Click. Run now, don't wait on unload event.
                log_1.Log.consoleLog('from popup button.. just run now.. in dataInightsFactory .');
                self.getData(siteData.tab.url, modelJson);
            }
        }
        catch (ex) {
            //errors have no enumerable objects, and thus can't be serialized
            log_1.Log.consoleLog('Error IN  FACTORY setupEventOnUnloadListener()', ex);
            this.diResult.exception = { 'exception': ex.stack };
            chrome.runtime.sendMessage({
                type: 0,
                value: this.diResult
            });
        }
    }
    initialSetup(siteData, modelJson, source, clientId, debugging) {
        if (debugging) {
            log_1.Log.showDebugging = true;
        }
        //this needs to happen early, or else errors won't messages don't make it back to core.
        if (clientId) {
            this.diResult.clientID = clientId;
        }
        log_1.Log.consoleLog('initialSetup. siteData ', siteData);
        log_1.Log.consoleLog('initialSetup. Full modelJson ', modelJson);
        var pageType;
        var pageMatch;
        if (siteData.pages && siteData.pageMatch) {
            const pageKeys = Object.keys(siteData.pages);
            if (pageKeys.includes(siteData.pageMatch)) {
                pageType = siteData.pages[siteData.pageMatch];
                pageMatch = siteData.pageMatch;
            }
            else {
                // TODO TEMP to account for extra slashes, verify this can be removed this after EMS-1487
                if (pageKeys.includes(siteData.pageMatch.substring(0, siteData.pageMatch.length - 1))) {
                    pageType = siteData.pages[siteData.pageMatch.substring(0, siteData.pageMatch.length - 1)];
                    pageMatch = siteData.pageMatch.substring(0, siteData.pageMatch.length - 1);
                }
            }
        }
        this.diResult.pageMatch = pageMatch;
        this.diResult.pageType = pageType;
        this.diResult.source = source;
        this.diResult.url = siteData.tab.url;
        if (siteData.tab && siteData.tab.tabId) {
            this.diResult.tabID = siteData.tab.tabId;
        }
        if (siteData.id) {
            this.diResult.siteID = siteData.id;
        }
        if (siteData.tab.timeStamp) {
            this.diResult.ts = siteData.tab.timeStamp;
        }
        this.setupMerchantConfig(siteData.tab.url, modelJson);
    }
    setupMerchantConfig(url, modelJson) {
        this.merchantConfig = new merchant_config_1.MerchantConfig(modelJson);
        if (!this.merchantConfig) {
            this.diResult.addToGeneralMessage(`No Merchant Config Matched for current url: ${url} with current modelJson: ${JSON.stringify(modelJson)}`);
            log_1.Log.consoleLog('adding general message ' + this.diResult.generalMessage);
            const dataInsightResultEvent = new CustomEvent('dataInsightResults', { 'detail': this.diResult });
            document.dispatchEvent(dataInsightResultEvent);
            return;
        }
        log_1.Log.consoleLog('Individual url part of merchant config', this.merchantConfig);
    }
    // Main Method
    async getData(url, modelJson, fullModelJson) {
        try {
            log_1.Log.consoleLog('START FACTORY getData()');
            if (this.merchantConfig.emptyCartSelector && document.querySelector(this.merchantConfig.emptyCartSelector)) {
                this.sendDiResult = false;
            }
            // Only start deepScrape here if enabled AND we have at least one parent httpConfig
            else if (this.merchantConfig.deepScrapeConfig?.enabled && this.merchantConfig.deepScrapeConfig.httpConfigs) {
                log_1.Log.consoleLog('******************* DEEP SCRAPE with parent ****');
                this.diResult.scrapeMethod = scrapeMethod_1.ScrapeMethod.DeepScrape;
                this.diResult = await deep_scraper_1.DeepScraper.runDeepScrape(this.diResult, this.merchantConfig, fullModelJson);
                log_1.Log.consoleLog('this.diResult ', JSON.parse(JSON.stringify(this.diResult)));
            }
            else {
                this.diResult.scrapeMethod = scrapeMethod_1.ScrapeMethod.Standard;
                // orderConfigSet / productConfigSet:  Usually only one. But sometimes we need two sets of selectors for a single page 
                //      multiple productConfigSets : HomeDepot Checkout,Staples Cart... can result in extra items w/ errors
                //      multiple orderConfigSets : Target Thankyou (untested)
                //      in these cases we need to loop through both of these sets and try both selectors
                // orders : is when there are multiple orders on a single page (like order history)
                //       When multiple orders, we want to loop through the orders and get the children for each.
                let jsonOrderSetsWithRows = [];
                let htmlOrderSetsWithRows = [];
                this.merchantConfig.orderConfigSet.forEach(orderConfigSet => {
                    if (orderConfigSet.scriptJson) {
                        jsonOrderSetsWithRows.push(orderConfigSet);
                    }
                    else if (orderConfigSet.orderLevelConfigItemRow) {
                        htmlOrderSetsWithRows.push(orderConfigSet);
                    }
                });
                log_1.Log.consoleLog('*** jsonOrderSetsWithRows.length', jsonOrderSetsWithRows.length);
                log_1.Log.consoleLog('*** htmlOrderSetsWithRows.length', htmlOrderSetsWithRows.length);
                let orderCounter = 0;
                if (jsonOrderSetsWithRows.length > 0) {
                    log_1.Log.consoleLog('*************************** JSON **************************');
                    this.diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.JsonOnPage;
                    try {
                        this.diResult = json_script_parser_1.JSONScriptParser.parseJsonScript(this.diResult, this.merchantConfig);
                        //in case we have both html and json configured, we want to make sure html doesn't overwrite json.
                        if (this.diResult.orders && this.diResult.orders.length > 0) {
                            orderCounter = this.diResult.orders.length;
                        }
                    }
                    catch (ex) {
                        log_1.Log.consoleLog('JSON processing order error', ex);
                    }
                }
                if (htmlOrderSetsWithRows.length > 0) {
                    log_1.Log.consoleLog('*************************** HTML with Order Rows **************************');
                    this.diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.Html;
                    let htmlOrders;
                    let nonJsonProductConfigSets = this.merchantConfig.productConfigSet.filter(prodConfigSet => !prodConfigSet.scriptJson);
                    htmlOrders = document.querySelectorAll(htmlOrderSetsWithRows[0].orderLevelConfigItemRow.selector);
                    // if we have both JSON and HTML, but this is a JSON page, we will have no htmlOrders and thus this will all be skipped..
                    htmlOrders.forEach(orderElement => {
                        let parentDocument = orderElement;
                        this.diResult.orders[orderCounter] = new order_result_1.OrderResult();
                        html_parser_1.HtmlParser.getOrders(parentDocument, htmlOrderSetsWithRows, this.diResult.orders[orderCounter]);
                        html_parser_1.HtmlParser.getProducts(parentDocument, nonJsonProductConfigSets, this.diResult.orders[orderCounter]);
                        orderCounter++;
                    });
                }
                else if (htmlOrderSetsWithRows.length === 0 && jsonOrderSetsWithRows.length === 0) {
                    log_1.Log.consoleLog('*************************** HTML withOUT Order Rows (cart pages etc..) **************************');
                    this.diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.Html;
                    //no order rows, single order (most cart, checkout, thankyou pages)
                    // We do have an OrderArray, but only has cartTotal etc, no row:{ selector } in orderConfigSet
                    this.diResult.orders[0] = new order_result_1.OrderResult();
                    try {
                        html_parser_1.HtmlParser.getOrders(document.documentElement, this.merchantConfig.orderConfigSet, this.diResult.orders[0]);
                        html_parser_1.HtmlParser.getProducts(document.documentElement, this.merchantConfig.productConfigSet, this.diResult.orders[0]);
                    }
                    catch (ex) {
                        log_1.Log.consoleLog('Error processing single order ', ex);
                    }
                }
                // if we have both html and json config, let's merge the results
                if (jsonOrderSetsWithRows.length > 0 && htmlOrderSetsWithRows.length > 0) {
                    this.diResult = this.mergeDIResults(this.diResult);
                }
                if (this.merchantConfig.deepScrapeConfig?.enabled && this.merchantConfig.deepScrapeConfig.childHttpConfig) {
                    log_1.Log.consoleLog('******************* DEEP SCRAPE with only child****');
                    this.diResult.scrapeMethod = scrapeMethod_1.ScrapeMethod.DeepScrape;
                    var orderSummaryTempDIResult = new data_insights_result_1.DataInsightsResult();
                    orderSummaryTempDIResult = JSON.parse(JSON.stringify((this.diResult)));
                    this.diResult.orders = [];
                    await deep_scraper_1.DeepScraper.processChildHttpConfigs(fullModelJson, this.merchantConfig, orderSummaryTempDIResult, this.diResult);
                }
                log_1.Log.consoleLog(`Dispatching generalMessage ${this.diResult.generalMessage} `);
                log_1.Log.consoleLog('Dispatching runtime message DIFactory Results', this.diResult);
            }
        }
        catch (ex) {
            //errors have no enumerable objects, and thus can't be serialized
            log_1.Log.consoleLog(' Error IN FACTORY getdata()', ex);
            this.diResult.exception = { 'exception': ex.stack };
        }
        finally {
            // we may have set sendDiResult to false if faled IEC etc. 
            // if doing deep scrape, we may have already sent some or all the orders  
            if (this.sendDiResult && (this.diResult.orders?.length > 0 || this.diResult.exception)) {
                log_1.Log.consoleLog(`Dispatching generalMessage ${this.diResult.generalMessage} `);
                log_1.Log.consoleLog('Dispatching runtime message DIFactory Results', this.diResult);
                chrome.runtime.sendMessage({
                    type: 0,
                    value: this.diResult
                });
            }
        }
    }
    mergeDIResults(diResult) {
        // orderKeys is a combination of orderId and orderDate, as some merchants use 0 for inPerson orderIds etc.
        log_1.Log.consoleLog(`merging diResults `);
        let orderKeys;
        let ordersWithIdAndDate = diResult.orders.filter(order => order.orderID && order.orderDate);
        if (ordersWithIdAndDate.length === diResult.orders.length) {
            orderKeys = diResult.orders.filter(order => order.orderID).map((order, index) => {
                return order.orderID + "_" + order.orderDate;
            });
        }
        if (orderKeys && this.hasDuplicates(orderKeys)) {
            log_1.Log.consoleLog(`merging diResults - we have duplicates, merging results diResults. Before merge`, JSON.parse(JSON.stringify(diResult)));
            let diResultTarget = new data_insights_result_1.DataInsightsResult();
            Object.keys(diResult).forEach(key => {
                if (key !== "orders") {
                    diResultTarget[key] = diResult[key];
                }
            });
            diResult.orders.forEach(thisOrder => {
                let dups = diResult.orders.filter(order => order.orderID === thisOrder.orderID && order.orderDate === thisOrder.orderDate);
                if (dups.length > 1) {
                    // only do merge if first time we've encountered this orderID.....else ignore/skip
                    if (diResultTarget.orders && !diResultTarget.orders.find(order => order.orderID === thisOrder.orderID && order.orderDate === thisOrder.orderDate)) {
                        //compare the two and merge, There should never be more than 2.
                        // TODO do we need to handle more than 2
                        let newMergedOrder = this.mergeOrder(dups[0], dups[1]);
                        diResultTarget.orders.push(newMergedOrder);
                    }
                }
                else {
                    diResultTarget.orders.push(thisOrder);
                }
            });
            return diResultTarget;
        }
        else {
            // if no results, stick with original
            return diResult;
        }
    }
    hasDuplicates(arr) {
        return new Set(arr).size !== arr.length;
    }
    // current priority is 'exist/doesNotExist'... we might add priorities later
    mergeOrder(order1, order2) {
        // Object.Assign only goes one level deep on objects
        // productLevel
        let allProducts = [];
        let count = 0;
        order1.products.forEach(product1 => {
            if (order2.products && order2.products[count]) {
                Object.assign(product1, order2.products[count]);
            }
            count++;
            allProducts.push(product1);
        });
        // now do orderLevel
        Object.assign(order1, order2);
        // now update outerlevel with inner level
        order1.products = allProducts;
        return order1;
    }
}
exports.DataInsightsFactory = DataInsightsFactory;
if (typeof (window) !== "undefined") {
    window['Prdg'] = window['Prdg'] || {};
    window['Prdg']['DataInsightsFactory'] = DataInsightsFactory;
}

},{"./configs/merchant-config":3,"./deep-scraper":11,"./html-parser":12,"./json-script-parser":14,"./log":15,"./models/scrapeMethod":18,"./models/scrapePageSource":19,"./results/data-insights-result":20,"./results/order-result":22}],11:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeepScraper = void 0;
const merchant_config_1 = require("./configs/merchant-config");
const data_insights_result_1 = require("./results/data-insights-result");
const http_config_1 = require("./configs/http-config");
const json_script_parser_1 = require("./json-script-parser");
const html_parser_1 = require("./html-parser");
const order_result_1 = require("./results/order-result");
const log_1 = require("./log");
const json_parser_1 = require("./json-parser");
const scrapePageSource_1 = require("./models/scrapePageSource");
const pageSubType_1 = require("./models/pageSubType");
class DeepScraper {
    static constructRequest() {
        return new XMLHttpRequest();
    }
    static async runDeepScrape(diResult, merchantConfig, fullModelJson) {
        let hasChildHttpConfigs = false;
        var self = this;
        if (merchantConfig.deepScrapeConfig.childHttpConfig) {
            hasChildHttpConfigs = true;
            // Is temporary, as it is where we hold the values we get from the parent page, so we can find the inner pages to fill the real diResult.
            var orderSummaryTempDIResult = new data_insights_result_1.DataInsightsResult();
        }
        // Usually will be a single httpConfig. But sometimes we need more for instore & online, or multiple dates like Costco
        for (const httpConfig of merchantConfig.deepScrapeConfig.httpConfigs) {
            let htmlOrders;
            if (merchantConfig.deepScrapeConfig.returnType === "html") {
                diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.Html;
                let httpConfigToUse = new http_config_1.HttpConfig(JSON.parse(JSON.stringify(httpConfig)));
                let deepScrapeData = await self.getData(merchantConfig.deepScrapeConfig, httpConfigToUse);
                let returnDoc = self.htmlDomParser(deepScrapeData);
                if (merchantConfig.orderConfigSet[0].scriptJson) {
                    diResult = await json_script_parser_1.JSONScriptParser.parseJsonScript(diResult, merchantConfig, deepScrapeData);
                }
                else {
                    // get OrderRows HTML elements
                    htmlOrders = returnDoc.querySelectorAll(merchantConfig.orderConfigSet[0].orderLevelConfigItemRow.selector);
                    htmlOrders.forEach(orderElement => {
                        let orderResult = new order_result_1.OrderResult();
                        html_parser_1.HtmlParser.getOrders(orderElement, merchantConfig.orderConfigSet, orderResult);
                        if (hasChildHttpConfigs) {
                            // will get products below afer all orders collected
                            orderSummaryTempDIResult.orders.push(orderResult);
                        }
                        else {
                            // TODO .. Probably need HtmlParser.getProducts() here. No current samples
                            diResult.orders.push(orderResult);
                        }
                    });
                }
            }
            else if (merchantConfig.deepScrapeConfig.returnType === "json") {
                diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.JsonFromApi;
                // diResults are cumulative across all httpConfigs
                let diResultOrdersCounter = diResult.orders?.length ? diResult.orders.length : 0;
                let currentCursor = "";
                for (let pageNumber = 1; pageNumber <= merchantConfig.deepScrapeConfig.maxPageNumbers; pageNumber++) {
                    // reset httpConfigToUse each loop
                    let httpConfigToUse = new http_config_1.HttpConfig(JSON.parse(JSON.stringify(httpConfig)));
                    DeepScraper.setupHttpConfigToUse(merchantConfig, httpConfigToUse, pageNumber, currentCursor);
                    let deepScrapeData = await self.getData(merchantConfig.deepScrapeConfig, httpConfigToUse);
                    try {
                        await json_script_parser_1.JSONScriptParser.parseJsonScript(diResult, merchantConfig, deepScrapeData);
                    }
                    catch (e) {
                        //TODO We can fail on parseJSON, if our loop runs off the end. We should we be able to configure a 'no results' check...
                        // but it is quite a bit different for each merchant.
                        log_1.Log.consoleLog('ParseJson Failed. May just be we ran off end...');
                    }
                    if (merchantConfig.deepScrapeConfig.useCursor) {
                        currentCursor = json_parser_1.JSONParser.parseJson(merchantConfig.deepScrapeConfig.cursorSelector, deepScrapeData).value;
                        // known end of orders no 'next' cursor..
                        if (currentCursor === undefined) {
                            break;
                        }
                    }
                    // Every merchant has different indicator for, 'you've run off the end of the orders...no more pages'
                    // This is attempt to stop looping if no new results, also so we don't make a bunch of calls, if no orders..
                    if (diResult.orders.length === diResultOrdersCounter) {
                        // TODO BTN-2169 Probably should return diResults here or higher (batched results)
                        break;
                    }
                    diResultOrdersCounter = diResult.orders.length;
                    if (hasChildHttpConfigs) {
                        diResult.orders.forEach(order => {
                            // will get products below afer all orders collected
                            orderSummaryTempDIResult.orders.push(order);
                        });
                        diResult.orders = [];
                    }
                }
            }
        }
        if (hasChildHttpConfigs) {
            await DeepScraper.processChildHttpConfigs(fullModelJson, merchantConfig, orderSummaryTempDIResult, diResult);
        }
        // for deepscraping even if we started at OHSummary, this should be logged as OHDetails, as we are going 'Deep' and 'Wide'
        // for example, if we are doing partialRollout, we'd want deep to be prioritized over non deep.
        diResult.orders.forEach(order => {
            order.pageSubType = pageSubType_1.PageSubType.OrderHistoryDetails;
        });
        return diResult;
    }
    static setupHttpConfigToUse(merchantConfig, httpConfigToUse, pageNumber, currentCursor) {
        const pageSizePlaceholder = '{pageSize}';
        const pageNumberPlaceholder = '{pageNumber}';
        const cursorPlaceholder = '{cursor}';
        const offsetPlaceholder = '{offset}';
        if (httpConfigToUse.url.includes(offsetPlaceholder) && httpConfigToUse.url.includes(pageSizePlaceholder)) {
            httpConfigToUse.url = httpConfigToUse.url.replace(offsetPlaceholder, this.currentOffset.toString());
            this.currentOffset = this.currentOffset += merchantConfig.deepScrapeConfig.pageSize;
        }
        if (merchantConfig.deepScrapeConfig.pageSize) {
            if (httpConfigToUse.url.includes(pageSizePlaceholder)) {
                httpConfigToUse.url = httpConfigToUse.url.replace(pageSizePlaceholder, merchantConfig.deepScrapeConfig.pageSize.toString());
            }
            if (httpConfigToUse.body?.includes(pageSizePlaceholder)) {
                httpConfigToUse.body = httpConfigToUse.body.replace(pageSizePlaceholder, merchantConfig.deepScrapeConfig.pageSize.toString());
            }
        }
        if (httpConfigToUse.url.includes(pageNumberPlaceholder)) {
            httpConfigToUse.url = httpConfigToUse.url.replace(pageNumberPlaceholder, pageNumber.toString());
        }
        if (merchantConfig.deepScrapeConfig.useCursor) {
            if (httpConfigToUse.body?.includes(cursorPlaceholder)) {
                httpConfigToUse.body = httpConfigToUse.body.replace(cursorPlaceholder, currentCursor.toString());
                httpConfigToUse.body = httpConfigToUse.body;
            }
        }
        log_1.Log.consoleLog('httpConfigToUse', httpConfigToUse);
    }
    static setupChildHttpConfigToUse(httpConfigToUse, parentKey) {
        const parentKeyTemplate = '{parentKey}';
        if (parentKey) {
            if (httpConfigToUse.url.includes(parentKeyTemplate)) {
                httpConfigToUse.url = httpConfigToUse.url.replace(parentKeyTemplate, parentKey.toString());
            }
            if (httpConfigToUse.body?.includes(parentKeyTemplate)) {
                httpConfigToUse.body = httpConfigToUse.body.replace(parentKeyTemplate, parentKey.toString());
            }
        }
        log_1.Log.consoleLog('httpConfigToUse', httpConfigToUse);
    }
    // if HTML will usually be the individual Order Summary Details pages, if API, the equivalent of the details page.
    static async processChildHttpConfigs(fullModelJson, merchantConfig, orderSummaryTempDIResult, diResult) {
        let childOrderConfigSet, childProductConfigSet;
        let childMerchantConfig = new merchant_config_1.MerchantConfig(fullModelJson[merchantConfig.deepScrapeConfig.childPathKey]);
        childOrderConfigSet = childMerchantConfig.orderConfigSet;
        childProductConfigSet = childMerchantConfig.productConfigSet;
        let parentOrders = orderSummaryTempDIResult.orders;
        let parentOrdersLength = orderSummaryTempDIResult.orders.length;
        log_1.Log.consoleLog('Starting childHttpConfigs. ParentOrders:', parentOrders);
        // Needs to be old structure, to avoid Async Issues.
        for (let i = 0; i < parentOrdersLength; i++) {
            let childHttpConfigToUse = JSON.parse(JSON.stringify((merchantConfig.deepScrapeConfig.childHttpConfig)));
            let order = parentOrders[i];
            let orderKey = merchantConfig.deepScrapeConfig.parentKey;
            // often the orderID or possibly the entire URL.
            let orderValue = order[orderKey];
            if (orderKey) {
                DeepScraper.setupChildHttpConfigToUse(childHttpConfigToUse, orderValue);
                let deepScrapeData;
                try {
                    deepScrapeData = await DeepScraper.getData(merchantConfig.deepScrapeConfig, childHttpConfigToUse);
                }
                catch (e) {
                    log_1.Log.consoleLog('Problem getting child order. err:', e);
                }
                if (merchantConfig.orderConfigSet[0].scriptJson) {
                    diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.JsonFromApi;
                    diResult = await json_script_parser_1.JSONScriptParser.parseJsonScript(diResult, childMerchantConfig, deepScrapeData);
                }
                else {
                    let returnDoc = DeepScraper.htmlDomParser(deepScrapeData);
                    let orderResult = new order_result_1.OrderResult();
                    try {
                        // TODO add ability to parse JSON from inside HTML - BTN-2166
                        diResult.scrapePageSource = scrapePageSource_1.ScrapePageSource.Html;
                        orderResult = html_parser_1.HtmlParser.getOrders(returnDoc, childOrderConfigSet, orderResult);
                        html_parser_1.HtmlParser.getProducts(returnDoc, childProductConfigSet, orderResult);
                        diResult.orders.push(orderResult);
                    }
                    catch (e) {
                        log_1.Log.consoleLog('Problem parsing child order. err:', e);
                    }
                }
            }
            else {
                log_1.Log.consoleLog('No order key');
            }
            // leftovers not caught by this will be sent with final standard 'sendMessage' in DIFactory
            if (merchantConfig.deepScrapeConfig.sendPartialResultCount && ((i + 1) % merchantConfig.deepScrapeConfig.sendPartialResultCount === 0)) {
                chrome.runtime.sendMessage({
                    type: 0,
                    value: diResult
                });
                diResult.orders = [];
            }
        }
    }
    // Todo, probably should be private, but need to get spys working with private
    static async getData(deepScrapeConfig, httpConfig) {
        // if html pages...
        if (deepScrapeConfig.returnType === "html") {
            let response = await this.callHtml(httpConfig);
            return response;
        }
        // if json api.. 
        else if (deepScrapeConfig.returnType === "json") {
            return await this.callApi(httpConfig);
        }
        else {
            log_1.Log.consoleLog("deepScraper getDatainvalid() return type");
            return;
        }
    }
    static async callApi(httpConfig) {
        try {
            let response = await this.processRequest(httpConfig);
            return response;
        }
        catch (e) {
            log_1.Log.consoleLog("DeepScraper API error processing request", e);
            return;
        }
    }
    // TODO - handle LazyLoads BTN-2165
    static async callHtml(httpConfig) {
        try {
            let response = await this.processRequest(httpConfig);
            return response;
        }
        catch (e) {
            log_1.Log.consoleLog("DeepScraper HTML error processing request", e);
            return;
        }
    }
    // despite being async, this not work with lazy loaded pages, that rely upon javascript running and loading the html. Would probably require loading the return into a headless browser.
    static async processRequest(config) {
        log_1.Log.consoleLog('Processing httpConfig', config);
        return new Promise((res, rej) => {
            let url = config.url;
            let request = this.constructRequest();
            request.onreadystatechange = async () => {
                if (request.readyState === 4) {
                    if (request.status === 200) {
                        let response = null;
                        if (request.responseText) {
                            response = request.responseText;
                        }
                        res(response);
                    }
                    else {
                        log_1.Log.consoleLog(`HTTP onreadystatechange not 200 status : ${request.status}  `);
                        rej();
                    }
                }
            };
            request.open(config.method, url, true);
            let headers = config.headers;
            if (headers) {
                Object.keys(headers).forEach(k => {
                    request.setRequestHeader(k, (headers[k]));
                });
            }
            let body = null;
            if (config.body) {
                body = config.body;
            }
            request.withCredentials = true;
            if (config.rateLimit) {
                window.setTimeout(() => {
                    request.send(body);
                }, config.rateLimit);
            }
            else {
                request.send(body);
            }
        });
    }
    static htmlDomParser(response) {
        var htmlDoc;
        try {
            var parser = new window.DOMParser;
            htmlDoc = parser.parseFromString(response, "text/html");
            // TODO ?
            // // Sometimes, (walmart - previous sample HTML was inside object) the returned page is inside some other stuff.
            // if (modelConfig.returnIsHtml.DOMSelector) {
            //     htmlDoc = htmlDoc.querySelector(modelConfig.returnIsHtml.DOMSelector);
            // }
        }
        catch (e) {
            log_1.Log.consoleLog('htmlDomParser ERROR , e is ', e);
        }
        return htmlDoc;
    }
}
exports.DeepScraper = DeepScraper;
DeepScraper.currentOffset = 0;

},{"./configs/http-config":2,"./configs/merchant-config":3,"./html-parser":12,"./json-parser":13,"./json-script-parser":14,"./log":15,"./models/pageSubType":16,"./models/scrapePageSource":19,"./results/data-insights-result":20,"./results/order-result":22}],12:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HtmlParser = void 0;
const log_1 = require("./log");
const manipulated_string_1 = require("./results/manipulated-string");
const product_result_1 = require("./results/product-result");
const string_formatter_1 = require("./string-formatter");
const string_manipulator_1 = require("./string-manipulator");
class HtmlParser {
    // mostly same as CI after first line, except added try/catches, and return type 
    // currenty return .value can be string or Json Object.. usually a subset of incoming data or just string if that is actually found...
    static getOrders(orderOrDocument, orderConfigSets, orderResult) {
        orderConfigSets.forEach((orderConfig) => {
            if (orderConfig.pageSubType) {
                orderResult.pageSubType = orderConfig.pageSubType;
            }
            orderConfig.orderLevelConfigItems.forEach((config) => {
                if (config.selector || config.useUrl) {
                    var manipulatedString = this.getOrderLevelItem(orderOrDocument, config);
                    if (manipulatedString.skipped || manipulatedString.error) {
                        if (config.useDefault) {
                            log_1.Log.consoleLog(`use Default for  : ${config.name}`);
                            orderResult[config.name] = config.defaultValue;
                        }
                        else {
                            //skipped same?
                            if (manipulatedString.skipped) {
                                log_1.Log.consoleLog(`Skipped manipulatedString.value:${manipulatedString.value}    manipulatedString.error:${manipulatedString.error}`);
                            }
                            orderResult.addErrorItem(manipulatedString.error);
                        }
                        // add even if there is an error(if not found it will be empty, if string manipulation error, go ahead and add full starter string)
                        if (manipulatedString.value) {
                            orderResult[config.name] = manipulatedString.value;
                        }
                    }
                    else {
                        orderResult[config.name] = manipulatedString.value;
                    }
                }
                else {
                    log_1.Log.consoleLog(`no selector found for : ${config.name}`);
                    orderResult.addSkippedItem(`no selector found for : ${config.name}`);
                }
            });
        });
        return orderResult;
    }
    static getOrderLevelItem(orderOrDocument, configItem) {
        let manipulatedString = new manipulated_string_1.ManipulatedString("");
        if ((configItem.selector
            && orderOrDocument.querySelector(configItem.selector))
            || configItem.useUrl
            || configItem.useFullPage) {
            // TODO THIS part should be pulled out into a function that makes it same as products BTN-2067
            if (configItem.useFullPage) {
                let element = document.querySelector(configItem.selector);
                // this section should probably be broken out and genericized for after this section.
                if (element && configItem.attribute) {
                    manipulatedString.value = element.getAttribute(configItem.attribute);
                }
                else {
                    if (document.querySelector(configItem.selector)) {
                        manipulatedString.value = document.querySelector(configItem.selector)?.textContent;
                    }
                }
                if (!manipulatedString.value && configItem.useDefault) {
                    manipulatedString.value = configItem.defaultValue;
                }
                if (!manipulatedString.value) {
                    manipulatedString.addToError(` Error: could not get ${configItem.name} by useUrl, ${configItem.useUrl} `);
                }
            }
            else if (configItem.attribute) {
                let element = orderOrDocument.querySelector(configItem.selector);
                manipulatedString.value = element.getAttribute(configItem.attribute);
                if (!manipulatedString.value) {
                    manipulatedString.addToError(` Error: could not get ${configItem.name} by attribute, ${configItem.attribute} `);
                }
            }
            else if (configItem.useUrl) {
                manipulatedString.value = window.location.href;
                if (!manipulatedString.value) {
                    manipulatedString.addToError(` Error: could not get ${configItem.name} by useUrl, ${configItem.useUrl} `);
                }
            }
            else {
                //this is standard normal flow
                manipulatedString.value = orderOrDocument.querySelector(configItem.selector).textContent;
                let element = orderOrDocument.querySelector(configItem.selector);
                manipulatedString = this.checkAndProcessUseType(manipulatedString, element, configItem);
            }
            manipulatedString = string_manipulator_1.StringManipulator.checkAndProcessStringManipulation(manipulatedString, configItem);
            if (manipulatedString.error) {
                return log_1.Log.logMessageAsIssue(manipulatedString, configItem, `${manipulatedString.error}`);
            }
            manipulatedString = string_formatter_1.StringFormatter.checkAndProcessStringFormatters(manipulatedString, configItem, orderOrDocument);
        }
        else {
            if (!configItem.selector) {
                manipulatedString.skipped = `no selector found for : ${configItem.name}`;
            }
            else {
                manipulatedString.addToError(`unable to get getOrderLevelItem() orderLevelItem Name: ${configItem.name}    selector: ${configItem.selector}`);
            }
        }
        return manipulatedString;
    }
    static getProducts(orderOrDocument, productConfigs, orderResult) {
        log_1.Log.consoleLog('orderOrDocument tagname ', orderOrDocument.tagName);
        productConfigs.forEach((productConfig) => {
            const productRows = orderOrDocument.querySelectorAll(productConfig.productConfigItemRow.selector);
            if (productRows && productRows.length === 0) {
                if (productConfig.productConfigItemRow.useDefault) {
                    if (productConfig.productConfigItemRow.defaultValue === null) {
                        //do nothing, skip this row
                    }
                    ;
                }
                else {
                    orderResult.addErrorItem(`Error: Products row not found. Product Row Selector is ${productConfig.productConfigItemRow.selector}`);
                }
            }
            log_1.Log.consoleLog(' product rows ', productRows.length);
            //list of actual rows of product items on the page.
            productRows.forEach(productRow => {
                const rowResult = new product_result_1.ProductResult();
                productConfig.productConfigItems.forEach(configItem => {
                    let manipulatedString = this.getIndividualProductSection(orderOrDocument, productRow, configItem);
                    if (manipulatedString.skipped || manipulatedString.error) {
                        // if an error, but we have a useDefault, ignore the error/skipped
                        if (configItem.useDefault) {
                            log_1.Log.consoleLog(`use Default for  : ${configItem.name}`);
                            rowResult[configItem.name] = configItem.defaultValue;
                        }
                        else {
                            if (manipulatedString.skipped) {
                                log_1.Log.consoleLog(`Skipped manipulatedString.value:${manipulatedString.value}    manipulatedString.error:${manipulatedString.error}`);
                            }
                            else {
                                rowResult.addErrorItem(manipulatedString.error);
                            }
                        }
                    }
                    // add even if there is an error(if not found it will be empty, if string manipulation error, go ahead and add full starter string)
                    // unless there was an error and a default value 
                    if (manipulatedString.value && !(manipulatedString.error && configItem.defaultValue)) {
                        rowResult[configItem.name] = manipulatedString.value;
                    }
                });
                orderResult.products.push(rowResult);
            });
        });
    }
    static getIndividualProductSection(orderOrDocument, productRow, configItem) {
        let element;
        let item;
        if (configItem.selector !== undefined && configItem.selector === '') {
            element = productRow;
        }
        else if (configItem.selector) {
            element = productRow.querySelector(configItem.selector);
        }
        else {
            // Nothing to do but this is somewhat unexpected..
        }
        let manipulatedString = new manipulated_string_1.ManipulatedString(item);
        if (!element) {
            return log_1.Log.logResultAsIssue(manipulatedString, orderOrDocument, productRow, configItem);
        }
        if (configItem.attribute) {
            try {
                manipulatedString.value = element.getAttribute(configItem.attribute);
                if (!manipulatedString.value) {
                    manipulatedString = this.errorOrDefault(configItem, manipulatedString, ` Error: could not get ${configItem.name} by attribute, ${configItem.attribute} `);
                }
            }
            catch (ex) {
                manipulatedString.addToError(` CATCH Error: could not get ${configItem.name} by attribute, ${configItem.attribute} `);
            }
        }
        else if (configItem.useUrl) {
            manipulatedString.value = window.location.href;
            if (!manipulatedString.value) {
                manipulatedString.addToError(` Error: could not get ${configItem.name} by useUrl, ${configItem.useUrl} `);
            }
        }
        else {
            // this is the standard, normal flow.. need to call generalFormatter before useType, as we want to create the manipulated string and clean it up first
            manipulatedString.value = string_formatter_1.StringFormatter.generalFormatter(element.textContent);
            manipulatedString = this.checkAndProcessUseType(manipulatedString, element, configItem);
        }
        manipulatedString = string_manipulator_1.StringManipulator.checkAndProcessStringManipulation(manipulatedString, configItem);
        if (manipulatedString.error) {
            return log_1.Log.logMessageAsIssue(manipulatedString, configItem, ` ${manipulatedString.error}`);
        }
        manipulatedString = string_formatter_1.StringFormatter.checkAndProcessStringFormatters(manipulatedString, configItem, orderOrDocument, productRow);
        return manipulatedString;
    }
    static errorOrDefault(configItem, manipulatedString, errorString) {
        if (configItem.useDefault) {
            manipulatedString.value = configItem.defaultValue;
        }
        else {
            manipulatedString.addToError(errorString);
        }
        return manipulatedString;
    }
    // tru useType if configured, or if we found nothing with textContent
    static checkAndProcessUseType(manipulatedString, element, configItem) {
        if (!manipulatedString.value || (configItem.useType)) {
            manipulatedString = this.getIndividualElementBasedOnDefaultType(manipulatedString, element);
            if (!manipulatedString.value) {
                //if msg, first 2 paramameters irrelevant.                
                manipulatedString.addToError(` useType Error`);
            }
        }
        return manipulatedString;
    }
    //can not be actual 'Element' type or requires much more complex attribute check
    static getIndividualElementBasedOnDefaultType(manipulatedString, element) {
        log_1.Log.consoleLog(`use element type tagName:${element.tagName} : classlist:${element.classlist}`);
        switch (element.tagName) {
            case 'A':
                manipulatedString.value = element.href;
                break;
            case 'OPTION':
            case 'INPUT':
            case 'SELECT':
                manipulatedString.value = element.value;
                break;
            case 'IMG':
                manipulatedString.value = element.alt;
                break;
            case 'DIV':
            case 'TD':
                manipulatedString.value = element.innerHTML;
            default:
                manipulatedString.error = ` UseType not a known element : element.tagName:${element.tagName}`;
        }
        return manipulatedString;
    }
}
exports.HtmlParser = HtmlParser;

},{"./log":15,"./results/manipulated-string":21,"./results/product-result":24,"./string-formatter":25,"./string-manipulator":26}],13:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JSONParser = void 0;
const parsed_json_1 = require("./results/parsed-json");
const log_1 = require("./log");
class JSONParser {
    // mostly same as CI after first line, except added try/catches, and return type 
    // currenty return .value can be string or Json Object.. usually a subset of incoming data or just string if that is actually found...
    static parseJson(path, data) {
        let parsedJson = new parsed_json_1.ParsedJson();
        // if string change to json, and verify it's valid JSON 
        if (typeof (data) === "string") {
            try {
                data = JSON.parse(data);
            }
            catch (e) {
                log_1.Log.consoleLog('parseJson failed invalid JSON - was passed in as string');
                return parsedJson;
            }
            // if already JSON, verify it's valid JSON 
        }
        else if (typeof (data) === "object") {
            try {
                let test = JSON.parse(JSON.stringify(data));
            }
            catch (e) {
                parsedJson.addToError('parseJson failed. data was invalid JSON - was passed in as object');
                return parsedJson;
            }
        }
        else {
            parsedJson.addToError('parseJson parameter data was not a string or object');
            return parsedJson;
        }
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
                    let { objPathKey, objPathIndex } = JSONParser.getArrayIndex(pathKeys, i);
                    try {
                        data = data[objPathKey][objPathIndex];
                    }
                    catch (e) {
                        parsedJson.addToError(`error parsing JSON when path includes array. Path is ${path}`);
                        return parsedJson;
                    }
                }
                else {
                    // normal non-array flow 
                    try {
                        data = data[pathKeys[i]];
                        if (!data) {
                            parsedJson.addToError(`Nothing found with path key: ${pathKeys[i]} of total path: ${path}`);
                            return parsedJson;
                        }
                    }
                    catch (e) {
                        parsedJson.addToError(`error parsing JSON. Path is ${path}`);
                        return parsedJson;
                    }
                }
            }
        }
        else {
            parsedJson.addToError("No pathkeys");
            return parsedJson;
        }
        parsedJson.value = data;
        return parsedJson;
    }
    // if an array is hardcoded into data string like "...:data.promotions[0].coupon.UUID"
    //TODO handle 'n'  : BTN-2071                   
    static getArrayIndex(pathKeys, i) {
        let pathKeySplit = pathKeys[i].split('[');
        let objPathKey = pathKeySplit[0];
        let objPathIndexLength = pathKeySplit[1].indexOf(']'); // in case index > 1 digit 
        let objPathIndex = parseInt(pathKeySplit[1].substring(0, objPathIndexLength));
        return { objPathKey, objPathIndex };
    }
}
exports.JSONParser = JSONParser;

},{"./log":15,"./results/parsed-json":23}],14:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JSONScriptParser = void 0;
const log_1 = require("./log");
const string_manipulator_1 = require("./string-manipulator");
const manipulated_string_1 = require("./results/manipulated-string");
const order_result_1 = require("./results/order-result");
const product_result_1 = require("./results/product-result");
const string_formatter_1 = require("./string-formatter");
const json_parser_1 = require("./json-parser");
const parsed_json_1 = require("./results/parsed-json");
class JSONScriptParser {
    // This class helps process <script> inside an html page or an API return that includes a JSON object, and organizes the DIResult Object
    // The actual parsing of a specific piece of JSON is doen in other class json-parser.ts
    // TODO I meant to refactor this, but forgot before I submitted PR, so I turned that into a new story, should be relatively small..
    // will get rid of 3rd parameter, and duplication/confusion in line 31/32
    static parseJsonScript(diResult, configSection, jsonApiDataReturn) {
        let orderConfigSet = configSection.orderConfigSet.filter(orderConfigSet => orderConfigSet.scriptJson)[0];
        let productConfigSet = configSection.productConfigSet.filter(productConfigSet => productConfigSet.scriptJson)[0];
        let jsonContent;
        let jsonParsed;
        // api returned json data
        if (jsonApiDataReturn) {
            jsonContent = jsonApiDataReturn;
            if (!jsonContent) {
                log_1.Log.consoleLog('parseJsonScript(): Api returned no json data');
                return diResult;
            }
            jsonParsed = jsonApiDataReturn;
        }
        // go get json from inside HTML page
        else {
            jsonContent = this.getScript(orderConfigSet.scriptJson);
            if (!jsonContent) {
                log_1.Log.consoleLog('parseJsonScript(): No matching script tag found');
                return diResult;
            }
            jsonParsed = JSON.parse(jsonContent);
        }
        if (orderConfigSet.orderLevelConfigItemRow) {
            let orders;
            if (orderConfigSet.orderLevelConfigItemRow.selector.includes(this.ALL_ARRAY)) {
                orders = this.getALLOrdersOrProducts(orderConfigSet.orderLevelConfigItemRow.selector, jsonParsed);
            }
            else {
                orders = json_parser_1.JSONParser.parseJson(orderConfigSet.orderLevelConfigItemRow.selector, jsonParsed);
            }
            if (orders.error) {
                log_1.Log.consoleLog("Error in get parseJson", orders.error);
            }
            else {
                orders.value.forEach(order => {
                    JSONScriptParser.processOrdersAndProducts(order, orderConfigSet, productConfigSet, diResult);
                });
            }
        }
        else {
            JSONScriptParser.processOrdersAndProducts(jsonParsed, orderConfigSet, productConfigSet, diResult);
        }
        return diResult;
    }
    static processOrdersAndProducts(order, orderConfigSet, productConfigSet, diResult) {
        let orderResult = this.getOrder(order, orderConfigSet);
        if (productConfigSet) {
            orderResult = this.getProducts(orderResult, order, productConfigSet);
        }
        diResult.orders.push(orderResult);
    }
    static getOrder(order, orderConfigSet) {
        let orderResult = new order_result_1.OrderResult();
        if (orderConfigSet.pageSubType) {
            orderResult.pageSubType = orderConfigSet.pageSubType;
        }
        orderConfigSet.orderLevelConfigItems.forEach(orderLevelConfigItem => {
            let manipulatedString = new manipulated_string_1.ManipulatedString("");
            if (orderLevelConfigItem.selector) {
                manipulatedString.value = json_parser_1.JSONParser.parseJson(orderLevelConfigItem.selector, order).value;
                manipulatedString = string_manipulator_1.StringManipulator.checkAndProcessStringManipulation(manipulatedString, orderLevelConfigItem);
                if (manipulatedString.error) {
                    return log_1.Log.logMessageAsIssue(manipulatedString, orderLevelConfigItem, ` ${manipulatedString.error}`);
                }
                manipulatedString = string_formatter_1.StringFormatter.checkAndProcessStringFormatters(manipulatedString, orderLevelConfigItem);
                orderResult[orderLevelConfigItem.name] = manipulatedString.value;
            }
        });
        return orderResult;
    }
    // when we have an ALL_ARRAY in the configuration
    static getALLOrdersOrProducts(selector, order) {
        let orderOrProducts;
        let allOrdersOrProductsFound = new parsed_json_1.ParsedJson();
        allOrdersOrProductsFound.value = [];
        let allLocation = selector.indexOf(this.ALL_ARRAY);
        let beforeAllSelector = selector.substring(0, allLocation);
        let afterAllSelector = selector.substring(allLocation + this.ALL_ARRAY.length + 1);
        // could be groups or shipments etc...
        let groups = json_parser_1.JSONParser.parseJson(beforeAllSelector, order);
        // More than 1 ALL_ARRAY (Currently only handles 2.. not recursive)
        if (afterAllSelector.indexOf(this.ALL_ARRAY) > -1) {
            // Process leftmost groups and flatten thouse for use below
            groups = JSONScriptParser.getOuterAllOrdersOrProducts(afterAllSelector, groups);
            log_1.Log.consoleLog('json-script-parser.getOuterAllOrdersOrProducts() groups : ', groups);
            //update afterAllSelector
            let innerAllLocation = afterAllSelector.indexOf(this.ALL_ARRAY);
            afterAllSelector = afterAllSelector.substring(innerAllLocation + this.ALL_ARRAY.length + 1);
        }
        try {
            groups.value.forEach(groupItemValue => {
                orderOrProducts = json_parser_1.JSONParser.parseJson(afterAllSelector, groupItemValue);
                if (orderOrProducts.value?.length && !orderOrProducts?.error) {
                    orderOrProducts.value.forEach(product => {
                        allOrdersOrProductsFound.value.push(product);
                    });
                }
                else if (orderOrProducts.error) {
                    allOrdersOrProductsFound.addToError(`Error in allOrdersOrProductsFound this.ALL_ARRAY/[ALL] ${orderOrProducts.error}`);
                }
            });
        }
        catch (e) {
            allOrdersOrProductsFound.addToError(`Try/Catch Exception in processing this.ALL_ARRAY/[ALL] ${e.toString()}`);
        }
        return allOrdersOrProductsFound;
    }
    // when we have 2 ALL_ARRAYs in the same selector
    static getOuterAllOrdersOrProducts(afterAllSelector, groups) {
        let outerAllLocation = afterAllSelector.indexOf(this.ALL_ARRAY);
        let outerBeforeAllSelector = afterAllSelector.substring(0, outerAllLocation);
        let outerGroups = new parsed_json_1.ParsedJson();
        outerGroups.value = [];
        groups.value.forEach(groupItemValue => {
            let outerResult = json_parser_1.JSONParser.parseJson(outerBeforeAllSelector, groupItemValue);
            if (outerResult.value && !outerResult.error) {
                outerResult.value.forEach(outerResultVal => {
                    outerGroups.value.push(outerResultVal);
                });
            }
            else {
                outerGroups.addToError(`error in getOuterAllOrdersOrProducts, nothing found with ${outerBeforeAllSelector} `);
            }
        });
        return outerGroups;
    }
    static getProducts(orderResult, order, productConfigSet) {
        let products;
        if (productConfigSet.productConfigItemRow.selector.includes(this.ALL_ARRAY)) {
            products = this.getALLOrdersOrProducts(productConfigSet.productConfigItemRow.selector, order);
        }
        else {
            // Standard workflow (not this.ALL_ARRAY/[ALL])
            products = json_parser_1.JSONParser.parseJson(productConfigSet.productConfigItemRow.selector, order);
        }
        if (products.error) {
            log_1.Log.consoleLog("Error in getProducts parseJson", products.error);
        }
        else {
            products.value.forEach(product => {
                let productResult = new product_result_1.ProductResult();
                productConfigSet.productConfigItems.forEach(productConfigItem => {
                    let manipulatedString = new manipulated_string_1.ManipulatedString("");
                    if (productConfigItem.selector) {
                        manipulatedString.value = json_parser_1.JSONParser.parseJson(productConfigItem.selector, product).value;
                        manipulatedString = string_manipulator_1.StringManipulator.checkAndProcessStringManipulation(manipulatedString, productConfigItem);
                        manipulatedString = string_formatter_1.StringFormatter.checkAndProcessStringFormatters(manipulatedString, productConfigItem);
                        if (manipulatedString.error) {
                            return log_1.Log.logMessageAsIssue(manipulatedString, productConfigItem, ` ${manipulatedString.error}`);
                        }
                        productResult[productConfigItem.name] = manipulatedString.value;
                    }
                });
                orderResult.products.push(productResult);
            });
        }
        return orderResult;
    }
    static getScript(jsonConfig) {
        let jsonContent = "";
        let scriptsFound = document.querySelectorAll(jsonConfig.scriptJsonSelector);
        if (scriptsFound.length === 0) {
            log_1.Log.consoleLog('getScript(): No matching JSON scripts found');
            return "";
        }
        log_1.Log.consoleLog('scripts found count ', scriptsFound.length);
        for (let i = 0; i < scriptsFound.length; i++) {
            jsonContent = scriptsFound[i].textContent;
            if (jsonConfig.scriptJsonPreManipulator) {
                let manipulatedStringPreManipulator = new manipulated_string_1.ManipulatedString(jsonContent);
                manipulatedStringPreManipulator = string_manipulator_1.StringManipulator.checkAndProcessJsonPreManipulation(manipulatedStringPreManipulator, jsonConfig);
                if (!manipulatedStringPreManipulator.error) {
                    jsonContent = manipulatedStringPreManipulator.value;
                }
                try {
                    //verify it's valid json, but pass back string 
                    let parsedJson = JSON.parse(jsonContent);
                    return jsonContent;
                }
                catch (ex) {
                    log_1.Log.consoleLog('Error in parsing scripts ex:', ex);
                    log_1.Log.consoleLog('Error in parsing scripts jsonContent:', jsonContent);
                }
            }
            //in case no preManipulator, return first matching script with valid JSON //TODO  BTN-2069 
            else {
                if (jsonContent !== "") {
                    try {
                        //verify it's valid json, but pass back string 
                        let parsedJson = JSON.parse(jsonContent);
                        return jsonContent;
                    }
                    catch (ex) {
                        log_1.Log.consoleLog('Error in parsing scripts (no manipulator) ex:', ex);
                    }
                }
            }
        }
        return null;
    }
}
exports.JSONScriptParser = JSONScriptParser;
// Special Configuration used to flatten arrays for 'rows' selectors
JSONScriptParser.ALL_ARRAY = "[ALL]";

},{"./json-parser":13,"./log":15,"./results/manipulated-string":21,"./results/order-result":22,"./results/parsed-json":23,"./results/product-result":24,"./string-formatter":25,"./string-manipulator":26}],15:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Log = void 0;
class Log {
    static consoleLog(str, object) {
        if (this.showDebugging) {
            if (object) {
                console.log(this.PREFIX, str, JSON.stringify(object, null, 2));
            }
            else {
                console.log(this.PREFIX, str);
            }
        }
    }
    static logMessageAsIssue(manipulatedString, configItem, msg) {
        try {
            manipulatedString.addToError(`${msg} : ${configItem.name}  : configItem selector ${configItem.selector}`);
        }
        catch (ex) {
            manipulatedString.addToError(ex);
        }
        return manipulatedString;
    }
    static logResultAsIssue(manipulatedString, orderOrDocument, productRow, configItem) {
        try {
            const name = configItem.name;
            if (!configItem.selector) {
                var skippedItem = `${name} : no selector `;
                manipulatedString.skipped = skippedItem;
            }
            else {
                let errItem = 'Error';
                let orderOrDocumentIsDocument = true;
                let selectorInOrder = null;
                if (orderOrDocument.tagName !== "HTML") {
                    orderOrDocumentIsDocument = false;
                    selectorInOrder = orderOrDocument.querySelector(configItem.selector);
                }
                let selectorInDocument = document.querySelector(configItem.selector);
                let selectorInProductRow = productRow.querySelector(configItem.selector);
                if (!selectorInDocument) {
                    errItem = `${name} : nothing found on whole document with selector : ${configItem.selector}`;
                }
                else if (!orderOrDocumentIsDocument && !selectorInOrder) {
                    errItem = `${name} : configItem selector ${configItem.selector} was found in document, but outside of order. `;
                }
                else if (!selectorInProductRow) {
                    errItem = `${name} : configItem selector ${configItem.selector} was found in document/order, but outside of product row. `;
                }
                manipulatedString.addToError(errItem);
            }
        }
        catch (ex) {
            manipulatedString.addToError(ex);
        }
        return manipulatedString;
    }
}
exports.Log = Log;
Log.showDebugging = false; //leave false normally, flip to true to see logs when debugging.
Log.PREFIX = "*DI "; //easier to filter

},{}],16:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PageSubType = void 0;
var PageSubType;
(function (PageSubType) {
    PageSubType[PageSubType["OrderHistorySummary"] = 1] = "OrderHistorySummary";
    PageSubType[PageSubType["OrderHistoryDetails"] = 2] = "OrderHistoryDetails";
    PageSubType[PageSubType["OrderHistorySummaryAndDetailsBlended"] = 3] = "OrderHistorySummaryAndDetailsBlended";
    PageSubType[PageSubType["OrderHistoryFromPostPurchase"] = 4] = "OrderHistoryFromPostPurchase";
})(PageSubType = exports.PageSubType || (exports.PageSubType = {}));

},{}],17:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PurchaseLocation = void 0;
var PurchaseLocation;
(function (PurchaseLocation) {
    PurchaseLocation[PurchaseLocation["Online"] = 1] = "Online";
    PurchaseLocation[PurchaseLocation["Instore"] = 2] = "Instore";
    PurchaseLocation[PurchaseLocation["Pickup"] = 3] = "Pickup";
})(PurchaseLocation = exports.PurchaseLocation || (exports.PurchaseLocation = {}));

},{}],18:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ScrapeMethod = void 0;
var ScrapeMethod;
(function (ScrapeMethod) {
    ScrapeMethod[ScrapeMethod["Standard"] = 1] = "Standard";
    ScrapeMethod[ScrapeMethod["DeepScrape"] = 2] = "DeepScrape";
})(ScrapeMethod = exports.ScrapeMethod || (exports.ScrapeMethod = {}));

},{}],19:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ScrapePageSource = void 0;
var ScrapePageSource;
(function (ScrapePageSource) {
    ScrapePageSource[ScrapePageSource["Html"] = 1] = "Html";
    ScrapePageSource[ScrapePageSource["JsonOnPage"] = 2] = "JsonOnPage";
    ScrapePageSource[ScrapePageSource["JsonFromApi"] = 3] = "JsonFromApi";
})(ScrapePageSource = exports.ScrapePageSource || (exports.ScrapePageSource = {}));

},{}],20:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DataInsightsResult = void 0;
class DataInsightsResult {
    constructor() {
        this.orders = [];
    }
    addToGeneralMessage(message) {
        if (!this.generalMessage) {
            this.generalMessage = message;
        }
        else {
            this.generalMessage += " - " + message;
        }
    }
}
exports.DataInsightsResult = DataInsightsResult;

},{}],21:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ManipulatedString = void 0;
// Return Object for Manipulator Methods
class ManipulatedString {
    constructor(value) {
        this.value = value;
    }
    addToError(errString) {
        if (this.error) {
            this.error += errString;
        }
        else {
            this.error = errString;
        }
    }
}
exports.ManipulatedString = ManipulatedString;

},{}],22:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderResult = void 0;
class OrderResult {
    constructor() {
        this.products = [];
    }
    addErrorItem(newError) {
        if (newError && !this.errorItems) {
            this.errorItems = [newError];
        }
        else {
            this.errorItems.push(newError);
        }
    }
    addSkippedItem(newSkip) {
        if (newSkip && !this.skippedItems) {
            this.skippedItems = [newSkip];
        }
        else {
            this.skippedItems.push(newSkip);
        }
    }
}
exports.OrderResult = OrderResult;

},{}],23:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ParsedJson = void 0;
class ParsedJson {
    addToError(errString) {
        if (this.error) {
            this.error += errString;
        }
        else {
            this.error = errString;
        }
    }
}
exports.ParsedJson = ParsedJson;

},{}],24:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProductResult = void 0;
class ProductResult {
    addErrorItem(newError) {
        if (newError && !this.errorItems) {
            this.errorItems = [newError];
        }
        else {
            this.errorItems.push(newError);
        }
    }
    addSkippedItem(newSkip) {
        if (newSkip && !this.skippedItems) {
            this.skippedItems = [newSkip];
        }
        else {
            this.skippedItems.push(newSkip);
        }
    }
}
exports.ProductResult = ProductResult;

},{}],25:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StringFormatter = void 0;
const log_1 = require("./log");
class StringFormatter {
    static checkAndProcessStringFormatters(manipulatedString, configItem, orderOrDocument, productRow) {
        if (configItem.isCurrency) {
            manipulatedString.value = this.currencyFormatter(manipulatedString.value);
            if (manipulatedString.value !== -1) {
                if (manipulatedString.value > this.priceMaxNumber) {
                    return log_1.Log.logMessageAsIssue(manipulatedString, configItem, ` Error: Price exceeded maximum of ${this.priceMaxNumber}`);
                }
            }
            else {
                if (orderOrDocument && productRow) {
                    return log_1.Log.logResultAsIssue(manipulatedString, orderOrDocument, productRow, configItem);
                }
                else {
                    return log_1.Log.logMessageAsIssue(manipulatedString, configItem, ` Error: price is -1`);
                }
            }
        }
        else if (configItem.isNumeric) {
            manipulatedString.value = this.numericFloatFormatter(manipulatedString.value);
            if (manipulatedString.value !== -1) {
                if (manipulatedString.value > this.quantityMaxNumber) {
                    return log_1.Log.logMessageAsIssue(manipulatedString, configItem, ` Error: Quantity exceeded maximum of ${this.quantityMaxNumber}`);
                }
            }
            else {
                if (orderOrDocument && productRow) {
                    return log_1.Log.logResultAsIssue(manipulatedString, orderOrDocument, productRow, configItem);
                }
                else {
                    return log_1.Log.logMessageAsIssue(manipulatedString, configItem, ` Error: quantity not found`);
                }
            }
        }
        else if (configItem.isLongNumericString) {
            if (manipulatedString.value !== -1) {
                manipulatedString.value = this.returnNumInt(manipulatedString.value);
            }
            else {
                if (orderOrDocument && productRow) {
                    return log_1.Log.logResultAsIssue(manipulatedString, orderOrDocument, productRow, configItem);
                }
                else {
                    return log_1.Log.logMessageAsIssue(manipulatedString, configItem, ` Error: upc not found`);
                }
            }
        }
        else {
            manipulatedString.value = this.generalFormatter(manipulatedString.value);
        }
        return manipulatedString;
    }
    static generalFormatter(stringToFormat) {
        // for JSON, not everything comes in as a string as of now. 
        if (!stringToFormat || typeof (stringToFormat) !== "string") {
            return stringToFormat;
        }
        // For now just removing HTML tags, but might add more functionality as when needed. 
        const stringWithOutHtmlTags = this.removeHtmlTags(stringToFormat);
        // Removing break lines here and trimming extra spaces at the beginning and end of the string. 
        const breakRegex = new RegExp('\\n|\\t', 'g');
        stringWithOutHtmlTags.replace(breakRegex, '').trim();
        return stringWithOutHtmlTags.replace(breakRegex, '').trim();
    }
    static removeHtmlTags(stringWithTags) {
        // Removing html tags if there are any in the provided string.
        if (!stringWithTags || typeof (stringWithTags) === "number") {
            return stringWithTags;
        }
        let stringWitOutTags = stringWithTags;
        try {
            stringWitOutTags = stringWithTags.replace(/(<([^>]+)>)/ig, '');
        }
        catch (ex) {
            log_1.Log.consoleLog(`Error in removeHtmlTags trying to run regex on stringWithTags :${stringWithTags} `, ex);
            return stringWithTags;
        }
        return stringWitOutTags;
    }
    // Used by CartTotal, UPC & Price (All Prices converted to ints)
    // all prices are stored in total cents without a decimal so $34.99 stored as 3499
    static returnNumInt(stringWithSymbols) {
        // Removing spaces, dot, commas to put it as a numeric string
        if (!stringWithSymbols || typeof (stringWithSymbols) === "number") {
            return stringWithSymbols;
        }
        let stringWithOutSymbols = stringWithSymbols;
        // adding try/catch to make sure empty values do not cause issues. Should be caught by three lines above.. but is not
        // Target OrderHistory (example Order[2].product[0].qty)
        try {
            stringWithOutSymbols = stringWithSymbols.replace(/\D/ig, '');
        }
        catch (ex) {
            log_1.Log.consoleLog('Error in returnNum ', ex);
            return stringWithSymbols;
        }
        return stringWithOutSymbols;
    }
    // Used by CartTotal, UPC & Price (All Prices converted to ints)
    static isNumericIntString(numericString) {
        return /^\d+$/.test(numericString);
    }
    // Quantity must be handled by floats (because of lbs etc..)
    // Used by Qty
    static returnNumFloat(stringWithSymbols) {
        // Removing spaces, dot, commas to put it as a numeric string
        if (!stringWithSymbols) {
            return stringWithSymbols;
        }
        let stringWithOutSymbols = stringWithSymbols;
        // adding try/catch to make sure empty values do not cause issues. Should be caught by theree lines above.. but is not
        // Target OrderHistory (example Order[2].product[0].qty)
        try {
            stringWithOutSymbols = stringWithSymbols.replace(/[^0-9.]/g, '');
        }
        catch (ex) {
            log_1.Log.consoleLog('Error in returnNum ', ex);
        }
        return stringWithOutSymbols;
    }
    // Used by Qty
    static isNumericFloatString(numericString) {
        return /[0-9.]/g.test(numericString);
    }
    // Used by qty
    static numericFloatFormatter(numericString) {
        const formattedString = this.removeHtmlTags(numericString);
        const formattedNumString = this.returnNumFloat(formattedString);
        if (this.isNumericFloatString(formattedNumString)) {
            return Number(formattedNumString);
        }
        else {
            return -1;
        }
    }
    static currencyFormatter(currencyString, hasCents = true) {
        const formattedString = this.removeHtmlTags(currencyString);
        let formattedCurrencyString;
        if (!formattedString) {
            return -1;
        }
        else {
            if (hasCents) {
                formattedCurrencyString = this.returnNumInt(formattedString.toString());
            }
            else {
                formattedCurrencyString = this.returnNumInt(formattedString.toString()) + '00';
            }
            if (this.isNumericIntString(formattedCurrencyString)) {
                return Number(formattedCurrencyString);
            }
            else {
                return -1;
            }
        }
    }
}
exports.StringFormatter = StringFormatter;
StringFormatter.quantityMaxNumber = 2147483000; //less than int
StringFormatter.priceMaxNumber = 2147483000; //less than int

},{"./log":15}],26:[function(require,module,exports){
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StringManipulator = void 0;
const moment_1 = __importDefault(require("moment"));
const string_formatter_1 = require("./string-formatter");
class StringManipulator {
    static checkAndProcessStringManipulation(manipulatedString, configItem) {
        if (manipulatedString.value && configItem.manipulator) {
            manipulatedString = StringManipulator.getManipulatedValue(manipulatedString, configItem.manipulator);
        }
        return manipulatedString;
    }
    static checkAndProcessJsonPreManipulation(manipulatedString, configItem) {
        if (manipulatedString.value && configItem.scriptJsonPreManipulator) {
            manipulatedString = StringManipulator.getManipulatedValue(manipulatedString, configItem.scriptJsonPreManipulator);
        }
        return manipulatedString;
    }
    static getManipulatedValue(manipulatedString, manipulatorConfigs) {
        if (!manipulatorConfigs) {
            manipulatedString.addToError(` Error: String manipulation error: no manipulator for ${manipulatedString.value}`);
            return manipulatedString;
        }
        // chained instructions 
        if (manipulatorConfigs.indexOf('::') > -1) {
            let manipulatorGroups = manipulatorConfigs.split('::');
            manipulatorGroups.forEach(individualManipulatorGroup => {
                manipulatedString = this.processInstructions(manipulatedString, individualManipulatorGroup);
            });
        }
        //single instruction 
        else {
            manipulatedString = this.processInstructions(manipulatedString, manipulatorConfigs);
        }
        return manipulatedString;
    }
    // called individually each time for chained instructions. 
    static processInstructions(manipulatedString, manipulatorConfig) {
        if (!manipulatorConfig) {
            manipulatedString.addToError(` Error: String manipulation error: no manipulator for ${manipulatedString.value}`);
            return manipulatedString;
        }
        let manipulatorSections = manipulatorConfig.split(':');
        // decode 'colon' -> ':' 
        manipulatorSections = manipulatorSections.map(item => item.replace('colon', ':'));
        if (!manipulatedString.value) {
            manipulatedString.addToError(` Error: String manipulation error: no item for ${manipulatorConfig}`);
            return manipulatedString;
        }
        // currently these are the 5 supported string manipulation instructions. 
        switch (manipulatorSections[0]) {
            case 'replace':
                manipulatedString = this.getManipulatedValueReplace(manipulatedString, manipulatorSections);
                break;
            case 'splitGetByIdentifier':
                manipulatedString = this.getManipulatedValueSplitByIdentifier(manipulatedString, manipulatorSections);
                break;
            case 'splitGetByIndex':
                manipulatedString = this.getManipulatedValueSplitByIndex(manipulatedString, manipulatorSections);
                break;
            case 'splitGetByIndexLast':
                manipulatedString = this.getManipulatedValueSplitByIndexLast(manipulatedString, manipulatorSections);
                break;
            case 'formatDate':
                manipulatedString = this.getManipulatedValueFormatDate(manipulatedString, manipulatorSections);
                break;
            case 'sale':
                manipulatedString = this.getManipulatedValueSale(manipulatedString);
                break;
            case 'trimAndRemoveLastCharacter':
                manipulatedString = this.getManipulatedValueTrimAndRemoveLastCharacter(manipulatedString);
                break;
            case 'match':
                manipulatedString = this.getManipulatedValueMatch(manipulatedString, manipulatorSections);
                break;
            case 'inferAndAddYear':
                manipulatedString = this.getManipulatedValueInferAndAddYear(manipulatedString, manipulatorSections);
                break;
            default:
                manipulatedString.error += ` Error: String manipulation error: unknown instruction : ${manipulatorSections[0]}`;
        }
        return manipulatedString;
    }
    static verifyManipulatorParameters(count, manipulatorSections) {
        if (count !== manipulatorSections.length) {
            return ` Error: String manipulation error: ${manipulatorSections[0]} Expecting different count of parameters, looking for ${count} but found ${manipulatorSections.length}`;
        }
        else {
            return "";
        }
    }
    static getManipulatedValueFormatDate(manipulatedString, manipulatorSections) {
        let formattedString = string_formatter_1.StringFormatter.generalFormatter(manipulatedString.value);
        let formattedDateString;
        let momentDate;
        if (formattedString.toLowerCase().includes('today')) {
            momentDate = moment_1.default(new Date());
            manipulatedString.value = momentDate.format("YYYY-MM-DD");
        }
        else {
            momentDate = moment_1.default(formattedString, manipulatorSections[1]);
            formattedDateString = momentDate.format("YYYY-MM-DD");
            if (formattedDateString === "Invalid date") {
                manipulatedString.addToError(` Invalid date : inputString:${manipulatedString.value} , formatter: ${manipulatorSections[1]}`);
            }
            else {
                manipulatedString.value = formattedDateString;
            }
        }
        return manipulatedString;
    }
    static getManipulatedValueInferAndAddYear(manipulatedString, manipulatorSections) {
        var parameterError = this.verifyManipulatorParameters(1, manipulatorSections);
        if (parameterError) {
            manipulatedString.error += parameterError;
            return manipulatedString;
        }
        let momentDate = moment_1.default(manipulatedString.value);
        // add one day so we don't have to think about times.. if it's today.. it's probably really today, even if in "future" 
        let currentDate = moment_1.default().add(1, 'day');
        if (currentDate < momentDate) {
            // we had no date, and Moment guessed and used the current year.. but it is in the future. 
            momentDate = momentDate.subtract(1, 'year');
            let formattedDateString = momentDate.format("YYYY-MM-DD");
            manipulatedString.value = formattedDateString;
        }
        return manipulatedString;
    }
    static getManipulatedValueReplace(manipulatedString, manipulatorSections) {
        var parameterError = this.verifyManipulatorParameters(3, manipulatorSections);
        if (parameterError) {
            manipulatedString.error += parameterError;
            return manipulatedString;
        }
        let replacee = manipulatorSections[1];
        let replacer = manipulatorSections[2];
        const regExp = new RegExp(replacee, 'g');
        const replaceWithString = replacer;
        let updatedItem = manipulatedString.value.replace(regExp, replaceWithString);
        manipulatedString.value = updatedItem;
        return manipulatedString;
    }
    static getManipulatedValueSale(manipulatedString) {
        // Here we will send the lower price if we have two prices or just send the one 
        // Filtering out only the price values, ex. "Sale $19.99 Original $29.99" is given, following regex will return "$19.99 $29.99" 
        const prices = manipulatedString.value.match(/\$\w+\.[0-9][0-9]/g);
        if (prices.length === 1) {
            manipulatedString.value = prices[0];
            return manipulatedString;
        }
        else {
            const priceValues = prices.map(price => {
                // Only getting the numeric values in the substring 
                manipulatedString.value = price.replace(/\D/ig, '');
                return manipulatedString.value;
            });
            priceValues.sort();
            prices.filter(price => {
                if (price.replace(/\D/ig, '') === priceValues[0]) {
                    manipulatedString.value = price;
                    return manipulatedString;
                }
            });
            manipulatedString.value = prices[0];
            return manipulatedString;
        }
    }
    // split and then look for a specific string, the identifier, in each of the split items and return the one that contains the identifier 
    static getManipulatedValueSplitByIdentifier(manipulatedString, manipulatorSections) {
        var parameterError = this.verifyManipulatorParameters(3, manipulatorSections);
        if (parameterError) {
            manipulatedString.error += parameterError;
            return manipulatedString;
        }
        let splitter = manipulatorSections[1];
        let identifier = manipulatorSections[2];
        if (!identifier) {
            manipulatedString.addToError(' Error: String manipulation error: splitGetByIdentifier missing identifier.');
            return manipulatedString;
        }
        const itemElements = manipulatedString.value.split(splitter);
        const itemIdentifier = identifier;
        const itemIdentifierIndex = itemElements.findIndex(element => element.includes(itemIdentifier));
        manipulatedString.value = itemElements[itemIdentifierIndex];
        return manipulatedString;
    }
    static getManipulatedValueSplitByIndex(manipulatedString, manipulatorSections) {
        var parameterError = this.verifyManipulatorParameters(3, manipulatorSections);
        if (parameterError) {
            manipulatedString.error += parameterError;
            return manipulatedString;
        }
        let splitter = manipulatorSections[1];
        let index = +manipulatorSections[2];
        if (!index && index !== 0) {
            manipulatedString.addToError(' Error: String manipulation error: splitGetByIndex missing index.');
            return manipulatedString;
        }
        const itemElements = manipulatedString.value.split(splitter);
        if (index < itemElements.length) {
            manipulatedString.value = itemElements[index];
        }
        else {
            manipulatedString.addToError(` Error: String manipulation error: index ${index} for ${manipulatedString.value} out of range`);
        }
        return manipulatedString;
    }
    static getManipulatedValueSplitByIndexLast(manipulatedString, manipulatorSections) {
        var parameterError = this.verifyManipulatorParameters(2, manipulatorSections);
        if (parameterError) {
            manipulatedString.error += parameterError;
            return manipulatedString;
        }
        let splitter = manipulatorSections[1];
        const itemElements = manipulatedString.value.split(splitter);
        if (itemElements.length) {
            manipulatedString.value = itemElements[itemElements.length - 1];
            return manipulatedString;
        }
        else {
            return manipulatedString;
        }
    }
    static getManipulatedValueTrimAndRemoveLastCharacter(manipulatedString) {
        manipulatedString.value = manipulatedString.value.trim();
        manipulatedString.value = manipulatedString.value.slice(0, -1);
        return manipulatedString;
    }
    static getManipulatedValueMatch(manipulatedString, manipulatorSections) {
        var parameterError = this.verifyManipulatorParameters(4, manipulatorSections);
        if (parameterError) {
            manipulatedString.error += parameterError;
            return manipulatedString;
        }
        let searchVal = manipulatorSections[1];
        let matchfound = manipulatorSections[2];
        let matchNotFound = manipulatorSections[3];
        let updatedItem = manipulatedString.value.indexOf(searchVal);
        if (updatedItem > -1) {
            manipulatedString.value = matchfound;
        }
        else {
            manipulatedString.value = matchNotFound;
        }
        return manipulatedString;
    }
}
exports.StringManipulator = StringManipulator;

},{"./string-formatter":25,"moment":27}],27:[function(require,module,exports){
//! moment.js
//! version : 2.30.1
//! authors : Tim Wood, Iskren Chernev, Moment.js contributors
//! license : MIT
//! momentjs.com

;(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
    typeof define === 'function' && define.amd ? define(factory) :
    global.moment = factory()
}(this, (function () { 'use strict';

    var hookCallback;

    function hooks() {
        return hookCallback.apply(null, arguments);
    }

    // This is done to register the method called with moment()
    // without creating circular dependencies.
    function setHookCallback(callback) {
        hookCallback = callback;
    }

    function isArray(input) {
        return (
            input instanceof Array ||
            Object.prototype.toString.call(input) === '[object Array]'
        );
    }

    function isObject(input) {
        // IE8 will treat undefined and null as object if it wasn't for
        // input != null
        return (
            input != null &&
            Object.prototype.toString.call(input) === '[object Object]'
        );
    }

    function hasOwnProp(a, b) {
        return Object.prototype.hasOwnProperty.call(a, b);
    }

    function isObjectEmpty(obj) {
        if (Object.getOwnPropertyNames) {
            return Object.getOwnPropertyNames(obj).length === 0;
        } else {
            var k;
            for (k in obj) {
                if (hasOwnProp(obj, k)) {
                    return false;
                }
            }
            return true;
        }
    }

    function isUndefined(input) {
        return input === void 0;
    }

    function isNumber(input) {
        return (
            typeof input === 'number' ||
            Object.prototype.toString.call(input) === '[object Number]'
        );
    }

    function isDate(input) {
        return (
            input instanceof Date ||
            Object.prototype.toString.call(input) === '[object Date]'
        );
    }

    function map(arr, fn) {
        var res = [],
            i,
            arrLen = arr.length;
        for (i = 0; i < arrLen; ++i) {
            res.push(fn(arr[i], i));
        }
        return res;
    }

    function extend(a, b) {
        for (var i in b) {
            if (hasOwnProp(b, i)) {
                a[i] = b[i];
            }
        }

        if (hasOwnProp(b, 'toString')) {
            a.toString = b.toString;
        }

        if (hasOwnProp(b, 'valueOf')) {
            a.valueOf = b.valueOf;
        }

        return a;
    }

    function createUTC(input, format, locale, strict) {
        return createLocalOrUTC(input, format, locale, strict, true).utc();
    }

    function defaultParsingFlags() {
        // We need to deep clone this object.
        return {
            empty: false,
            unusedTokens: [],
            unusedInput: [],
            overflow: -2,
            charsLeftOver: 0,
            nullInput: false,
            invalidEra: null,
            invalidMonth: null,
            invalidFormat: false,
            userInvalidated: false,
            iso: false,
            parsedDateParts: [],
            era: null,
            meridiem: null,
            rfc2822: false,
            weekdayMismatch: false,
        };
    }

    function getParsingFlags(m) {
        if (m._pf == null) {
            m._pf = defaultParsingFlags();
        }
        return m._pf;
    }

    var some;
    if (Array.prototype.some) {
        some = Array.prototype.some;
    } else {
        some = function (fun) {
            var t = Object(this),
                len = t.length >>> 0,
                i;

            for (i = 0; i < len; i++) {
                if (i in t && fun.call(this, t[i], i, t)) {
                    return true;
                }
            }

            return false;
        };
    }

    function isValid(m) {
        var flags = null,
            parsedParts = false,
            isNowValid = m._d && !isNaN(m._d.getTime());
        if (isNowValid) {
            flags = getParsingFlags(m);
            parsedParts = some.call(flags.parsedDateParts, function (i) {
                return i != null;
            });
            isNowValid =
                flags.overflow < 0 &&
                !flags.empty &&
                !flags.invalidEra &&
                !flags.invalidMonth &&
                !flags.invalidWeekday &&
                !flags.weekdayMismatch &&
                !flags.nullInput &&
                !flags.invalidFormat &&
                !flags.userInvalidated &&
                (!flags.meridiem || (flags.meridiem && parsedParts));
            if (m._strict) {
                isNowValid =
                    isNowValid &&
                    flags.charsLeftOver === 0 &&
                    flags.unusedTokens.length === 0 &&
                    flags.bigHour === undefined;
            }
        }
        if (Object.isFrozen == null || !Object.isFrozen(m)) {
            m._isValid = isNowValid;
        } else {
            return isNowValid;
        }
        return m._isValid;
    }

    function createInvalid(flags) {
        var m = createUTC(NaN);
        if (flags != null) {
            extend(getParsingFlags(m), flags);
        } else {
            getParsingFlags(m).userInvalidated = true;
        }

        return m;
    }

    // Plugins that add properties should also add the key here (null value),
    // so we can properly clone ourselves.
    var momentProperties = (hooks.momentProperties = []),
        updateInProgress = false;

    function copyConfig(to, from) {
        var i,
            prop,
            val,
            momentPropertiesLen = momentProperties.length;

        if (!isUndefined(from._isAMomentObject)) {
            to._isAMomentObject = from._isAMomentObject;
        }
        if (!isUndefined(from._i)) {
            to._i = from._i;
        }
        if (!isUndefined(from._f)) {
            to._f = from._f;
        }
        if (!isUndefined(from._l)) {
            to._l = from._l;
        }
        if (!isUndefined(from._strict)) {
            to._strict = from._strict;
        }
        if (!isUndefined(from._tzm)) {
            to._tzm = from._tzm;
        }
        if (!isUndefined(from._isUTC)) {
            to._isUTC = from._isUTC;
        }
        if (!isUndefined(from._offset)) {
            to._offset = from._offset;
        }
        if (!isUndefined(from._pf)) {
            to._pf = getParsingFlags(from);
        }
        if (!isUndefined(from._locale)) {
            to._locale = from._locale;
        }

        if (momentPropertiesLen > 0) {
            for (i = 0; i < momentPropertiesLen; i++) {
                prop = momentProperties[i];
                val = from[prop];
                if (!isUndefined(val)) {
                    to[prop] = val;
                }
            }
        }

        return to;
    }

    // Moment prototype object
    function Moment(config) {
        copyConfig(this, config);
        this._d = new Date(config._d != null ? config._d.getTime() : NaN);
        if (!this.isValid()) {
            this._d = new Date(NaN);
        }
        // Prevent infinite loop in case updateOffset creates new moment
        // objects.
        if (updateInProgress === false) {
            updateInProgress = true;
            hooks.updateOffset(this);
            updateInProgress = false;
        }
    }

    function isMoment(obj) {
        return (
            obj instanceof Moment || (obj != null && obj._isAMomentObject != null)
        );
    }

    function warn(msg) {
        if (
            hooks.suppressDeprecationWarnings === false &&
            typeof console !== 'undefined' &&
            console.warn
        ) {
            console.warn('Deprecation warning: ' + msg);
        }
    }

    function deprecate(msg, fn) {
        var firstTime = true;

        return extend(function () {
            if (hooks.deprecationHandler != null) {
                hooks.deprecationHandler(null, msg);
            }
            if (firstTime) {
                var args = [],
                    arg,
                    i,
                    key,
                    argLen = arguments.length;
                for (i = 0; i < argLen; i++) {
                    arg = '';
                    if (typeof arguments[i] === 'object') {
                        arg += '\n[' + i + '] ';
                        for (key in arguments[0]) {
                            if (hasOwnProp(arguments[0], key)) {
                                arg += key + ': ' + arguments[0][key] + ', ';
                            }
                        }
                        arg = arg.slice(0, -2); // Remove trailing comma and space
                    } else {
                        arg = arguments[i];
                    }
                    args.push(arg);
                }
                warn(
                    msg +
                        '\nArguments: ' +
                        Array.prototype.slice.call(args).join('') +
                        '\n' +
                        new Error().stack
                );
                firstTime = false;
            }
            return fn.apply(this, arguments);
        }, fn);
    }

    var deprecations = {};

    function deprecateSimple(name, msg) {
        if (hooks.deprecationHandler != null) {
            hooks.deprecationHandler(name, msg);
        }
        if (!deprecations[name]) {
            warn(msg);
            deprecations[name] = true;
        }
    }

    hooks.suppressDeprecationWarnings = false;
    hooks.deprecationHandler = null;

    function isFunction(input) {
        return (
            (typeof Function !== 'undefined' && input instanceof Function) ||
            Object.prototype.toString.call(input) === '[object Function]'
        );
    }

    function set(config) {
        var prop, i;
        for (i in config) {
            if (hasOwnProp(config, i)) {
                prop = config[i];
                if (isFunction(prop)) {
                    this[i] = prop;
                } else {
                    this['_' + i] = prop;
                }
            }
        }
        this._config = config;
        // Lenient ordinal parsing accepts just a number in addition to
        // number + (possibly) stuff coming from _dayOfMonthOrdinalParse.
        // TODO: Remove "ordinalParse" fallback in next major release.
        this._dayOfMonthOrdinalParseLenient = new RegExp(
            (this._dayOfMonthOrdinalParse.source || this._ordinalParse.source) +
                '|' +
                /\d{1,2}/.source
        );
    }

    function mergeConfigs(parentConfig, childConfig) {
        var res = extend({}, parentConfig),
            prop;
        for (prop in childConfig) {
            if (hasOwnProp(childConfig, prop)) {
                if (isObject(parentConfig[prop]) && isObject(childConfig[prop])) {
                    res[prop] = {};
                    extend(res[prop], parentConfig[prop]);
                    extend(res[prop], childConfig[prop]);
                } else if (childConfig[prop] != null) {
                    res[prop] = childConfig[prop];
                } else {
                    delete res[prop];
                }
            }
        }
        for (prop in parentConfig) {
            if (
                hasOwnProp(parentConfig, prop) &&
                !hasOwnProp(childConfig, prop) &&
                isObject(parentConfig[prop])
            ) {
                // make sure changes to properties don't modify parent config
                res[prop] = extend({}, res[prop]);
            }
        }
        return res;
    }

    function Locale(config) {
        if (config != null) {
            this.set(config);
        }
    }

    var keys;

    if (Object.keys) {
        keys = Object.keys;
    } else {
        keys = function (obj) {
            var i,
                res = [];
            for (i in obj) {
                if (hasOwnProp(obj, i)) {
                    res.push(i);
                }
            }
            return res;
        };
    }

    var defaultCalendar = {
        sameDay: '[Today at] LT',
        nextDay: '[Tomorrow at] LT',
        nextWeek: 'dddd [at] LT',
        lastDay: '[Yesterday at] LT',
        lastWeek: '[Last] dddd [at] LT',
        sameElse: 'L',
    };

    function calendar(key, mom, now) {
        var output = this._calendar[key] || this._calendar['sameElse'];
        return isFunction(output) ? output.call(mom, now) : output;
    }

    function zeroFill(number, targetLength, forceSign) {
        var absNumber = '' + Math.abs(number),
            zerosToFill = targetLength - absNumber.length,
            sign = number >= 0;
        return (
            (sign ? (forceSign ? '+' : '') : '-') +
            Math.pow(10, Math.max(0, zerosToFill)).toString().substr(1) +
            absNumber
        );
    }

    var formattingTokens =
            /(\[[^\[]*\])|(\\)?([Hh]mm(ss)?|Mo|MM?M?M?|Do|DDDo|DD?D?D?|ddd?d?|do?|w[o|w]?|W[o|W]?|Qo?|N{1,5}|YYYYYY|YYYYY|YYYY|YY|y{2,4}|yo?|gg(ggg?)?|GG(GGG?)?|e|E|a|A|hh?|HH?|kk?|mm?|ss?|S{1,9}|x|X|zz?|ZZ?|.)/g,
        localFormattingTokens = /(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g,
        formatFunctions = {},
        formatTokenFunctions = {};

    // token:    'M'
    // padded:   ['MM', 2]
    // ordinal:  'Mo'
    // callback: function () { this.month() + 1 }
    function addFormatToken(token, padded, ordinal, callback) {
        var func = callback;
        if (typeof callback === 'string') {
            func = function () {
                return this[callback]();
            };
        }
        if (token) {
            formatTokenFunctions[token] = func;
        }
        if (padded) {
            formatTokenFunctions[padded[0]] = function () {
                return zeroFill(func.apply(this, arguments), padded[1], padded[2]);
            };
        }
        if (ordinal) {
            formatTokenFunctions[ordinal] = function () {
                return this.localeData().ordinal(
                    func.apply(this, arguments),
                    token
                );
            };
        }
    }

    function removeFormattingTokens(input) {
        if (input.match(/\[[\s\S]/)) {
            return input.replace(/^\[|\]$/g, '');
        }
        return input.replace(/\\/g, '');
    }

    function makeFormatFunction(format) {
        var array = format.match(formattingTokens),
            i,
            length;

        for (i = 0, length = array.length; i < length; i++) {
            if (formatTokenFunctions[array[i]]) {
                array[i] = formatTokenFunctions[array[i]];
            } else {
                array[i] = removeFormattingTokens(array[i]);
            }
        }

        return function (mom) {
            var output = '',
                i;
            for (i = 0; i < length; i++) {
                output += isFunction(array[i])
                    ? array[i].call(mom, format)
                    : array[i];
            }
            return output;
        };
    }

    // format date using native date object
    function formatMoment(m, format) {
        if (!m.isValid()) {
            return m.localeData().invalidDate();
        }

        format = expandFormat(format, m.localeData());
        formatFunctions[format] =
            formatFunctions[format] || makeFormatFunction(format);

        return formatFunctions[format](m);
    }

    function expandFormat(format, locale) {
        var i = 5;

        function replaceLongDateFormatTokens(input) {
            return locale.longDateFormat(input) || input;
        }

        localFormattingTokens.lastIndex = 0;
        while (i >= 0 && localFormattingTokens.test(format)) {
            format = format.replace(
                localFormattingTokens,
                replaceLongDateFormatTokens
            );
            localFormattingTokens.lastIndex = 0;
            i -= 1;
        }

        return format;
    }

    var defaultLongDateFormat = {
        LTS: 'h:mm:ss A',
        LT: 'h:mm A',
        L: 'MM/DD/YYYY',
        LL: 'MMMM D, YYYY',
        LLL: 'MMMM D, YYYY h:mm A',
        LLLL: 'dddd, MMMM D, YYYY h:mm A',
    };

    function longDateFormat(key) {
        var format = this._longDateFormat[key],
            formatUpper = this._longDateFormat[key.toUpperCase()];

        if (format || !formatUpper) {
            return format;
        }

        this._longDateFormat[key] = formatUpper
            .match(formattingTokens)
            .map(function (tok) {
                if (
                    tok === 'MMMM' ||
                    tok === 'MM' ||
                    tok === 'DD' ||
                    tok === 'dddd'
                ) {
                    return tok.slice(1);
                }
                return tok;
            })
            .join('');

        return this._longDateFormat[key];
    }

    var defaultInvalidDate = 'Invalid date';

    function invalidDate() {
        return this._invalidDate;
    }

    var defaultOrdinal = '%d',
        defaultDayOfMonthOrdinalParse = /\d{1,2}/;

    function ordinal(number) {
        return this._ordinal.replace('%d', number);
    }

    var defaultRelativeTime = {
        future: 'in %s',
        past: '%s ago',
        s: 'a few seconds',
        ss: '%d seconds',
        m: 'a minute',
        mm: '%d minutes',
        h: 'an hour',
        hh: '%d hours',
        d: 'a day',
        dd: '%d days',
        w: 'a week',
        ww: '%d weeks',
        M: 'a month',
        MM: '%d months',
        y: 'a year',
        yy: '%d years',
    };

    function relativeTime(number, withoutSuffix, string, isFuture) {
        var output = this._relativeTime[string];
        return isFunction(output)
            ? output(number, withoutSuffix, string, isFuture)
            : output.replace(/%d/i, number);
    }

    function pastFuture(diff, output) {
        var format = this._relativeTime[diff > 0 ? 'future' : 'past'];
        return isFunction(format) ? format(output) : format.replace(/%s/i, output);
    }

    var aliases = {
        D: 'date',
        dates: 'date',
        date: 'date',
        d: 'day',
        days: 'day',
        day: 'day',
        e: 'weekday',
        weekdays: 'weekday',
        weekday: 'weekday',
        E: 'isoWeekday',
        isoweekdays: 'isoWeekday',
        isoweekday: 'isoWeekday',
        DDD: 'dayOfYear',
        dayofyears: 'dayOfYear',
        dayofyear: 'dayOfYear',
        h: 'hour',
        hours: 'hour',
        hour: 'hour',
        ms: 'millisecond',
        milliseconds: 'millisecond',
        millisecond: 'millisecond',
        m: 'minute',
        minutes: 'minute',
        minute: 'minute',
        M: 'month',
        months: 'month',
        month: 'month',
        Q: 'quarter',
        quarters: 'quarter',
        quarter: 'quarter',
        s: 'second',
        seconds: 'second',
        second: 'second',
        gg: 'weekYear',
        weekyears: 'weekYear',
        weekyear: 'weekYear',
        GG: 'isoWeekYear',
        isoweekyears: 'isoWeekYear',
        isoweekyear: 'isoWeekYear',
        w: 'week',
        weeks: 'week',
        week: 'week',
        W: 'isoWeek',
        isoweeks: 'isoWeek',
        isoweek: 'isoWeek',
        y: 'year',
        years: 'year',
        year: 'year',
    };

    function normalizeUnits(units) {
        return typeof units === 'string'
            ? aliases[units] || aliases[units.toLowerCase()]
            : undefined;
    }

    function normalizeObjectUnits(inputObject) {
        var normalizedInput = {},
            normalizedProp,
            prop;

        for (prop in inputObject) {
            if (hasOwnProp(inputObject, prop)) {
                normalizedProp = normalizeUnits(prop);
                if (normalizedProp) {
                    normalizedInput[normalizedProp] = inputObject[prop];
                }
            }
        }

        return normalizedInput;
    }

    var priorities = {
        date: 9,
        day: 11,
        weekday: 11,
        isoWeekday: 11,
        dayOfYear: 4,
        hour: 13,
        millisecond: 16,
        minute: 14,
        month: 8,
        quarter: 7,
        second: 15,
        weekYear: 1,
        isoWeekYear: 1,
        week: 5,
        isoWeek: 5,
        year: 1,
    };

    function getPrioritizedUnits(unitsObj) {
        var units = [],
            u;
        for (u in unitsObj) {
            if (hasOwnProp(unitsObj, u)) {
                units.push({ unit: u, priority: priorities[u] });
            }
        }
        units.sort(function (a, b) {
            return a.priority - b.priority;
        });
        return units;
    }

    var match1 = /\d/, //       0 - 9
        match2 = /\d\d/, //      00 - 99
        match3 = /\d{3}/, //     000 - 999
        match4 = /\d{4}/, //    0000 - 9999
        match6 = /[+-]?\d{6}/, // -999999 - 999999
        match1to2 = /\d\d?/, //       0 - 99
        match3to4 = /\d\d\d\d?/, //     999 - 9999
        match5to6 = /\d\d\d\d\d\d?/, //   99999 - 999999
        match1to3 = /\d{1,3}/, //       0 - 999
        match1to4 = /\d{1,4}/, //       0 - 9999
        match1to6 = /[+-]?\d{1,6}/, // -999999 - 999999
        matchUnsigned = /\d+/, //       0 - inf
        matchSigned = /[+-]?\d+/, //    -inf - inf
        matchOffset = /Z|[+-]\d\d:?\d\d/gi, // +00:00 -00:00 +0000 -0000 or Z
        matchShortOffset = /Z|[+-]\d\d(?::?\d\d)?/gi, // +00 -00 +00:00 -00:00 +0000 -0000 or Z
        matchTimestamp = /[+-]?\d+(\.\d{1,3})?/, // 123456789 123456789.123
        // any word (or two) characters or numbers including two/three word month in arabic.
        // includes scottish gaelic two word and hyphenated months
        matchWord =
            /[0-9]{0,256}['a-z\u00A0-\u05FF\u0700-\uD7FF\uF900-\uFDCF\uFDF0-\uFF07\uFF10-\uFFEF]{1,256}|[\u0600-\u06FF\/]{1,256}(\s*?[\u0600-\u06FF]{1,256}){1,2}/i,
        match1to2NoLeadingZero = /^[1-9]\d?/, //         1-99
        match1to2HasZero = /^([1-9]\d|\d)/, //           0-99
        regexes;

    regexes = {};

    function addRegexToken(token, regex, strictRegex) {
        regexes[token] = isFunction(regex)
            ? regex
            : function (isStrict, localeData) {
                  return isStrict && strictRegex ? strictRegex : regex;
              };
    }

    function getParseRegexForToken(token, config) {
        if (!hasOwnProp(regexes, token)) {
            return new RegExp(unescapeFormat(token));
        }

        return regexes[token](config._strict, config._locale);
    }

    // Code from http://stackoverflow.com/questions/3561493/is-there-a-regexp-escape-function-in-javascript
    function unescapeFormat(s) {
        return regexEscape(
            s
                .replace('\\', '')
                .replace(
                    /\\(\[)|\\(\])|\[([^\]\[]*)\]|\\(.)/g,
                    function (matched, p1, p2, p3, p4) {
                        return p1 || p2 || p3 || p4;
                    }
                )
        );
    }

    function regexEscape(s) {
        return s.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    }

    function absFloor(number) {
        if (number < 0) {
            // -0 -> 0
            return Math.ceil(number) || 0;
        } else {
            return Math.floor(number);
        }
    }

    function toInt(argumentForCoercion) {
        var coercedNumber = +argumentForCoercion,
            value = 0;

        if (coercedNumber !== 0 && isFinite(coercedNumber)) {
            value = absFloor(coercedNumber);
        }

        return value;
    }

    var tokens = {};

    function addParseToken(token, callback) {
        var i,
            func = callback,
            tokenLen;
        if (typeof token === 'string') {
            token = [token];
        }
        if (isNumber(callback)) {
            func = function (input, array) {
                array[callback] = toInt(input);
            };
        }
        tokenLen = token.length;
        for (i = 0; i < tokenLen; i++) {
            tokens[token[i]] = func;
        }
    }

    function addWeekParseToken(token, callback) {
        addParseToken(token, function (input, array, config, token) {
            config._w = config._w || {};
            callback(input, config._w, config, token);
        });
    }

    function addTimeToArrayFromToken(token, input, config) {
        if (input != null && hasOwnProp(tokens, token)) {
            tokens[token](input, config._a, config, token);
        }
    }

    function isLeapYear(year) {
        return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
    }

    var YEAR = 0,
        MONTH = 1,
        DATE = 2,
        HOUR = 3,
        MINUTE = 4,
        SECOND = 5,
        MILLISECOND = 6,
        WEEK = 7,
        WEEKDAY = 8;

    // FORMATTING

    addFormatToken('Y', 0, 0, function () {
        var y = this.year();
        return y <= 9999 ? zeroFill(y, 4) : '+' + y;
    });

    addFormatToken(0, ['YY', 2], 0, function () {
        return this.year() % 100;
    });

    addFormatToken(0, ['YYYY', 4], 0, 'year');
    addFormatToken(0, ['YYYYY', 5], 0, 'year');
    addFormatToken(0, ['YYYYYY', 6, true], 0, 'year');

    // PARSING

    addRegexToken('Y', matchSigned);
    addRegexToken('YY', match1to2, match2);
    addRegexToken('YYYY', match1to4, match4);
    addRegexToken('YYYYY', match1to6, match6);
    addRegexToken('YYYYYY', match1to6, match6);

    addParseToken(['YYYYY', 'YYYYYY'], YEAR);
    addParseToken('YYYY', function (input, array) {
        array[YEAR] =
            input.length === 2 ? hooks.parseTwoDigitYear(input) : toInt(input);
    });
    addParseToken('YY', function (input, array) {
        array[YEAR] = hooks.parseTwoDigitYear(input);
    });
    addParseToken('Y', function (input, array) {
        array[YEAR] = parseInt(input, 10);
    });

    // HELPERS

    function daysInYear(year) {
        return isLeapYear(year) ? 366 : 365;
    }

    // HOOKS

    hooks.parseTwoDigitYear = function (input) {
        return toInt(input) + (toInt(input) > 68 ? 1900 : 2000);
    };

    // MOMENTS

    var getSetYear = makeGetSet('FullYear', true);

    function getIsLeapYear() {
        return isLeapYear(this.year());
    }

    function makeGetSet(unit, keepTime) {
        return function (value) {
            if (value != null) {
                set$1(this, unit, value);
                hooks.updateOffset(this, keepTime);
                return this;
            } else {
                return get(this, unit);
            }
        };
    }

    function get(mom, unit) {
        if (!mom.isValid()) {
            return NaN;
        }

        var d = mom._d,
            isUTC = mom._isUTC;

        switch (unit) {
            case 'Milliseconds':
                return isUTC ? d.getUTCMilliseconds() : d.getMilliseconds();
            case 'Seconds':
                return isUTC ? d.getUTCSeconds() : d.getSeconds();
            case 'Minutes':
                return isUTC ? d.getUTCMinutes() : d.getMinutes();
            case 'Hours':
                return isUTC ? d.getUTCHours() : d.getHours();
            case 'Date':
                return isUTC ? d.getUTCDate() : d.getDate();
            case 'Day':
                return isUTC ? d.getUTCDay() : d.getDay();
            case 'Month':
                return isUTC ? d.getUTCMonth() : d.getMonth();
            case 'FullYear':
                return isUTC ? d.getUTCFullYear() : d.getFullYear();
            default:
                return NaN; // Just in case
        }
    }

    function set$1(mom, unit, value) {
        var d, isUTC, year, month, date;

        if (!mom.isValid() || isNaN(value)) {
            return;
        }

        d = mom._d;
        isUTC = mom._isUTC;

        switch (unit) {
            case 'Milliseconds':
                return void (isUTC
                    ? d.setUTCMilliseconds(value)
                    : d.setMilliseconds(value));
            case 'Seconds':
                return void (isUTC ? d.setUTCSeconds(value) : d.setSeconds(value));
            case 'Minutes':
                return void (isUTC ? d.setUTCMinutes(value) : d.setMinutes(value));
            case 'Hours':
                return void (isUTC ? d.setUTCHours(value) : d.setHours(value));
            case 'Date':
                return void (isUTC ? d.setUTCDate(value) : d.setDate(value));
            // case 'Day': // Not real
            //    return void (isUTC ? d.setUTCDay(value) : d.setDay(value));
            // case 'Month': // Not used because we need to pass two variables
            //     return void (isUTC ? d.setUTCMonth(value) : d.setMonth(value));
            case 'FullYear':
                break; // See below ...
            default:
                return; // Just in case
        }

        year = value;
        month = mom.month();
        date = mom.date();
        date = date === 29 && month === 1 && !isLeapYear(year) ? 28 : date;
        void (isUTC
            ? d.setUTCFullYear(year, month, date)
            : d.setFullYear(year, month, date));
    }

    // MOMENTS

    function stringGet(units) {
        units = normalizeUnits(units);
        if (isFunction(this[units])) {
            return this[units]();
        }
        return this;
    }

    function stringSet(units, value) {
        if (typeof units === 'object') {
            units = normalizeObjectUnits(units);
            var prioritized = getPrioritizedUnits(units),
                i,
                prioritizedLen = prioritized.length;
            for (i = 0; i < prioritizedLen; i++) {
                this[prioritized[i].unit](units[prioritized[i].unit]);
            }
        } else {
            units = normalizeUnits(units);
            if (isFunction(this[units])) {
                return this[units](value);
            }
        }
        return this;
    }

    function mod(n, x) {
        return ((n % x) + x) % x;
    }

    var indexOf;

    if (Array.prototype.indexOf) {
        indexOf = Array.prototype.indexOf;
    } else {
        indexOf = function (o) {
            // I know
            var i;
            for (i = 0; i < this.length; ++i) {
                if (this[i] === o) {
                    return i;
                }
            }
            return -1;
        };
    }

    function daysInMonth(year, month) {
        if (isNaN(year) || isNaN(month)) {
            return NaN;
        }
        var modMonth = mod(month, 12);
        year += (month - modMonth) / 12;
        return modMonth === 1
            ? isLeapYear(year)
                ? 29
                : 28
            : 31 - ((modMonth % 7) % 2);
    }

    // FORMATTING

    addFormatToken('M', ['MM', 2], 'Mo', function () {
        return this.month() + 1;
    });

    addFormatToken('MMM', 0, 0, function (format) {
        return this.localeData().monthsShort(this, format);
    });

    addFormatToken('MMMM', 0, 0, function (format) {
        return this.localeData().months(this, format);
    });

    // PARSING

    addRegexToken('M', match1to2, match1to2NoLeadingZero);
    addRegexToken('MM', match1to2, match2);
    addRegexToken('MMM', function (isStrict, locale) {
        return locale.monthsShortRegex(isStrict);
    });
    addRegexToken('MMMM', function (isStrict, locale) {
        return locale.monthsRegex(isStrict);
    });

    addParseToken(['M', 'MM'], function (input, array) {
        array[MONTH] = toInt(input) - 1;
    });

    addParseToken(['MMM', 'MMMM'], function (input, array, config, token) {
        var month = config._locale.monthsParse(input, token, config._strict);
        // if we didn't find a month name, mark the date as invalid.
        if (month != null) {
            array[MONTH] = month;
        } else {
            getParsingFlags(config).invalidMonth = input;
        }
    });

    // LOCALES

    var defaultLocaleMonths =
            'January_February_March_April_May_June_July_August_September_October_November_December'.split(
                '_'
            ),
        defaultLocaleMonthsShort =
            'Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec'.split('_'),
        MONTHS_IN_FORMAT = /D[oD]?(\[[^\[\]]*\]|\s)+MMMM?/,
        defaultMonthsShortRegex = matchWord,
        defaultMonthsRegex = matchWord;

    function localeMonths(m, format) {
        if (!m) {
            return isArray(this._months)
                ? this._months
                : this._months['standalone'];
        }
        return isArray(this._months)
            ? this._months[m.month()]
            : this._months[
                  (this._months.isFormat || MONTHS_IN_FORMAT).test(format)
                      ? 'format'
                      : 'standalone'
              ][m.month()];
    }

    function localeMonthsShort(m, format) {
        if (!m) {
            return isArray(this._monthsShort)
                ? this._monthsShort
                : this._monthsShort['standalone'];
        }
        return isArray(this._monthsShort)
            ? this._monthsShort[m.month()]
            : this._monthsShort[
                  MONTHS_IN_FORMAT.test(format) ? 'format' : 'standalone'
              ][m.month()];
    }

    function handleStrictParse(monthName, format, strict) {
        var i,
            ii,
            mom,
            llc = monthName.toLocaleLowerCase();
        if (!this._monthsParse) {
            // this is not used
            this._monthsParse = [];
            this._longMonthsParse = [];
            this._shortMonthsParse = [];
            for (i = 0; i < 12; ++i) {
                mom = createUTC([2000, i]);
                this._shortMonthsParse[i] = this.monthsShort(
                    mom,
                    ''
                ).toLocaleLowerCase();
                this._longMonthsParse[i] = this.months(mom, '').toLocaleLowerCase();
            }
        }

        if (strict) {
            if (format === 'MMM') {
                ii = indexOf.call(this._shortMonthsParse, llc);
                return ii !== -1 ? ii : null;
            } else {
                ii = indexOf.call(this._longMonthsParse, llc);
                return ii !== -1 ? ii : null;
            }
        } else {
            if (format === 'MMM') {
                ii = indexOf.call(this._shortMonthsParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._longMonthsParse, llc);
                return ii !== -1 ? ii : null;
            } else {
                ii = indexOf.call(this._longMonthsParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._shortMonthsParse, llc);
                return ii !== -1 ? ii : null;
            }
        }
    }

    function localeMonthsParse(monthName, format, strict) {
        var i, mom, regex;

        if (this._monthsParseExact) {
            return handleStrictParse.call(this, monthName, format, strict);
        }

        if (!this._monthsParse) {
            this._monthsParse = [];
            this._longMonthsParse = [];
            this._shortMonthsParse = [];
        }

        // TODO: add sorting
        // Sorting makes sure if one month (or abbr) is a prefix of another
        // see sorting in computeMonthsParse
        for (i = 0; i < 12; i++) {
            // make the regex if we don't have it already
            mom = createUTC([2000, i]);
            if (strict && !this._longMonthsParse[i]) {
                this._longMonthsParse[i] = new RegExp(
                    '^' + this.months(mom, '').replace('.', '') + '$',
                    'i'
                );
                this._shortMonthsParse[i] = new RegExp(
                    '^' + this.monthsShort(mom, '').replace('.', '') + '$',
                    'i'
                );
            }
            if (!strict && !this._monthsParse[i]) {
                regex =
                    '^' + this.months(mom, '') + '|^' + this.monthsShort(mom, '');
                this._monthsParse[i] = new RegExp(regex.replace('.', ''), 'i');
            }
            // test the regex
            if (
                strict &&
                format === 'MMMM' &&
                this._longMonthsParse[i].test(monthName)
            ) {
                return i;
            } else if (
                strict &&
                format === 'MMM' &&
                this._shortMonthsParse[i].test(monthName)
            ) {
                return i;
            } else if (!strict && this._monthsParse[i].test(monthName)) {
                return i;
            }
        }
    }

    // MOMENTS

    function setMonth(mom, value) {
        if (!mom.isValid()) {
            // No op
            return mom;
        }

        if (typeof value === 'string') {
            if (/^\d+$/.test(value)) {
                value = toInt(value);
            } else {
                value = mom.localeData().monthsParse(value);
                // TODO: Another silent failure?
                if (!isNumber(value)) {
                    return mom;
                }
            }
        }

        var month = value,
            date = mom.date();

        date = date < 29 ? date : Math.min(date, daysInMonth(mom.year(), month));
        void (mom._isUTC
            ? mom._d.setUTCMonth(month, date)
            : mom._d.setMonth(month, date));
        return mom;
    }

    function getSetMonth(value) {
        if (value != null) {
            setMonth(this, value);
            hooks.updateOffset(this, true);
            return this;
        } else {
            return get(this, 'Month');
        }
    }

    function getDaysInMonth() {
        return daysInMonth(this.year(), this.month());
    }

    function monthsShortRegex(isStrict) {
        if (this._monthsParseExact) {
            if (!hasOwnProp(this, '_monthsRegex')) {
                computeMonthsParse.call(this);
            }
            if (isStrict) {
                return this._monthsShortStrictRegex;
            } else {
                return this._monthsShortRegex;
            }
        } else {
            if (!hasOwnProp(this, '_monthsShortRegex')) {
                this._monthsShortRegex = defaultMonthsShortRegex;
            }
            return this._monthsShortStrictRegex && isStrict
                ? this._monthsShortStrictRegex
                : this._monthsShortRegex;
        }
    }

    function monthsRegex(isStrict) {
        if (this._monthsParseExact) {
            if (!hasOwnProp(this, '_monthsRegex')) {
                computeMonthsParse.call(this);
            }
            if (isStrict) {
                return this._monthsStrictRegex;
            } else {
                return this._monthsRegex;
            }
        } else {
            if (!hasOwnProp(this, '_monthsRegex')) {
                this._monthsRegex = defaultMonthsRegex;
            }
            return this._monthsStrictRegex && isStrict
                ? this._monthsStrictRegex
                : this._monthsRegex;
        }
    }

    function computeMonthsParse() {
        function cmpLenRev(a, b) {
            return b.length - a.length;
        }

        var shortPieces = [],
            longPieces = [],
            mixedPieces = [],
            i,
            mom,
            shortP,
            longP;
        for (i = 0; i < 12; i++) {
            // make the regex if we don't have it already
            mom = createUTC([2000, i]);
            shortP = regexEscape(this.monthsShort(mom, ''));
            longP = regexEscape(this.months(mom, ''));
            shortPieces.push(shortP);
            longPieces.push(longP);
            mixedPieces.push(longP);
            mixedPieces.push(shortP);
        }
        // Sorting makes sure if one month (or abbr) is a prefix of another it
        // will match the longer piece.
        shortPieces.sort(cmpLenRev);
        longPieces.sort(cmpLenRev);
        mixedPieces.sort(cmpLenRev);

        this._monthsRegex = new RegExp('^(' + mixedPieces.join('|') + ')', 'i');
        this._monthsShortRegex = this._monthsRegex;
        this._monthsStrictRegex = new RegExp(
            '^(' + longPieces.join('|') + ')',
            'i'
        );
        this._monthsShortStrictRegex = new RegExp(
            '^(' + shortPieces.join('|') + ')',
            'i'
        );
    }

    function createDate(y, m, d, h, M, s, ms) {
        // can't just apply() to create a date:
        // https://stackoverflow.com/q/181348
        var date;
        // the date constructor remaps years 0-99 to 1900-1999
        if (y < 100 && y >= 0) {
            // preserve leap years using a full 400 year cycle, then reset
            date = new Date(y + 400, m, d, h, M, s, ms);
            if (isFinite(date.getFullYear())) {
                date.setFullYear(y);
            }
        } else {
            date = new Date(y, m, d, h, M, s, ms);
        }

        return date;
    }

    function createUTCDate(y) {
        var date, args;
        // the Date.UTC function remaps years 0-99 to 1900-1999
        if (y < 100 && y >= 0) {
            args = Array.prototype.slice.call(arguments);
            // preserve leap years using a full 400 year cycle, then reset
            args[0] = y + 400;
            date = new Date(Date.UTC.apply(null, args));
            if (isFinite(date.getUTCFullYear())) {
                date.setUTCFullYear(y);
            }
        } else {
            date = new Date(Date.UTC.apply(null, arguments));
        }

        return date;
    }

    // start-of-first-week - start-of-year
    function firstWeekOffset(year, dow, doy) {
        var // first-week day -- which january is always in the first week (4 for iso, 1 for other)
            fwd = 7 + dow - doy,
            // first-week day local weekday -- which local weekday is fwd
            fwdlw = (7 + createUTCDate(year, 0, fwd).getUTCDay() - dow) % 7;

        return -fwdlw + fwd - 1;
    }

    // https://en.wikipedia.org/wiki/ISO_week_date#Calculating_a_date_given_the_year.2C_week_number_and_weekday
    function dayOfYearFromWeeks(year, week, weekday, dow, doy) {
        var localWeekday = (7 + weekday - dow) % 7,
            weekOffset = firstWeekOffset(year, dow, doy),
            dayOfYear = 1 + 7 * (week - 1) + localWeekday + weekOffset,
            resYear,
            resDayOfYear;

        if (dayOfYear <= 0) {
            resYear = year - 1;
            resDayOfYear = daysInYear(resYear) + dayOfYear;
        } else if (dayOfYear > daysInYear(year)) {
            resYear = year + 1;
            resDayOfYear = dayOfYear - daysInYear(year);
        } else {
            resYear = year;
            resDayOfYear = dayOfYear;
        }

        return {
            year: resYear,
            dayOfYear: resDayOfYear,
        };
    }

    function weekOfYear(mom, dow, doy) {
        var weekOffset = firstWeekOffset(mom.year(), dow, doy),
            week = Math.floor((mom.dayOfYear() - weekOffset - 1) / 7) + 1,
            resWeek,
            resYear;

        if (week < 1) {
            resYear = mom.year() - 1;
            resWeek = week + weeksInYear(resYear, dow, doy);
        } else if (week > weeksInYear(mom.year(), dow, doy)) {
            resWeek = week - weeksInYear(mom.year(), dow, doy);
            resYear = mom.year() + 1;
        } else {
            resYear = mom.year();
            resWeek = week;
        }

        return {
            week: resWeek,
            year: resYear,
        };
    }

    function weeksInYear(year, dow, doy) {
        var weekOffset = firstWeekOffset(year, dow, doy),
            weekOffsetNext = firstWeekOffset(year + 1, dow, doy);
        return (daysInYear(year) - weekOffset + weekOffsetNext) / 7;
    }

    // FORMATTING

    addFormatToken('w', ['ww', 2], 'wo', 'week');
    addFormatToken('W', ['WW', 2], 'Wo', 'isoWeek');

    // PARSING

    addRegexToken('w', match1to2, match1to2NoLeadingZero);
    addRegexToken('ww', match1to2, match2);
    addRegexToken('W', match1to2, match1to2NoLeadingZero);
    addRegexToken('WW', match1to2, match2);

    addWeekParseToken(
        ['w', 'ww', 'W', 'WW'],
        function (input, week, config, token) {
            week[token.substr(0, 1)] = toInt(input);
        }
    );

    // HELPERS

    // LOCALES

    function localeWeek(mom) {
        return weekOfYear(mom, this._week.dow, this._week.doy).week;
    }

    var defaultLocaleWeek = {
        dow: 0, // Sunday is the first day of the week.
        doy: 6, // The week that contains Jan 6th is the first week of the year.
    };

    function localeFirstDayOfWeek() {
        return this._week.dow;
    }

    function localeFirstDayOfYear() {
        return this._week.doy;
    }

    // MOMENTS

    function getSetWeek(input) {
        var week = this.localeData().week(this);
        return input == null ? week : this.add((input - week) * 7, 'd');
    }

    function getSetISOWeek(input) {
        var week = weekOfYear(this, 1, 4).week;
        return input == null ? week : this.add((input - week) * 7, 'd');
    }

    // FORMATTING

    addFormatToken('d', 0, 'do', 'day');

    addFormatToken('dd', 0, 0, function (format) {
        return this.localeData().weekdaysMin(this, format);
    });

    addFormatToken('ddd', 0, 0, function (format) {
        return this.localeData().weekdaysShort(this, format);
    });

    addFormatToken('dddd', 0, 0, function (format) {
        return this.localeData().weekdays(this, format);
    });

    addFormatToken('e', 0, 0, 'weekday');
    addFormatToken('E', 0, 0, 'isoWeekday');

    // PARSING

    addRegexToken('d', match1to2);
    addRegexToken('e', match1to2);
    addRegexToken('E', match1to2);
    addRegexToken('dd', function (isStrict, locale) {
        return locale.weekdaysMinRegex(isStrict);
    });
    addRegexToken('ddd', function (isStrict, locale) {
        return locale.weekdaysShortRegex(isStrict);
    });
    addRegexToken('dddd', function (isStrict, locale) {
        return locale.weekdaysRegex(isStrict);
    });

    addWeekParseToken(['dd', 'ddd', 'dddd'], function (input, week, config, token) {
        var weekday = config._locale.weekdaysParse(input, token, config._strict);
        // if we didn't get a weekday name, mark the date as invalid
        if (weekday != null) {
            week.d = weekday;
        } else {
            getParsingFlags(config).invalidWeekday = input;
        }
    });

    addWeekParseToken(['d', 'e', 'E'], function (input, week, config, token) {
        week[token] = toInt(input);
    });

    // HELPERS

    function parseWeekday(input, locale) {
        if (typeof input !== 'string') {
            return input;
        }

        if (!isNaN(input)) {
            return parseInt(input, 10);
        }

        input = locale.weekdaysParse(input);
        if (typeof input === 'number') {
            return input;
        }

        return null;
    }

    function parseIsoWeekday(input, locale) {
        if (typeof input === 'string') {
            return locale.weekdaysParse(input) % 7 || 7;
        }
        return isNaN(input) ? null : input;
    }

    // LOCALES
    function shiftWeekdays(ws, n) {
        return ws.slice(n, 7).concat(ws.slice(0, n));
    }

    var defaultLocaleWeekdays =
            'Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday'.split('_'),
        defaultLocaleWeekdaysShort = 'Sun_Mon_Tue_Wed_Thu_Fri_Sat'.split('_'),
        defaultLocaleWeekdaysMin = 'Su_Mo_Tu_We_Th_Fr_Sa'.split('_'),
        defaultWeekdaysRegex = matchWord,
        defaultWeekdaysShortRegex = matchWord,
        defaultWeekdaysMinRegex = matchWord;

    function localeWeekdays(m, format) {
        var weekdays = isArray(this._weekdays)
            ? this._weekdays
            : this._weekdays[
                  m && m !== true && this._weekdays.isFormat.test(format)
                      ? 'format'
                      : 'standalone'
              ];
        return m === true
            ? shiftWeekdays(weekdays, this._week.dow)
            : m
              ? weekdays[m.day()]
              : weekdays;
    }

    function localeWeekdaysShort(m) {
        return m === true
            ? shiftWeekdays(this._weekdaysShort, this._week.dow)
            : m
              ? this._weekdaysShort[m.day()]
              : this._weekdaysShort;
    }

    function localeWeekdaysMin(m) {
        return m === true
            ? shiftWeekdays(this._weekdaysMin, this._week.dow)
            : m
              ? this._weekdaysMin[m.day()]
              : this._weekdaysMin;
    }

    function handleStrictParse$1(weekdayName, format, strict) {
        var i,
            ii,
            mom,
            llc = weekdayName.toLocaleLowerCase();
        if (!this._weekdaysParse) {
            this._weekdaysParse = [];
            this._shortWeekdaysParse = [];
            this._minWeekdaysParse = [];

            for (i = 0; i < 7; ++i) {
                mom = createUTC([2000, 1]).day(i);
                this._minWeekdaysParse[i] = this.weekdaysMin(
                    mom,
                    ''
                ).toLocaleLowerCase();
                this._shortWeekdaysParse[i] = this.weekdaysShort(
                    mom,
                    ''
                ).toLocaleLowerCase();
                this._weekdaysParse[i] = this.weekdays(mom, '').toLocaleLowerCase();
            }
        }

        if (strict) {
            if (format === 'dddd') {
                ii = indexOf.call(this._weekdaysParse, llc);
                return ii !== -1 ? ii : null;
            } else if (format === 'ddd') {
                ii = indexOf.call(this._shortWeekdaysParse, llc);
                return ii !== -1 ? ii : null;
            } else {
                ii = indexOf.call(this._minWeekdaysParse, llc);
                return ii !== -1 ? ii : null;
            }
        } else {
            if (format === 'dddd') {
                ii = indexOf.call(this._weekdaysParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._shortWeekdaysParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._minWeekdaysParse, llc);
                return ii !== -1 ? ii : null;
            } else if (format === 'ddd') {
                ii = indexOf.call(this._shortWeekdaysParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._weekdaysParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._minWeekdaysParse, llc);
                return ii !== -1 ? ii : null;
            } else {
                ii = indexOf.call(this._minWeekdaysParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._weekdaysParse, llc);
                if (ii !== -1) {
                    return ii;
                }
                ii = indexOf.call(this._shortWeekdaysParse, llc);
                return ii !== -1 ? ii : null;
            }
        }
    }

    function localeWeekdaysParse(weekdayName, format, strict) {
        var i, mom, regex;

        if (this._weekdaysParseExact) {
            return handleStrictParse$1.call(this, weekdayName, format, strict);
        }

        if (!this._weekdaysParse) {
            this._weekdaysParse = [];
            this._minWeekdaysParse = [];
            this._shortWeekdaysParse = [];
            this._fullWeekdaysParse = [];
        }

        for (i = 0; i < 7; i++) {
            // make the regex if we don't have it already

            mom = createUTC([2000, 1]).day(i);
            if (strict && !this._fullWeekdaysParse[i]) {
                this._fullWeekdaysParse[i] = new RegExp(
                    '^' + this.weekdays(mom, '').replace('.', '\\.?') + '$',
                    'i'
                );
                this._shortWeekdaysParse[i] = new RegExp(
                    '^' + this.weekdaysShort(mom, '').replace('.', '\\.?') + '$',
                    'i'
                );
                this._minWeekdaysParse[i] = new RegExp(
                    '^' + this.weekdaysMin(mom, '').replace('.', '\\.?') + '$',
                    'i'
                );
            }
            if (!this._weekdaysParse[i]) {
                regex =
                    '^' +
                    this.weekdays(mom, '') +
                    '|^' +
                    this.weekdaysShort(mom, '') +
                    '|^' +
                    this.weekdaysMin(mom, '');
                this._weekdaysParse[i] = new RegExp(regex.replace('.', ''), 'i');
            }
            // test the regex
            if (
                strict &&
                format === 'dddd' &&
                this._fullWeekdaysParse[i].test(weekdayName)
            ) {
                return i;
            } else if (
                strict &&
                format === 'ddd' &&
                this._shortWeekdaysParse[i].test(weekdayName)
            ) {
                return i;
            } else if (
                strict &&
                format === 'dd' &&
                this._minWeekdaysParse[i].test(weekdayName)
            ) {
                return i;
            } else if (!strict && this._weekdaysParse[i].test(weekdayName)) {
                return i;
            }
        }
    }

    // MOMENTS

    function getSetDayOfWeek(input) {
        if (!this.isValid()) {
            return input != null ? this : NaN;
        }

        var day = get(this, 'Day');
        if (input != null) {
            input = parseWeekday(input, this.localeData());
            return this.add(input - day, 'd');
        } else {
            return day;
        }
    }

    function getSetLocaleDayOfWeek(input) {
        if (!this.isValid()) {
            return input != null ? this : NaN;
        }
        var weekday = (this.day() + 7 - this.localeData()._week.dow) % 7;
        return input == null ? weekday : this.add(input - weekday, 'd');
    }

    function getSetISODayOfWeek(input) {
        if (!this.isValid()) {
            return input != null ? this : NaN;
        }

        // behaves the same as moment#day except
        // as a getter, returns 7 instead of 0 (1-7 range instead of 0-6)
        // as a setter, sunday should belong to the previous week.

        if (input != null) {
            var weekday = parseIsoWeekday(input, this.localeData());
            return this.day(this.day() % 7 ? weekday : weekday - 7);
        } else {
            return this.day() || 7;
        }
    }

    function weekdaysRegex(isStrict) {
        if (this._weekdaysParseExact) {
            if (!hasOwnProp(this, '_weekdaysRegex')) {
                computeWeekdaysParse.call(this);
            }
            if (isStrict) {
                return this._weekdaysStrictRegex;
            } else {
                return this._weekdaysRegex;
            }
        } else {
            if (!hasOwnProp(this, '_weekdaysRegex')) {
                this._weekdaysRegex = defaultWeekdaysRegex;
            }
            return this._weekdaysStrictRegex && isStrict
                ? this._weekdaysStrictRegex
                : this._weekdaysRegex;
        }
    }

    function weekdaysShortRegex(isStrict) {
        if (this._weekdaysParseExact) {
            if (!hasOwnProp(this, '_weekdaysRegex')) {
                computeWeekdaysParse.call(this);
            }
            if (isStrict) {
                return this._weekdaysShortStrictRegex;
            } else {
                return this._weekdaysShortRegex;
            }
        } else {
            if (!hasOwnProp(this, '_weekdaysShortRegex')) {
                this._weekdaysShortRegex = defaultWeekdaysShortRegex;
            }
            return this._weekdaysShortStrictRegex && isStrict
                ? this._weekdaysShortStrictRegex
                : this._weekdaysShortRegex;
        }
    }

    function weekdaysMinRegex(isStrict) {
        if (this._weekdaysParseExact) {
            if (!hasOwnProp(this, '_weekdaysRegex')) {
                computeWeekdaysParse.call(this);
            }
            if (isStrict) {
                return this._weekdaysMinStrictRegex;
            } else {
                return this._weekdaysMinRegex;
            }
        } else {
            if (!hasOwnProp(this, '_weekdaysMinRegex')) {
                this._weekdaysMinRegex = defaultWeekdaysMinRegex;
            }
            return this._weekdaysMinStrictRegex && isStrict
                ? this._weekdaysMinStrictRegex
                : this._weekdaysMinRegex;
        }
    }

    function computeWeekdaysParse() {
        function cmpLenRev(a, b) {
            return b.length - a.length;
        }

        var minPieces = [],
            shortPieces = [],
            longPieces = [],
            mixedPieces = [],
            i,
            mom,
            minp,
            shortp,
            longp;
        for (i = 0; i < 7; i++) {
            // make the regex if we don't have it already
            mom = createUTC([2000, 1]).day(i);
            minp = regexEscape(this.weekdaysMin(mom, ''));
            shortp = regexEscape(this.weekdaysShort(mom, ''));
            longp = regexEscape(this.weekdays(mom, ''));
            minPieces.push(minp);
            shortPieces.push(shortp);
            longPieces.push(longp);
            mixedPieces.push(minp);
            mixedPieces.push(shortp);
            mixedPieces.push(longp);
        }
        // Sorting makes sure if one weekday (or abbr) is a prefix of another it
        // will match the longer piece.
        minPieces.sort(cmpLenRev);
        shortPieces.sort(cmpLenRev);
        longPieces.sort(cmpLenRev);
        mixedPieces.sort(cmpLenRev);

        this._weekdaysRegex = new RegExp('^(' + mixedPieces.join('|') + ')', 'i');
        this._weekdaysShortRegex = this._weekdaysRegex;
        this._weekdaysMinRegex = this._weekdaysRegex;

        this._weekdaysStrictRegex = new RegExp(
            '^(' + longPieces.join('|') + ')',
            'i'
        );
        this._weekdaysShortStrictRegex = new RegExp(
            '^(' + shortPieces.join('|') + ')',
            'i'
        );
        this._weekdaysMinStrictRegex = new RegExp(
            '^(' + minPieces.join('|') + ')',
            'i'
        );
    }

    // FORMATTING

    function hFormat() {
        return this.hours() % 12 || 12;
    }

    function kFormat() {
        return this.hours() || 24;
    }

    addFormatToken('H', ['HH', 2], 0, 'hour');
    addFormatToken('h', ['hh', 2], 0, hFormat);
    addFormatToken('k', ['kk', 2], 0, kFormat);

    addFormatToken('hmm', 0, 0, function () {
        return '' + hFormat.apply(this) + zeroFill(this.minutes(), 2);
    });

    addFormatToken('hmmss', 0, 0, function () {
        return (
            '' +
            hFormat.apply(this) +
            zeroFill(this.minutes(), 2) +
            zeroFill(this.seconds(), 2)
        );
    });

    addFormatToken('Hmm', 0, 0, function () {
        return '' + this.hours() + zeroFill(this.minutes(), 2);
    });

    addFormatToken('Hmmss', 0, 0, function () {
        return (
            '' +
            this.hours() +
            zeroFill(this.minutes(), 2) +
            zeroFill(this.seconds(), 2)
        );
    });

    function meridiem(token, lowercase) {
        addFormatToken(token, 0, 0, function () {
            return this.localeData().meridiem(
                this.hours(),
                this.minutes(),
                lowercase
            );
        });
    }

    meridiem('a', true);
    meridiem('A', false);

    // PARSING

    function matchMeridiem(isStrict, locale) {
        return locale._meridiemParse;
    }

    addRegexToken('a', matchMeridiem);
    addRegexToken('A', matchMeridiem);
    addRegexToken('H', match1to2, match1to2HasZero);
    addRegexToken('h', match1to2, match1to2NoLeadingZero);
    addRegexToken('k', match1to2, match1to2NoLeadingZero);
    addRegexToken('HH', match1to2, match2);
    addRegexToken('hh', match1to2, match2);
    addRegexToken('kk', match1to2, match2);

    addRegexToken('hmm', match3to4);
    addRegexToken('hmmss', match5to6);
    addRegexToken('Hmm', match3to4);
    addRegexToken('Hmmss', match5to6);

    addParseToken(['H', 'HH'], HOUR);
    addParseToken(['k', 'kk'], function (input, array, config) {
        var kInput = toInt(input);
        array[HOUR] = kInput === 24 ? 0 : kInput;
    });
    addParseToken(['a', 'A'], function (input, array, config) {
        config._isPm = config._locale.isPM(input);
        config._meridiem = input;
    });
    addParseToken(['h', 'hh'], function (input, array, config) {
        array[HOUR] = toInt(input);
        getParsingFlags(config).bigHour = true;
    });
    addParseToken('hmm', function (input, array, config) {
        var pos = input.length - 2;
        array[HOUR] = toInt(input.substr(0, pos));
        array[MINUTE] = toInt(input.substr(pos));
        getParsingFlags(config).bigHour = true;
    });
    addParseToken('hmmss', function (input, array, config) {
        var pos1 = input.length - 4,
            pos2 = input.length - 2;
        array[HOUR] = toInt(input.substr(0, pos1));
        array[MINUTE] = toInt(input.substr(pos1, 2));
        array[SECOND] = toInt(input.substr(pos2));
        getParsingFlags(config).bigHour = true;
    });
    addParseToken('Hmm', function (input, array, config) {
        var pos = input.length - 2;
        array[HOUR] = toInt(input.substr(0, pos));
        array[MINUTE] = toInt(input.substr(pos));
    });
    addParseToken('Hmmss', function (input, array, config) {
        var pos1 = input.length - 4,
            pos2 = input.length - 2;
        array[HOUR] = toInt(input.substr(0, pos1));
        array[MINUTE] = toInt(input.substr(pos1, 2));
        array[SECOND] = toInt(input.substr(pos2));
    });

    // LOCALES

    function localeIsPM(input) {
        // IE8 Quirks Mode & IE7 Standards Mode do not allow accessing strings like arrays
        // Using charAt should be more compatible.
        return (input + '').toLowerCase().charAt(0) === 'p';
    }

    var defaultLocaleMeridiemParse = /[ap]\.?m?\.?/i,
        // Setting the hour should keep the time, because the user explicitly
        // specified which hour they want. So trying to maintain the same hour (in
        // a new timezone) makes sense. Adding/subtracting hours does not follow
        // this rule.
        getSetHour = makeGetSet('Hours', true);

    function localeMeridiem(hours, minutes, isLower) {
        if (hours > 11) {
            return isLower ? 'pm' : 'PM';
        } else {
            return isLower ? 'am' : 'AM';
        }
    }

    var baseConfig = {
        calendar: defaultCalendar,
        longDateFormat: defaultLongDateFormat,
        invalidDate: defaultInvalidDate,
        ordinal: defaultOrdinal,
        dayOfMonthOrdinalParse: defaultDayOfMonthOrdinalParse,
        relativeTime: defaultRelativeTime,

        months: defaultLocaleMonths,
        monthsShort: defaultLocaleMonthsShort,

        week: defaultLocaleWeek,

        weekdays: defaultLocaleWeekdays,
        weekdaysMin: defaultLocaleWeekdaysMin,
        weekdaysShort: defaultLocaleWeekdaysShort,

        meridiemParse: defaultLocaleMeridiemParse,
    };

    // internal storage for locale config files
    var locales = {},
        localeFamilies = {},
        globalLocale;

    function commonPrefix(arr1, arr2) {
        var i,
            minl = Math.min(arr1.length, arr2.length);
        for (i = 0; i < minl; i += 1) {
            if (arr1[i] !== arr2[i]) {
                return i;
            }
        }
        return minl;
    }

    function normalizeLocale(key) {
        return key ? key.toLowerCase().replace('_', '-') : key;
    }

    // pick the locale from the array
    // try ['en-au', 'en-gb'] as 'en-au', 'en-gb', 'en', as in move through the list trying each
    // substring from most specific to least, but move to the next array item if it's a more specific variant than the current root
    function chooseLocale(names) {
        var i = 0,
            j,
            next,
            locale,
            split;

        while (i < names.length) {
            split = normalizeLocale(names[i]).split('-');
            j = split.length;
            next = normalizeLocale(names[i + 1]);
            next = next ? next.split('-') : null;
            while (j > 0) {
                locale = loadLocale(split.slice(0, j).join('-'));
                if (locale) {
                    return locale;
                }
                if (
                    next &&
                    next.length >= j &&
                    commonPrefix(split, next) >= j - 1
                ) {
                    //the next array item is better than a shallower substring of this one
                    break;
                }
                j--;
            }
            i++;
        }
        return globalLocale;
    }

    function isLocaleNameSane(name) {
        // Prevent names that look like filesystem paths, i.e contain '/' or '\'
        // Ensure name is available and function returns boolean
        return !!(name && name.match('^[^/\\\\]*$'));
    }

    function loadLocale(name) {
        var oldLocale = null,
            aliasedRequire;
        // TODO: Find a better way to register and load all the locales in Node
        if (
            locales[name] === undefined &&
            typeof module !== 'undefined' &&
            module &&
            module.exports &&
            isLocaleNameSane(name)
        ) {
            try {
                oldLocale = globalLocale._abbr;
                aliasedRequire = require;
                aliasedRequire('./locale/' + name);
                getSetGlobalLocale(oldLocale);
            } catch (e) {
                // mark as not found to avoid repeating expensive file require call causing high CPU
                // when trying to find en-US, en_US, en-us for every format call
                locales[name] = null; // null means not found
            }
        }
        return locales[name];
    }

    // This function will load locale and then set the global locale.  If
    // no arguments are passed in, it will simply return the current global
    // locale key.
    function getSetGlobalLocale(key, values) {
        var data;
        if (key) {
            if (isUndefined(values)) {
                data = getLocale(key);
            } else {
                data = defineLocale(key, values);
            }

            if (data) {
                // moment.duration._locale = moment._locale = data;
                globalLocale = data;
            } else {
                if (typeof console !== 'undefined' && console.warn) {
                    //warn user if arguments are passed but the locale could not be set
                    console.warn(
                        'Locale ' + key + ' not found. Did you forget to load it?'
                    );
                }
            }
        }

        return globalLocale._abbr;
    }

    function defineLocale(name, config) {
        if (config !== null) {
            var locale,
                parentConfig = baseConfig;
            config.abbr = name;
            if (locales[name] != null) {
                deprecateSimple(
                    'defineLocaleOverride',
                    'use moment.updateLocale(localeName, config) to change ' +
                        'an existing locale. moment.defineLocale(localeName, ' +
                        'config) should only be used for creating a new locale ' +
                        'See http://momentjs.com/guides/#/warnings/define-locale/ for more info.'
                );
                parentConfig = locales[name]._config;
            } else if (config.parentLocale != null) {
                if (locales[config.parentLocale] != null) {
                    parentConfig = locales[config.parentLocale]._config;
                } else {
                    locale = loadLocale(config.parentLocale);
                    if (locale != null) {
                        parentConfig = locale._config;
                    } else {
                        if (!localeFamilies[config.parentLocale]) {
                            localeFamilies[config.parentLocale] = [];
                        }
                        localeFamilies[config.parentLocale].push({
                            name: name,
                            config: config,
                        });
                        return null;
                    }
                }
            }
            locales[name] = new Locale(mergeConfigs(parentConfig, config));

            if (localeFamilies[name]) {
                localeFamilies[name].forEach(function (x) {
                    defineLocale(x.name, x.config);
                });
            }

            // backwards compat for now: also set the locale
            // make sure we set the locale AFTER all child locales have been
            // created, so we won't end up with the child locale set.
            getSetGlobalLocale(name);

            return locales[name];
        } else {
            // useful for testing
            delete locales[name];
            return null;
        }
    }

    function updateLocale(name, config) {
        if (config != null) {
            var locale,
                tmpLocale,
                parentConfig = baseConfig;

            if (locales[name] != null && locales[name].parentLocale != null) {
                // Update existing child locale in-place to avoid memory-leaks
                locales[name].set(mergeConfigs(locales[name]._config, config));
            } else {
                // MERGE
                tmpLocale = loadLocale(name);
                if (tmpLocale != null) {
                    parentConfig = tmpLocale._config;
                }
                config = mergeConfigs(parentConfig, config);
                if (tmpLocale == null) {
                    // updateLocale is called for creating a new locale
                    // Set abbr so it will have a name (getters return
                    // undefined otherwise).
                    config.abbr = name;
                }
                locale = new Locale(config);
                locale.parentLocale = locales[name];
                locales[name] = locale;
            }

            // backwards compat for now: also set the locale
            getSetGlobalLocale(name);
        } else {
            // pass null for config to unupdate, useful for tests
            if (locales[name] != null) {
                if (locales[name].parentLocale != null) {
                    locales[name] = locales[name].parentLocale;
                    if (name === getSetGlobalLocale()) {
                        getSetGlobalLocale(name);
                    }
                } else if (locales[name] != null) {
                    delete locales[name];
                }
            }
        }
        return locales[name];
    }

    // returns locale data
    function getLocale(key) {
        var locale;

        if (key && key._locale && key._locale._abbr) {
            key = key._locale._abbr;
        }

        if (!key) {
            return globalLocale;
        }

        if (!isArray(key)) {
            //short-circuit everything else
            locale = loadLocale(key);
            if (locale) {
                return locale;
            }
            key = [key];
        }

        return chooseLocale(key);
    }

    function listLocales() {
        return keys(locales);
    }

    function checkOverflow(m) {
        var overflow,
            a = m._a;

        if (a && getParsingFlags(m).overflow === -2) {
            overflow =
                a[MONTH] < 0 || a[MONTH] > 11
                    ? MONTH
                    : a[DATE] < 1 || a[DATE] > daysInMonth(a[YEAR], a[MONTH])
                      ? DATE
                      : a[HOUR] < 0 ||
                          a[HOUR] > 24 ||
                          (a[HOUR] === 24 &&
                              (a[MINUTE] !== 0 ||
                                  a[SECOND] !== 0 ||
                                  a[MILLISECOND] !== 0))
                        ? HOUR
                        : a[MINUTE] < 0 || a[MINUTE] > 59
                          ? MINUTE
                          : a[SECOND] < 0 || a[SECOND] > 59
                            ? SECOND
                            : a[MILLISECOND] < 0 || a[MILLISECOND] > 999
                              ? MILLISECOND
                              : -1;

            if (
                getParsingFlags(m)._overflowDayOfYear &&
                (overflow < YEAR || overflow > DATE)
            ) {
                overflow = DATE;
            }
            if (getParsingFlags(m)._overflowWeeks && overflow === -1) {
                overflow = WEEK;
            }
            if (getParsingFlags(m)._overflowWeekday && overflow === -1) {
                overflow = WEEKDAY;
            }

            getParsingFlags(m).overflow = overflow;
        }

        return m;
    }

    // iso 8601 regex
    // 0000-00-00 0000-W00 or 0000-W00-0 + T + 00 or 00:00 or 00:00:00 or 00:00:00.000 + +00:00 or +0000 or +00)
    var extendedIsoRegex =
            /^\s*((?:[+-]\d{6}|\d{4})-(?:\d\d-\d\d|W\d\d-\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?::\d\d(?::\d\d(?:[.,]\d+)?)?)?)([+-]\d\d(?::?\d\d)?|\s*Z)?)?$/,
        basicIsoRegex =
            /^\s*((?:[+-]\d{6}|\d{4})(?:\d\d\d\d|W\d\d\d|W\d\d|\d\d\d|\d\d|))(?:(T| )(\d\d(?:\d\d(?:\d\d(?:[.,]\d+)?)?)?)([+-]\d\d(?::?\d\d)?|\s*Z)?)?$/,
        tzRegex = /Z|[+-]\d\d(?::?\d\d)?/,
        isoDates = [
            ['YYYYYY-MM-DD', /[+-]\d{6}-\d\d-\d\d/],
            ['YYYY-MM-DD', /\d{4}-\d\d-\d\d/],
            ['GGGG-[W]WW-E', /\d{4}-W\d\d-\d/],
            ['GGGG-[W]WW', /\d{4}-W\d\d/, false],
            ['YYYY-DDD', /\d{4}-\d{3}/],
            ['YYYY-MM', /\d{4}-\d\d/, false],
            ['YYYYYYMMDD', /[+-]\d{10}/],
            ['YYYYMMDD', /\d{8}/],
            ['GGGG[W]WWE', /\d{4}W\d{3}/],
            ['GGGG[W]WW', /\d{4}W\d{2}/, false],
            ['YYYYDDD', /\d{7}/],
            ['YYYYMM', /\d{6}/, false],
            ['YYYY', /\d{4}/, false],
        ],
        // iso time formats and regexes
        isoTimes = [
            ['HH:mm:ss.SSSS', /\d\d:\d\d:\d\d\.\d+/],
            ['HH:mm:ss,SSSS', /\d\d:\d\d:\d\d,\d+/],
            ['HH:mm:ss', /\d\d:\d\d:\d\d/],
            ['HH:mm', /\d\d:\d\d/],
            ['HHmmss.SSSS', /\d\d\d\d\d\d\.\d+/],
            ['HHmmss,SSSS', /\d\d\d\d\d\d,\d+/],
            ['HHmmss', /\d\d\d\d\d\d/],
            ['HHmm', /\d\d\d\d/],
            ['HH', /\d\d/],
        ],
        aspNetJsonRegex = /^\/?Date\((-?\d+)/i,
        // RFC 2822 regex: For details see https://tools.ietf.org/html/rfc2822#section-3.3
        rfc2822 =
            /^(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s)?(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{2,4})\s(\d\d):(\d\d)(?::(\d\d))?\s(?:(UT|GMT|[ECMP][SD]T)|([Zz])|([+-]\d{4}))$/,
        obsOffsets = {
            UT: 0,
            GMT: 0,
            EDT: -4 * 60,
            EST: -5 * 60,
            CDT: -5 * 60,
            CST: -6 * 60,
            MDT: -6 * 60,
            MST: -7 * 60,
            PDT: -7 * 60,
            PST: -8 * 60,
        };

    // date from iso format
    function configFromISO(config) {
        var i,
            l,
            string = config._i,
            match = extendedIsoRegex.exec(string) || basicIsoRegex.exec(string),
            allowTime,
            dateFormat,
            timeFormat,
            tzFormat,
            isoDatesLen = isoDates.length,
            isoTimesLen = isoTimes.length;

        if (match) {
            getParsingFlags(config).iso = true;
            for (i = 0, l = isoDatesLen; i < l; i++) {
                if (isoDates[i][1].exec(match[1])) {
                    dateFormat = isoDates[i][0];
                    allowTime = isoDates[i][2] !== false;
                    break;
                }
            }
            if (dateFormat == null) {
                config._isValid = false;
                return;
            }
            if (match[3]) {
                for (i = 0, l = isoTimesLen; i < l; i++) {
                    if (isoTimes[i][1].exec(match[3])) {
                        // match[2] should be 'T' or space
                        timeFormat = (match[2] || ' ') + isoTimes[i][0];
                        break;
                    }
                }
                if (timeFormat == null) {
                    config._isValid = false;
                    return;
                }
            }
            if (!allowTime && timeFormat != null) {
                config._isValid = false;
                return;
            }
            if (match[4]) {
                if (tzRegex.exec(match[4])) {
                    tzFormat = 'Z';
                } else {
                    config._isValid = false;
                    return;
                }
            }
            config._f = dateFormat + (timeFormat || '') + (tzFormat || '');
            configFromStringAndFormat(config);
        } else {
            config._isValid = false;
        }
    }

    function extractFromRFC2822Strings(
        yearStr,
        monthStr,
        dayStr,
        hourStr,
        minuteStr,
        secondStr
    ) {
        var result = [
            untruncateYear(yearStr),
            defaultLocaleMonthsShort.indexOf(monthStr),
            parseInt(dayStr, 10),
            parseInt(hourStr, 10),
            parseInt(minuteStr, 10),
        ];

        if (secondStr) {
            result.push(parseInt(secondStr, 10));
        }

        return result;
    }

    function untruncateYear(yearStr) {
        var year = parseInt(yearStr, 10);
        if (year <= 49) {
            return 2000 + year;
        } else if (year <= 999) {
            return 1900 + year;
        }
        return year;
    }

    function preprocessRFC2822(s) {
        // Remove comments and folding whitespace and replace multiple-spaces with a single space
        return s
            .replace(/\([^()]*\)|[\n\t]/g, ' ')
            .replace(/(\s\s+)/g, ' ')
            .replace(/^\s\s*/, '')
            .replace(/\s\s*$/, '');
    }

    function checkWeekday(weekdayStr, parsedInput, config) {
        if (weekdayStr) {
            // TODO: Replace the vanilla JS Date object with an independent day-of-week check.
            var weekdayProvided = defaultLocaleWeekdaysShort.indexOf(weekdayStr),
                weekdayActual = new Date(
                    parsedInput[0],
                    parsedInput[1],
                    parsedInput[2]
                ).getDay();
            if (weekdayProvided !== weekdayActual) {
                getParsingFlags(config).weekdayMismatch = true;
                config._isValid = false;
                return false;
            }
        }
        return true;
    }

    function calculateOffset(obsOffset, militaryOffset, numOffset) {
        if (obsOffset) {
            return obsOffsets[obsOffset];
        } else if (militaryOffset) {
            // the only allowed military tz is Z
            return 0;
        } else {
            var hm = parseInt(numOffset, 10),
                m = hm % 100,
                h = (hm - m) / 100;
            return h * 60 + m;
        }
    }

    // date and time from ref 2822 format
    function configFromRFC2822(config) {
        var match = rfc2822.exec(preprocessRFC2822(config._i)),
            parsedArray;
        if (match) {
            parsedArray = extractFromRFC2822Strings(
                match[4],
                match[3],
                match[2],
                match[5],
                match[6],
                match[7]
            );
            if (!checkWeekday(match[1], parsedArray, config)) {
                return;
            }

            config._a = parsedArray;
            config._tzm = calculateOffset(match[8], match[9], match[10]);

            config._d = createUTCDate.apply(null, config._a);
            config._d.setUTCMinutes(config._d.getUTCMinutes() - config._tzm);

            getParsingFlags(config).rfc2822 = true;
        } else {
            config._isValid = false;
        }
    }

    // date from 1) ASP.NET, 2) ISO, 3) RFC 2822 formats, or 4) optional fallback if parsing isn't strict
    function configFromString(config) {
        var matched = aspNetJsonRegex.exec(config._i);
        if (matched !== null) {
            config._d = new Date(+matched[1]);
            return;
        }

        configFromISO(config);
        if (config._isValid === false) {
            delete config._isValid;
        } else {
            return;
        }

        configFromRFC2822(config);
        if (config._isValid === false) {
            delete config._isValid;
        } else {
            return;
        }

        if (config._strict) {
            config._isValid = false;
        } else {
            // Final attempt, use Input Fallback
            hooks.createFromInputFallback(config);
        }
    }

    hooks.createFromInputFallback = deprecate(
        'value provided is not in a recognized RFC2822 or ISO format. moment construction falls back to js Date(), ' +
            'which is not reliable across all browsers and versions. Non RFC2822/ISO date formats are ' +
            'discouraged. Please refer to http://momentjs.com/guides/#/warnings/js-date/ for more info.',
        function (config) {
            config._d = new Date(config._i + (config._useUTC ? ' UTC' : ''));
        }
    );

    // Pick the first defined of two or three arguments.
    function defaults(a, b, c) {
        if (a != null) {
            return a;
        }
        if (b != null) {
            return b;
        }
        return c;
    }

    function currentDateArray(config) {
        // hooks is actually the exported moment object
        var nowValue = new Date(hooks.now());
        if (config._useUTC) {
            return [
                nowValue.getUTCFullYear(),
                nowValue.getUTCMonth(),
                nowValue.getUTCDate(),
            ];
        }
        return [nowValue.getFullYear(), nowValue.getMonth(), nowValue.getDate()];
    }

    // convert an array to a date.
    // the array should mirror the parameters below
    // note: all values past the year are optional and will default to the lowest possible value.
    // [year, month, day , hour, minute, second, millisecond]
    function configFromArray(config) {
        var i,
            date,
            input = [],
            currentDate,
            expectedWeekday,
            yearToUse;

        if (config._d) {
            return;
        }

        currentDate = currentDateArray(config);

        //compute day of the year from weeks and weekdays
        if (config._w && config._a[DATE] == null && config._a[MONTH] == null) {
            dayOfYearFromWeekInfo(config);
        }

        //if the day of the year is set, figure out what it is
        if (config._dayOfYear != null) {
            yearToUse = defaults(config._a[YEAR], currentDate[YEAR]);

            if (
                config._dayOfYear > daysInYear(yearToUse) ||
                config._dayOfYear === 0
            ) {
                getParsingFlags(config)._overflowDayOfYear = true;
            }

            date = createUTCDate(yearToUse, 0, config._dayOfYear);
            config._a[MONTH] = date.getUTCMonth();
            config._a[DATE] = date.getUTCDate();
        }

        // Default to current date.
        // * if no year, month, day of month are given, default to today
        // * if day of month is given, default month and year
        // * if month is given, default only year
        // * if year is given, don't default anything
        for (i = 0; i < 3 && config._a[i] == null; ++i) {
            config._a[i] = input[i] = currentDate[i];
        }

        // Zero out whatever was not defaulted, including time
        for (; i < 7; i++) {
            config._a[i] = input[i] =
                config._a[i] == null ? (i === 2 ? 1 : 0) : config._a[i];
        }

        // Check for 24:00:00.000
        if (
            config._a[HOUR] === 24 &&
            config._a[MINUTE] === 0 &&
            config._a[SECOND] === 0 &&
            config._a[MILLISECOND] === 0
        ) {
            config._nextDay = true;
            config._a[HOUR] = 0;
        }

        config._d = (config._useUTC ? createUTCDate : createDate).apply(
            null,
            input
        );
        expectedWeekday = config._useUTC
            ? config._d.getUTCDay()
            : config._d.getDay();

        // Apply timezone offset from input. The actual utcOffset can be changed
        // with parseZone.
        if (config._tzm != null) {
            config._d.setUTCMinutes(config._d.getUTCMinutes() - config._tzm);
        }

        if (config._nextDay) {
            config._a[HOUR] = 24;
        }

        // check for mismatching day of week
        if (
            config._w &&
            typeof config._w.d !== 'undefined' &&
            config._w.d !== expectedWeekday
        ) {
            getParsingFlags(config).weekdayMismatch = true;
        }
    }

    function dayOfYearFromWeekInfo(config) {
        var w, weekYear, week, weekday, dow, doy, temp, weekdayOverflow, curWeek;

        w = config._w;
        if (w.GG != null || w.W != null || w.E != null) {
            dow = 1;
            doy = 4;

            // TODO: We need to take the current isoWeekYear, but that depends on
            // how we interpret now (local, utc, fixed offset). So create
            // a now version of current config (take local/utc/offset flags, and
            // create now).
            weekYear = defaults(
                w.GG,
                config._a[YEAR],
                weekOfYear(createLocal(), 1, 4).year
            );
            week = defaults(w.W, 1);
            weekday = defaults(w.E, 1);
            if (weekday < 1 || weekday > 7) {
                weekdayOverflow = true;
            }
        } else {
            dow = config._locale._week.dow;
            doy = config._locale._week.doy;

            curWeek = weekOfYear(createLocal(), dow, doy);

            weekYear = defaults(w.gg, config._a[YEAR], curWeek.year);

            // Default to current week.
            week = defaults(w.w, curWeek.week);

            if (w.d != null) {
                // weekday -- low day numbers are considered next week
                weekday = w.d;
                if (weekday < 0 || weekday > 6) {
                    weekdayOverflow = true;
                }
            } else if (w.e != null) {
                // local weekday -- counting starts from beginning of week
                weekday = w.e + dow;
                if (w.e < 0 || w.e > 6) {
                    weekdayOverflow = true;
                }
            } else {
                // default to beginning of week
                weekday = dow;
            }
        }
        if (week < 1 || week > weeksInYear(weekYear, dow, doy)) {
            getParsingFlags(config)._overflowWeeks = true;
        } else if (weekdayOverflow != null) {
            getParsingFlags(config)._overflowWeekday = true;
        } else {
            temp = dayOfYearFromWeeks(weekYear, week, weekday, dow, doy);
            config._a[YEAR] = temp.year;
            config._dayOfYear = temp.dayOfYear;
        }
    }

    // constant that refers to the ISO standard
    hooks.ISO_8601 = function () {};

    // constant that refers to the RFC 2822 form
    hooks.RFC_2822 = function () {};

    // date from string and format string
    function configFromStringAndFormat(config) {
        // TODO: Move this to another part of the creation flow to prevent circular deps
        if (config._f === hooks.ISO_8601) {
            configFromISO(config);
            return;
        }
        if (config._f === hooks.RFC_2822) {
            configFromRFC2822(config);
            return;
        }
        config._a = [];
        getParsingFlags(config).empty = true;

        // This array is used to make a Date, either with `new Date` or `Date.UTC`
        var string = '' + config._i,
            i,
            parsedInput,
            tokens,
            token,
            skipped,
            stringLength = string.length,
            totalParsedInputLength = 0,
            era,
            tokenLen;

        tokens =
            expandFormat(config._f, config._locale).match(formattingTokens) || [];
        tokenLen = tokens.length;
        for (i = 0; i < tokenLen; i++) {
            token = tokens[i];
            parsedInput = (string.match(getParseRegexForToken(token, config)) ||
                [])[0];
            if (parsedInput) {
                skipped = string.substr(0, string.indexOf(parsedInput));
                if (skipped.length > 0) {
                    getParsingFlags(config).unusedInput.push(skipped);
                }
                string = string.slice(
                    string.indexOf(parsedInput) + parsedInput.length
                );
                totalParsedInputLength += parsedInput.length;
            }
            // don't parse if it's not a known token
            if (formatTokenFunctions[token]) {
                if (parsedInput) {
                    getParsingFlags(config).empty = false;
                } else {
                    getParsingFlags(config).unusedTokens.push(token);
                }
                addTimeToArrayFromToken(token, parsedInput, config);
            } else if (config._strict && !parsedInput) {
                getParsingFlags(config).unusedTokens.push(token);
            }
        }

        // add remaining unparsed input length to the string
        getParsingFlags(config).charsLeftOver =
            stringLength - totalParsedInputLength;
        if (string.length > 0) {
            getParsingFlags(config).unusedInput.push(string);
        }

        // clear _12h flag if hour is <= 12
        if (
            config._a[HOUR] <= 12 &&
            getParsingFlags(config).bigHour === true &&
            config._a[HOUR] > 0
        ) {
            getParsingFlags(config).bigHour = undefined;
        }

        getParsingFlags(config).parsedDateParts = config._a.slice(0);
        getParsingFlags(config).meridiem = config._meridiem;
        // handle meridiem
        config._a[HOUR] = meridiemFixWrap(
            config._locale,
            config._a[HOUR],
            config._meridiem
        );

        // handle era
        era = getParsingFlags(config).era;
        if (era !== null) {
            config._a[YEAR] = config._locale.erasConvertYear(era, config._a[YEAR]);
        }

        configFromArray(config);
        checkOverflow(config);
    }

    function meridiemFixWrap(locale, hour, meridiem) {
        var isPm;

        if (meridiem == null) {
            // nothing to do
            return hour;
        }
        if (locale.meridiemHour != null) {
            return locale.meridiemHour(hour, meridiem);
        } else if (locale.isPM != null) {
            // Fallback
            isPm = locale.isPM(meridiem);
            if (isPm && hour < 12) {
                hour += 12;
            }
            if (!isPm && hour === 12) {
                hour = 0;
            }
            return hour;
        } else {
            // this is not supposed to happen
            return hour;
        }
    }

    // date from string and array of format strings
    function configFromStringAndArray(config) {
        var tempConfig,
            bestMoment,
            scoreToBeat,
            i,
            currentScore,
            validFormatFound,
            bestFormatIsValid = false,
            configfLen = config._f.length;

        if (configfLen === 0) {
            getParsingFlags(config).invalidFormat = true;
            config._d = new Date(NaN);
            return;
        }

        for (i = 0; i < configfLen; i++) {
            currentScore = 0;
            validFormatFound = false;
            tempConfig = copyConfig({}, config);
            if (config._useUTC != null) {
                tempConfig._useUTC = config._useUTC;
            }
            tempConfig._f = config._f[i];
            configFromStringAndFormat(tempConfig);

            if (isValid(tempConfig)) {
                validFormatFound = true;
            }

            // if there is any input that was not parsed add a penalty for that format
            currentScore += getParsingFlags(tempConfig).charsLeftOver;

            //or tokens
            currentScore += getParsingFlags(tempConfig).unusedTokens.length * 10;

            getParsingFlags(tempConfig).score = currentScore;

            if (!bestFormatIsValid) {
                if (
                    scoreToBeat == null ||
                    currentScore < scoreToBeat ||
                    validFormatFound
                ) {
                    scoreToBeat = currentScore;
                    bestMoment = tempConfig;
                    if (validFormatFound) {
                        bestFormatIsValid = true;
                    }
                }
            } else {
                if (currentScore < scoreToBeat) {
                    scoreToBeat = currentScore;
                    bestMoment = tempConfig;
                }
            }
        }

        extend(config, bestMoment || tempConfig);
    }

    function configFromObject(config) {
        if (config._d) {
            return;
        }

        var i = normalizeObjectUnits(config._i),
            dayOrDate = i.day === undefined ? i.date : i.day;
        config._a = map(
            [i.year, i.month, dayOrDate, i.hour, i.minute, i.second, i.millisecond],
            function (obj) {
                return obj && parseInt(obj, 10);
            }
        );

        configFromArray(config);
    }

    function createFromConfig(config) {
        var res = new Moment(checkOverflow(prepareConfig(config)));
        if (res._nextDay) {
            // Adding is smart enough around DST
            res.add(1, 'd');
            res._nextDay = undefined;
        }

        return res;
    }

    function prepareConfig(config) {
        var input = config._i,
            format = config._f;

        config._locale = config._locale || getLocale(config._l);

        if (input === null || (format === undefined && input === '')) {
            return createInvalid({ nullInput: true });
        }

        if (typeof input === 'string') {
            config._i = input = config._locale.preparse(input);
        }

        if (isMoment(input)) {
            return new Moment(checkOverflow(input));
        } else if (isDate(input)) {
            config._d = input;
        } else if (isArray(format)) {
            configFromStringAndArray(config);
        } else if (format) {
            configFromStringAndFormat(config);
        } else {
            configFromInput(config);
        }

        if (!isValid(config)) {
            config._d = null;
        }

        return config;
    }

    function configFromInput(config) {
        var input = config._i;
        if (isUndefined(input)) {
            config._d = new Date(hooks.now());
        } else if (isDate(input)) {
            config._d = new Date(input.valueOf());
        } else if (typeof input === 'string') {
            configFromString(config);
        } else if (isArray(input)) {
            config._a = map(input.slice(0), function (obj) {
                return parseInt(obj, 10);
            });
            configFromArray(config);
        } else if (isObject(input)) {
            configFromObject(config);
        } else if (isNumber(input)) {
            // from milliseconds
            config._d = new Date(input);
        } else {
            hooks.createFromInputFallback(config);
        }
    }

    function createLocalOrUTC(input, format, locale, strict, isUTC) {
        var c = {};

        if (format === true || format === false) {
            strict = format;
            format = undefined;
        }

        if (locale === true || locale === false) {
            strict = locale;
            locale = undefined;
        }

        if (
            (isObject(input) && isObjectEmpty(input)) ||
            (isArray(input) && input.length === 0)
        ) {
            input = undefined;
        }
        // object construction must be done this way.
        // https://github.com/moment/moment/issues/1423
        c._isAMomentObject = true;
        c._useUTC = c._isUTC = isUTC;
        c._l = locale;
        c._i = input;
        c._f = format;
        c._strict = strict;

        return createFromConfig(c);
    }

    function createLocal(input, format, locale, strict) {
        return createLocalOrUTC(input, format, locale, strict, false);
    }

    var prototypeMin = deprecate(
            'moment().min is deprecated, use moment.max instead. http://momentjs.com/guides/#/warnings/min-max/',
            function () {
                var other = createLocal.apply(null, arguments);
                if (this.isValid() && other.isValid()) {
                    return other < this ? this : other;
                } else {
                    return createInvalid();
                }
            }
        ),
        prototypeMax = deprecate(
            'moment().max is deprecated, use moment.min instead. http://momentjs.com/guides/#/warnings/min-max/',
            function () {
                var other = createLocal.apply(null, arguments);
                if (this.isValid() && other.isValid()) {
                    return other > this ? this : other;
                } else {
                    return createInvalid();
                }
            }
        );

    // Pick a moment m from moments so that m[fn](other) is true for all
    // other. This relies on the function fn to be transitive.
    //
    // moments should either be an array of moment objects or an array, whose
    // first element is an array of moment objects.
    function pickBy(fn, moments) {
        var res, i;
        if (moments.length === 1 && isArray(moments[0])) {
            moments = moments[0];
        }
        if (!moments.length) {
            return createLocal();
        }
        res = moments[0];
        for (i = 1; i < moments.length; ++i) {
            if (!moments[i].isValid() || moments[i][fn](res)) {
                res = moments[i];
            }
        }
        return res;
    }

    // TODO: Use [].sort instead?
    function min() {
        var args = [].slice.call(arguments, 0);

        return pickBy('isBefore', args);
    }

    function max() {
        var args = [].slice.call(arguments, 0);

        return pickBy('isAfter', args);
    }

    var now = function () {
        return Date.now ? Date.now() : +new Date();
    };

    var ordering = [
        'year',
        'quarter',
        'month',
        'week',
        'day',
        'hour',
        'minute',
        'second',
        'millisecond',
    ];

    function isDurationValid(m) {
        var key,
            unitHasDecimal = false,
            i,
            orderLen = ordering.length;
        for (key in m) {
            if (
                hasOwnProp(m, key) &&
                !(
                    indexOf.call(ordering, key) !== -1 &&
                    (m[key] == null || !isNaN(m[key]))
                )
            ) {
                return false;
            }
        }

        for (i = 0; i < orderLen; ++i) {
            if (m[ordering[i]]) {
                if (unitHasDecimal) {
                    return false; // only allow non-integers for smallest unit
                }
                if (parseFloat(m[ordering[i]]) !== toInt(m[ordering[i]])) {
                    unitHasDecimal = true;
                }
            }
        }

        return true;
    }

    function isValid$1() {
        return this._isValid;
    }

    function createInvalid$1() {
        return createDuration(NaN);
    }

    function Duration(duration) {
        var normalizedInput = normalizeObjectUnits(duration),
            years = normalizedInput.year || 0,
            quarters = normalizedInput.quarter || 0,
            months = normalizedInput.month || 0,
            weeks = normalizedInput.week || normalizedInput.isoWeek || 0,
            days = normalizedInput.day || 0,
            hours = normalizedInput.hour || 0,
            minutes = normalizedInput.minute || 0,
            seconds = normalizedInput.second || 0,
            milliseconds = normalizedInput.millisecond || 0;

        this._isValid = isDurationValid(normalizedInput);

        // representation for dateAddRemove
        this._milliseconds =
            +milliseconds +
            seconds * 1e3 + // 1000
            minutes * 6e4 + // 1000 * 60
            hours * 1000 * 60 * 60; //using 1000 * 60 * 60 instead of 36e5 to avoid floating point rounding errors https://github.com/moment/moment/issues/2978
        // Because of dateAddRemove treats 24 hours as different from a
        // day when working around DST, we need to store them separately
        this._days = +days + weeks * 7;
        // It is impossible to translate months into days without knowing
        // which months you are are talking about, so we have to store
        // it separately.
        this._months = +months + quarters * 3 + years * 12;

        this._data = {};

        this._locale = getLocale();

        this._bubble();
    }

    function isDuration(obj) {
        return obj instanceof Duration;
    }

    function absRound(number) {
        if (number < 0) {
            return Math.round(-1 * number) * -1;
        } else {
            return Math.round(number);
        }
    }

    // compare two arrays, return the number of differences
    function compareArrays(array1, array2, dontConvert) {
        var len = Math.min(array1.length, array2.length),
            lengthDiff = Math.abs(array1.length - array2.length),
            diffs = 0,
            i;
        for (i = 0; i < len; i++) {
            if (
                (dontConvert && array1[i] !== array2[i]) ||
                (!dontConvert && toInt(array1[i]) !== toInt(array2[i]))
            ) {
                diffs++;
            }
        }
        return diffs + lengthDiff;
    }

    // FORMATTING

    function offset(token, separator) {
        addFormatToken(token, 0, 0, function () {
            var offset = this.utcOffset(),
                sign = '+';
            if (offset < 0) {
                offset = -offset;
                sign = '-';
            }
            return (
                sign +
                zeroFill(~~(offset / 60), 2) +
                separator +
                zeroFill(~~offset % 60, 2)
            );
        });
    }

    offset('Z', ':');
    offset('ZZ', '');

    // PARSING

    addRegexToken('Z', matchShortOffset);
    addRegexToken('ZZ', matchShortOffset);
    addParseToken(['Z', 'ZZ'], function (input, array, config) {
        config._useUTC = true;
        config._tzm = offsetFromString(matchShortOffset, input);
    });

    // HELPERS

    // timezone chunker
    // '+10:00' > ['10',  '00']
    // '-1530'  > ['-15', '30']
    var chunkOffset = /([\+\-]|\d\d)/gi;

    function offsetFromString(matcher, string) {
        var matches = (string || '').match(matcher),
            chunk,
            parts,
            minutes;

        if (matches === null) {
            return null;
        }

        chunk = matches[matches.length - 1] || [];
        parts = (chunk + '').match(chunkOffset) || ['-', 0, 0];
        minutes = +(parts[1] * 60) + toInt(parts[2]);

        return minutes === 0 ? 0 : parts[0] === '+' ? minutes : -minutes;
    }

    // Return a moment from input, that is local/utc/zone equivalent to model.
    function cloneWithOffset(input, model) {
        var res, diff;
        if (model._isUTC) {
            res = model.clone();
            diff =
                (isMoment(input) || isDate(input)
                    ? input.valueOf()
                    : createLocal(input).valueOf()) - res.valueOf();
            // Use low-level api, because this fn is low-level api.
            res._d.setTime(res._d.valueOf() + diff);
            hooks.updateOffset(res, false);
            return res;
        } else {
            return createLocal(input).local();
        }
    }

    function getDateOffset(m) {
        // On Firefox.24 Date#getTimezoneOffset returns a floating point.
        // https://github.com/moment/moment/pull/1871
        return -Math.round(m._d.getTimezoneOffset());
    }

    // HOOKS

    // This function will be called whenever a moment is mutated.
    // It is intended to keep the offset in sync with the timezone.
    hooks.updateOffset = function () {};

    // MOMENTS

    // keepLocalTime = true means only change the timezone, without
    // affecting the local hour. So 5:31:26 +0300 --[utcOffset(2, true)]-->
    // 5:31:26 +0200 It is possible that 5:31:26 doesn't exist with offset
    // +0200, so we adjust the time as needed, to be valid.
    //
    // Keeping the time actually adds/subtracts (one hour)
    // from the actual represented time. That is why we call updateOffset
    // a second time. In case it wants us to change the offset again
    // _changeInProgress == true case, then we have to adjust, because
    // there is no such time in the given timezone.
    function getSetOffset(input, keepLocalTime, keepMinutes) {
        var offset = this._offset || 0,
            localAdjust;
        if (!this.isValid()) {
            return input != null ? this : NaN;
        }
        if (input != null) {
            if (typeof input === 'string') {
                input = offsetFromString(matchShortOffset, input);
                if (input === null) {
                    return this;
                }
            } else if (Math.abs(input) < 16 && !keepMinutes) {
                input = input * 60;
            }
            if (!this._isUTC && keepLocalTime) {
                localAdjust = getDateOffset(this);
            }
            this._offset = input;
            this._isUTC = true;
            if (localAdjust != null) {
                this.add(localAdjust, 'm');
            }
            if (offset !== input) {
                if (!keepLocalTime || this._changeInProgress) {
                    addSubtract(
                        this,
                        createDuration(input - offset, 'm'),
                        1,
                        false
                    );
                } else if (!this._changeInProgress) {
                    this._changeInProgress = true;
                    hooks.updateOffset(this, true);
                    this._changeInProgress = null;
                }
            }
            return this;
        } else {
            return this._isUTC ? offset : getDateOffset(this);
        }
    }

    function getSetZone(input, keepLocalTime) {
        if (input != null) {
            if (typeof input !== 'string') {
                input = -input;
            }

            this.utcOffset(input, keepLocalTime);

            return this;
        } else {
            return -this.utcOffset();
        }
    }

    function setOffsetToUTC(keepLocalTime) {
        return this.utcOffset(0, keepLocalTime);
    }

    function setOffsetToLocal(keepLocalTime) {
        if (this._isUTC) {
            this.utcOffset(0, keepLocalTime);
            this._isUTC = false;

            if (keepLocalTime) {
                this.subtract(getDateOffset(this), 'm');
            }
        }
        return this;
    }

    function setOffsetToParsedOffset() {
        if (this._tzm != null) {
            this.utcOffset(this._tzm, false, true);
        } else if (typeof this._i === 'string') {
            var tZone = offsetFromString(matchOffset, this._i);
            if (tZone != null) {
                this.utcOffset(tZone);
            } else {
                this.utcOffset(0, true);
            }
        }
        return this;
    }

    function hasAlignedHourOffset(input) {
        if (!this.isValid()) {
            return false;
        }
        input = input ? createLocal(input).utcOffset() : 0;

        return (this.utcOffset() - input) % 60 === 0;
    }

    function isDaylightSavingTime() {
        return (
            this.utcOffset() > this.clone().month(0).utcOffset() ||
            this.utcOffset() > this.clone().month(5).utcOffset()
        );
    }

    function isDaylightSavingTimeShifted() {
        if (!isUndefined(this._isDSTShifted)) {
            return this._isDSTShifted;
        }

        var c = {},
            other;

        copyConfig(c, this);
        c = prepareConfig(c);

        if (c._a) {
            other = c._isUTC ? createUTC(c._a) : createLocal(c._a);
            this._isDSTShifted =
                this.isValid() && compareArrays(c._a, other.toArray()) > 0;
        } else {
            this._isDSTShifted = false;
        }

        return this._isDSTShifted;
    }

    function isLocal() {
        return this.isValid() ? !this._isUTC : false;
    }

    function isUtcOffset() {
        return this.isValid() ? this._isUTC : false;
    }

    function isUtc() {
        return this.isValid() ? this._isUTC && this._offset === 0 : false;
    }

    // ASP.NET json date format regex
    var aspNetRegex = /^(-|\+)?(?:(\d*)[. ])?(\d+):(\d+)(?::(\d+)(\.\d*)?)?$/,
        // from http://docs.closure-library.googlecode.com/git/closure_goog_date_date.js.source.html
        // somewhat more in line with 4.4.3.2 2004 spec, but allows decimal anywhere
        // and further modified to allow for strings containing both week and day
        isoRegex =
            /^(-|\+)?P(?:([-+]?[0-9,.]*)Y)?(?:([-+]?[0-9,.]*)M)?(?:([-+]?[0-9,.]*)W)?(?:([-+]?[0-9,.]*)D)?(?:T(?:([-+]?[0-9,.]*)H)?(?:([-+]?[0-9,.]*)M)?(?:([-+]?[0-9,.]*)S)?)?$/;

    function createDuration(input, key) {
        var duration = input,
            // matching against regexp is expensive, do it on demand
            match = null,
            sign,
            ret,
            diffRes;

        if (isDuration(input)) {
            duration = {
                ms: input._milliseconds,
                d: input._days,
                M: input._months,
            };
        } else if (isNumber(input) || !isNaN(+input)) {
            duration = {};
            if (key) {
                duration[key] = +input;
            } else {
                duration.milliseconds = +input;
            }
        } else if ((match = aspNetRegex.exec(input))) {
            sign = match[1] === '-' ? -1 : 1;
            duration = {
                y: 0,
                d: toInt(match[DATE]) * sign,
                h: toInt(match[HOUR]) * sign,
                m: toInt(match[MINUTE]) * sign,
                s: toInt(match[SECOND]) * sign,
                ms: toInt(absRound(match[MILLISECOND] * 1000)) * sign, // the millisecond decimal point is included in the match
            };
        } else if ((match = isoRegex.exec(input))) {
            sign = match[1] === '-' ? -1 : 1;
            duration = {
                y: parseIso(match[2], sign),
                M: parseIso(match[3], sign),
                w: parseIso(match[4], sign),
                d: parseIso(match[5], sign),
                h: parseIso(match[6], sign),
                m: parseIso(match[7], sign),
                s: parseIso(match[8], sign),
            };
        } else if (duration == null) {
            // checks for null or undefined
            duration = {};
        } else if (
            typeof duration === 'object' &&
            ('from' in duration || 'to' in duration)
        ) {
            diffRes = momentsDifference(
                createLocal(duration.from),
                createLocal(duration.to)
            );

            duration = {};
            duration.ms = diffRes.milliseconds;
            duration.M = diffRes.months;
        }

        ret = new Duration(duration);

        if (isDuration(input) && hasOwnProp(input, '_locale')) {
            ret._locale = input._locale;
        }

        if (isDuration(input) && hasOwnProp(input, '_isValid')) {
            ret._isValid = input._isValid;
        }

        return ret;
    }

    createDuration.fn = Duration.prototype;
    createDuration.invalid = createInvalid$1;

    function parseIso(inp, sign) {
        // We'd normally use ~~inp for this, but unfortunately it also
        // converts floats to ints.
        // inp may be undefined, so careful calling replace on it.
        var res = inp && parseFloat(inp.replace(',', '.'));
        // apply sign while we're at it
        return (isNaN(res) ? 0 : res) * sign;
    }

    function positiveMomentsDifference(base, other) {
        var res = {};

        res.months =
            other.month() - base.month() + (other.year() - base.year()) * 12;
        if (base.clone().add(res.months, 'M').isAfter(other)) {
            --res.months;
        }

        res.milliseconds = +other - +base.clone().add(res.months, 'M');

        return res;
    }

    function momentsDifference(base, other) {
        var res;
        if (!(base.isValid() && other.isValid())) {
            return { milliseconds: 0, months: 0 };
        }

        other = cloneWithOffset(other, base);
        if (base.isBefore(other)) {
            res = positiveMomentsDifference(base, other);
        } else {
            res = positiveMomentsDifference(other, base);
            res.milliseconds = -res.milliseconds;
            res.months = -res.months;
        }

        return res;
    }

    // TODO: remove 'name' arg after deprecation is removed
    function createAdder(direction, name) {
        return function (val, period) {
            var dur, tmp;
            //invert the arguments, but complain about it
            if (period !== null && !isNaN(+period)) {
                deprecateSimple(
                    name,
                    'moment().' +
                        name +
                        '(period, number) is deprecated. Please use moment().' +
                        name +
                        '(number, period). ' +
                        'See http://momentjs.com/guides/#/warnings/add-inverted-param/ for more info.'
                );
                tmp = val;
                val = period;
                period = tmp;
            }

            dur = createDuration(val, period);
            addSubtract(this, dur, direction);
            return this;
        };
    }

    function addSubtract(mom, duration, isAdding, updateOffset) {
        var milliseconds = duration._milliseconds,
            days = absRound(duration._days),
            months = absRound(duration._months);

        if (!mom.isValid()) {
            // No op
            return;
        }

        updateOffset = updateOffset == null ? true : updateOffset;

        if (months) {
            setMonth(mom, get(mom, 'Month') + months * isAdding);
        }
        if (days) {
            set$1(mom, 'Date', get(mom, 'Date') + days * isAdding);
        }
        if (milliseconds) {
            mom._d.setTime(mom._d.valueOf() + milliseconds * isAdding);
        }
        if (updateOffset) {
            hooks.updateOffset(mom, days || months);
        }
    }

    var add = createAdder(1, 'add'),
        subtract = createAdder(-1, 'subtract');

    function isString(input) {
        return typeof input === 'string' || input instanceof String;
    }

    // type MomentInput = Moment | Date | string | number | (number | string)[] | MomentInputObject | void; // null | undefined
    function isMomentInput(input) {
        return (
            isMoment(input) ||
            isDate(input) ||
            isString(input) ||
            isNumber(input) ||
            isNumberOrStringArray(input) ||
            isMomentInputObject(input) ||
            input === null ||
            input === undefined
        );
    }

    function isMomentInputObject(input) {
        var objectTest = isObject(input) && !isObjectEmpty(input),
            propertyTest = false,
            properties = [
                'years',
                'year',
                'y',
                'months',
                'month',
                'M',
                'days',
                'day',
                'd',
                'dates',
                'date',
                'D',
                'hours',
                'hour',
                'h',
                'minutes',
                'minute',
                'm',
                'seconds',
                'second',
                's',
                'milliseconds',
                'millisecond',
                'ms',
            ],
            i,
            property,
            propertyLen = properties.length;

        for (i = 0; i < propertyLen; i += 1) {
            property = properties[i];
            propertyTest = propertyTest || hasOwnProp(input, property);
        }

        return objectTest && propertyTest;
    }

    function isNumberOrStringArray(input) {
        var arrayTest = isArray(input),
            dataTypeTest = false;
        if (arrayTest) {
            dataTypeTest =
                input.filter(function (item) {
                    return !isNumber(item) && isString(input);
                }).length === 0;
        }
        return arrayTest && dataTypeTest;
    }

    function isCalendarSpec(input) {
        var objectTest = isObject(input) && !isObjectEmpty(input),
            propertyTest = false,
            properties = [
                'sameDay',
                'nextDay',
                'lastDay',
                'nextWeek',
                'lastWeek',
                'sameElse',
            ],
            i,
            property;

        for (i = 0; i < properties.length; i += 1) {
            property = properties[i];
            propertyTest = propertyTest || hasOwnProp(input, property);
        }

        return objectTest && propertyTest;
    }

    function getCalendarFormat(myMoment, now) {
        var diff = myMoment.diff(now, 'days', true);
        return diff < -6
            ? 'sameElse'
            : diff < -1
              ? 'lastWeek'
              : diff < 0
                ? 'lastDay'
                : diff < 1
                  ? 'sameDay'
                  : diff < 2
                    ? 'nextDay'
                    : diff < 7
                      ? 'nextWeek'
                      : 'sameElse';
    }

    function calendar$1(time, formats) {
        // Support for single parameter, formats only overload to the calendar function
        if (arguments.length === 1) {
            if (!arguments[0]) {
                time = undefined;
                formats = undefined;
            } else if (isMomentInput(arguments[0])) {
                time = arguments[0];
                formats = undefined;
            } else if (isCalendarSpec(arguments[0])) {
                formats = arguments[0];
                time = undefined;
            }
        }
        // We want to compare the start of today, vs this.
        // Getting start-of-today depends on whether we're local/utc/offset or not.
        var now = time || createLocal(),
            sod = cloneWithOffset(now, this).startOf('day'),
            format = hooks.calendarFormat(this, sod) || 'sameElse',
            output =
                formats &&
                (isFunction(formats[format])
                    ? formats[format].call(this, now)
                    : formats[format]);

        return this.format(
            output || this.localeData().calendar(format, this, createLocal(now))
        );
    }

    function clone() {
        return new Moment(this);
    }

    function isAfter(input, units) {
        var localInput = isMoment(input) ? input : createLocal(input);
        if (!(this.isValid() && localInput.isValid())) {
            return false;
        }
        units = normalizeUnits(units) || 'millisecond';
        if (units === 'millisecond') {
            return this.valueOf() > localInput.valueOf();
        } else {
            return localInput.valueOf() < this.clone().startOf(units).valueOf();
        }
    }

    function isBefore(input, units) {
        var localInput = isMoment(input) ? input : createLocal(input);
        if (!(this.isValid() && localInput.isValid())) {
            return false;
        }
        units = normalizeUnits(units) || 'millisecond';
        if (units === 'millisecond') {
            return this.valueOf() < localInput.valueOf();
        } else {
            return this.clone().endOf(units).valueOf() < localInput.valueOf();
        }
    }

    function isBetween(from, to, units, inclusivity) {
        var localFrom = isMoment(from) ? from : createLocal(from),
            localTo = isMoment(to) ? to : createLocal(to);
        if (!(this.isValid() && localFrom.isValid() && localTo.isValid())) {
            return false;
        }
        inclusivity = inclusivity || '()';
        return (
            (inclusivity[0] === '('
                ? this.isAfter(localFrom, units)
                : !this.isBefore(localFrom, units)) &&
            (inclusivity[1] === ')'
                ? this.isBefore(localTo, units)
                : !this.isAfter(localTo, units))
        );
    }

    function isSame(input, units) {
        var localInput = isMoment(input) ? input : createLocal(input),
            inputMs;
        if (!(this.isValid() && localInput.isValid())) {
            return false;
        }
        units = normalizeUnits(units) || 'millisecond';
        if (units === 'millisecond') {
            return this.valueOf() === localInput.valueOf();
        } else {
            inputMs = localInput.valueOf();
            return (
                this.clone().startOf(units).valueOf() <= inputMs &&
                inputMs <= this.clone().endOf(units).valueOf()
            );
        }
    }

    function isSameOrAfter(input, units) {
        return this.isSame(input, units) || this.isAfter(input, units);
    }

    function isSameOrBefore(input, units) {
        return this.isSame(input, units) || this.isBefore(input, units);
    }

    function diff(input, units, asFloat) {
        var that, zoneDelta, output;

        if (!this.isValid()) {
            return NaN;
        }

        that = cloneWithOffset(input, this);

        if (!that.isValid()) {
            return NaN;
        }

        zoneDelta = (that.utcOffset() - this.utcOffset()) * 6e4;

        units = normalizeUnits(units);

        switch (units) {
            case 'year':
                output = monthDiff(this, that) / 12;
                break;
            case 'month':
                output = monthDiff(this, that);
                break;
            case 'quarter':
                output = monthDiff(this, that) / 3;
                break;
            case 'second':
                output = (this - that) / 1e3;
                break; // 1000
            case 'minute':
                output = (this - that) / 6e4;
                break; // 1000 * 60
            case 'hour':
                output = (this - that) / 36e5;
                break; // 1000 * 60 * 60
            case 'day':
                output = (this - that - zoneDelta) / 864e5;
                break; // 1000 * 60 * 60 * 24, negate dst
            case 'week':
                output = (this - that - zoneDelta) / 6048e5;
                break; // 1000 * 60 * 60 * 24 * 7, negate dst
            default:
                output = this - that;
        }

        return asFloat ? output : absFloor(output);
    }

    function monthDiff(a, b) {
        if (a.date() < b.date()) {
            // end-of-month calculations work correct when the start month has more
            // days than the end month.
            return -monthDiff(b, a);
        }
        // difference in months
        var wholeMonthDiff = (b.year() - a.year()) * 12 + (b.month() - a.month()),
            // b is in (anchor - 1 month, anchor + 1 month)
            anchor = a.clone().add(wholeMonthDiff, 'months'),
            anchor2,
            adjust;

        if (b - anchor < 0) {
            anchor2 = a.clone().add(wholeMonthDiff - 1, 'months');
            // linear across the month
            adjust = (b - anchor) / (anchor - anchor2);
        } else {
            anchor2 = a.clone().add(wholeMonthDiff + 1, 'months');
            // linear across the month
            adjust = (b - anchor) / (anchor2 - anchor);
        }

        //check for negative zero, return zero if negative zero
        return -(wholeMonthDiff + adjust) || 0;
    }

    hooks.defaultFormat = 'YYYY-MM-DDTHH:mm:ssZ';
    hooks.defaultFormatUtc = 'YYYY-MM-DDTHH:mm:ss[Z]';

    function toString() {
        return this.clone().locale('en').format('ddd MMM DD YYYY HH:mm:ss [GMT]ZZ');
    }

    function toISOString(keepOffset) {
        if (!this.isValid()) {
            return null;
        }
        var utc = keepOffset !== true,
            m = utc ? this.clone().utc() : this;
        if (m.year() < 0 || m.year() > 9999) {
            return formatMoment(
                m,
                utc
                    ? 'YYYYYY-MM-DD[T]HH:mm:ss.SSS[Z]'
                    : 'YYYYYY-MM-DD[T]HH:mm:ss.SSSZ'
            );
        }
        if (isFunction(Date.prototype.toISOString)) {
            // native implementation is ~50x faster, use it when we can
            if (utc) {
                return this.toDate().toISOString();
            } else {
                return new Date(this.valueOf() + this.utcOffset() * 60 * 1000)
                    .toISOString()
                    .replace('Z', formatMoment(m, 'Z'));
            }
        }
        return formatMoment(
            m,
            utc ? 'YYYY-MM-DD[T]HH:mm:ss.SSS[Z]' : 'YYYY-MM-DD[T]HH:mm:ss.SSSZ'
        );
    }

    /**
     * Return a human readable representation of a moment that can
     * also be evaluated to get a new moment which is the same
     *
     * @link https://nodejs.org/dist/latest/docs/api/util.html#util_custom_inspect_function_on_objects
     */
    function inspect() {
        if (!this.isValid()) {
            return 'moment.invalid(/* ' + this._i + ' */)';
        }
        var func = 'moment',
            zone = '',
            prefix,
            year,
            datetime,
            suffix;
        if (!this.isLocal()) {
            func = this.utcOffset() === 0 ? 'moment.utc' : 'moment.parseZone';
            zone = 'Z';
        }
        prefix = '[' + func + '("]';
        year = 0 <= this.year() && this.year() <= 9999 ? 'YYYY' : 'YYYYYY';
        datetime = '-MM-DD[T]HH:mm:ss.SSS';
        suffix = zone + '[")]';

        return this.format(prefix + year + datetime + suffix);
    }

    function format(inputString) {
        if (!inputString) {
            inputString = this.isUtc()
                ? hooks.defaultFormatUtc
                : hooks.defaultFormat;
        }
        var output = formatMoment(this, inputString);
        return this.localeData().postformat(output);
    }

    function from(time, withoutSuffix) {
        if (
            this.isValid() &&
            ((isMoment(time) && time.isValid()) || createLocal(time).isValid())
        ) {
            return createDuration({ to: this, from: time })
                .locale(this.locale())
                .humanize(!withoutSuffix);
        } else {
            return this.localeData().invalidDate();
        }
    }

    function fromNow(withoutSuffix) {
        return this.from(createLocal(), withoutSuffix);
    }

    function to(time, withoutSuffix) {
        if (
            this.isValid() &&
            ((isMoment(time) && time.isValid()) || createLocal(time).isValid())
        ) {
            return createDuration({ from: this, to: time })
                .locale(this.locale())
                .humanize(!withoutSuffix);
        } else {
            return this.localeData().invalidDate();
        }
    }

    function toNow(withoutSuffix) {
        return this.to(createLocal(), withoutSuffix);
    }

    // If passed a locale key, it will set the locale for this
    // instance.  Otherwise, it will return the locale configuration
    // variables for this instance.
    function locale(key) {
        var newLocaleData;

        if (key === undefined) {
            return this._locale._abbr;
        } else {
            newLocaleData = getLocale(key);
            if (newLocaleData != null) {
                this._locale = newLocaleData;
            }
            return this;
        }
    }

    var lang = deprecate(
        'moment().lang() is deprecated. Instead, use moment().localeData() to get the language configuration. Use moment().locale() to change languages.',
        function (key) {
            if (key === undefined) {
                return this.localeData();
            } else {
                return this.locale(key);
            }
        }
    );

    function localeData() {
        return this._locale;
    }

    var MS_PER_SECOND = 1000,
        MS_PER_MINUTE = 60 * MS_PER_SECOND,
        MS_PER_HOUR = 60 * MS_PER_MINUTE,
        MS_PER_400_YEARS = (365 * 400 + 97) * 24 * MS_PER_HOUR;

    // actual modulo - handles negative numbers (for dates before 1970):
    function mod$1(dividend, divisor) {
        return ((dividend % divisor) + divisor) % divisor;
    }

    function localStartOfDate(y, m, d) {
        // the date constructor remaps years 0-99 to 1900-1999
        if (y < 100 && y >= 0) {
            // preserve leap years using a full 400 year cycle, then reset
            return new Date(y + 400, m, d) - MS_PER_400_YEARS;
        } else {
            return new Date(y, m, d).valueOf();
        }
    }

    function utcStartOfDate(y, m, d) {
        // Date.UTC remaps years 0-99 to 1900-1999
        if (y < 100 && y >= 0) {
            // preserve leap years using a full 400 year cycle, then reset
            return Date.UTC(y + 400, m, d) - MS_PER_400_YEARS;
        } else {
            return Date.UTC(y, m, d);
        }
    }

    function startOf(units) {
        var time, startOfDate;
        units = normalizeUnits(units);
        if (units === undefined || units === 'millisecond' || !this.isValid()) {
            return this;
        }

        startOfDate = this._isUTC ? utcStartOfDate : localStartOfDate;

        switch (units) {
            case 'year':
                time = startOfDate(this.year(), 0, 1);
                break;
            case 'quarter':
                time = startOfDate(
                    this.year(),
                    this.month() - (this.month() % 3),
                    1
                );
                break;
            case 'month':
                time = startOfDate(this.year(), this.month(), 1);
                break;
            case 'week':
                time = startOfDate(
                    this.year(),
                    this.month(),
                    this.date() - this.weekday()
                );
                break;
            case 'isoWeek':
                time = startOfDate(
                    this.year(),
                    this.month(),
                    this.date() - (this.isoWeekday() - 1)
                );
                break;
            case 'day':
            case 'date':
                time = startOfDate(this.year(), this.month(), this.date());
                break;
            case 'hour':
                time = this._d.valueOf();
                time -= mod$1(
                    time + (this._isUTC ? 0 : this.utcOffset() * MS_PER_MINUTE),
                    MS_PER_HOUR
                );
                break;
            case 'minute':
                time = this._d.valueOf();
                time -= mod$1(time, MS_PER_MINUTE);
                break;
            case 'second':
                time = this._d.valueOf();
                time -= mod$1(time, MS_PER_SECOND);
                break;
        }

        this._d.setTime(time);
        hooks.updateOffset(this, true);
        return this;
    }

    function endOf(units) {
        var time, startOfDate;
        units = normalizeUnits(units);
        if (units === undefined || units === 'millisecond' || !this.isValid()) {
            return this;
        }

        startOfDate = this._isUTC ? utcStartOfDate : localStartOfDate;

        switch (units) {
            case 'year':
                time = startOfDate(this.year() + 1, 0, 1) - 1;
                break;
            case 'quarter':
                time =
                    startOfDate(
                        this.year(),
                        this.month() - (this.month() % 3) + 3,
                        1
                    ) - 1;
                break;
            case 'month':
                time = startOfDate(this.year(), this.month() + 1, 1) - 1;
                break;
            case 'week':
                time =
                    startOfDate(
                        this.year(),
                        this.month(),
                        this.date() - this.weekday() + 7
                    ) - 1;
                break;
            case 'isoWeek':
                time =
                    startOfDate(
                        this.year(),
                        this.month(),
                        this.date() - (this.isoWeekday() - 1) + 7
                    ) - 1;
                break;
            case 'day':
            case 'date':
                time = startOfDate(this.year(), this.month(), this.date() + 1) - 1;
                break;
            case 'hour':
                time = this._d.valueOf();
                time +=
                    MS_PER_HOUR -
                    mod$1(
                        time + (this._isUTC ? 0 : this.utcOffset() * MS_PER_MINUTE),
                        MS_PER_HOUR
                    ) -
                    1;
                break;
            case 'minute':
                time = this._d.valueOf();
                time += MS_PER_MINUTE - mod$1(time, MS_PER_MINUTE) - 1;
                break;
            case 'second':
                time = this._d.valueOf();
                time += MS_PER_SECOND - mod$1(time, MS_PER_SECOND) - 1;
                break;
        }

        this._d.setTime(time);
        hooks.updateOffset(this, true);
        return this;
    }

    function valueOf() {
        return this._d.valueOf() - (this._offset || 0) * 60000;
    }

    function unix() {
        return Math.floor(this.valueOf() / 1000);
    }

    function toDate() {
        return new Date(this.valueOf());
    }

    function toArray() {
        var m = this;
        return [
            m.year(),
            m.month(),
            m.date(),
            m.hour(),
            m.minute(),
            m.second(),
            m.millisecond(),
        ];
    }

    function toObject() {
        var m = this;
        return {
            years: m.year(),
            months: m.month(),
            date: m.date(),
            hours: m.hours(),
            minutes: m.minutes(),
            seconds: m.seconds(),
            milliseconds: m.milliseconds(),
        };
    }

    function toJSON() {
        // new Date(NaN).toJSON() === null
        return this.isValid() ? this.toISOString() : null;
    }

    function isValid$2() {
        return isValid(this);
    }

    function parsingFlags() {
        return extend({}, getParsingFlags(this));
    }

    function invalidAt() {
        return getParsingFlags(this).overflow;
    }

    function creationData() {
        return {
            input: this._i,
            format: this._f,
            locale: this._locale,
            isUTC: this._isUTC,
            strict: this._strict,
        };
    }

    addFormatToken('N', 0, 0, 'eraAbbr');
    addFormatToken('NN', 0, 0, 'eraAbbr');
    addFormatToken('NNN', 0, 0, 'eraAbbr');
    addFormatToken('NNNN', 0, 0, 'eraName');
    addFormatToken('NNNNN', 0, 0, 'eraNarrow');

    addFormatToken('y', ['y', 1], 'yo', 'eraYear');
    addFormatToken('y', ['yy', 2], 0, 'eraYear');
    addFormatToken('y', ['yyy', 3], 0, 'eraYear');
    addFormatToken('y', ['yyyy', 4], 0, 'eraYear');

    addRegexToken('N', matchEraAbbr);
    addRegexToken('NN', matchEraAbbr);
    addRegexToken('NNN', matchEraAbbr);
    addRegexToken('NNNN', matchEraName);
    addRegexToken('NNNNN', matchEraNarrow);

    addParseToken(
        ['N', 'NN', 'NNN', 'NNNN', 'NNNNN'],
        function (input, array, config, token) {
            var era = config._locale.erasParse(input, token, config._strict);
            if (era) {
                getParsingFlags(config).era = era;
            } else {
                getParsingFlags(config).invalidEra = input;
            }
        }
    );

    addRegexToken('y', matchUnsigned);
    addRegexToken('yy', matchUnsigned);
    addRegexToken('yyy', matchUnsigned);
    addRegexToken('yyyy', matchUnsigned);
    addRegexToken('yo', matchEraYearOrdinal);

    addParseToken(['y', 'yy', 'yyy', 'yyyy'], YEAR);
    addParseToken(['yo'], function (input, array, config, token) {
        var match;
        if (config._locale._eraYearOrdinalRegex) {
            match = input.match(config._locale._eraYearOrdinalRegex);
        }

        if (config._locale.eraYearOrdinalParse) {
            array[YEAR] = config._locale.eraYearOrdinalParse(input, match);
        } else {
            array[YEAR] = parseInt(input, 10);
        }
    });

    function localeEras(m, format) {
        var i,
            l,
            date,
            eras = this._eras || getLocale('en')._eras;
        for (i = 0, l = eras.length; i < l; ++i) {
            switch (typeof eras[i].since) {
                case 'string':
                    // truncate time
                    date = hooks(eras[i].since).startOf('day');
                    eras[i].since = date.valueOf();
                    break;
            }

            switch (typeof eras[i].until) {
                case 'undefined':
                    eras[i].until = +Infinity;
                    break;
                case 'string':
                    // truncate time
                    date = hooks(eras[i].until).startOf('day').valueOf();
                    eras[i].until = date.valueOf();
                    break;
            }
        }
        return eras;
    }

    function localeErasParse(eraName, format, strict) {
        var i,
            l,
            eras = this.eras(),
            name,
            abbr,
            narrow;
        eraName = eraName.toUpperCase();

        for (i = 0, l = eras.length; i < l; ++i) {
            name = eras[i].name.toUpperCase();
            abbr = eras[i].abbr.toUpperCase();
            narrow = eras[i].narrow.toUpperCase();

            if (strict) {
                switch (format) {
                    case 'N':
                    case 'NN':
                    case 'NNN':
                        if (abbr === eraName) {
                            return eras[i];
                        }
                        break;

                    case 'NNNN':
                        if (name === eraName) {
                            return eras[i];
                        }
                        break;

                    case 'NNNNN':
                        if (narrow === eraName) {
                            return eras[i];
                        }
                        break;
                }
            } else if ([name, abbr, narrow].indexOf(eraName) >= 0) {
                return eras[i];
            }
        }
    }

    function localeErasConvertYear(era, year) {
        var dir = era.since <= era.until ? +1 : -1;
        if (year === undefined) {
            return hooks(era.since).year();
        } else {
            return hooks(era.since).year() + (year - era.offset) * dir;
        }
    }

    function getEraName() {
        var i,
            l,
            val,
            eras = this.localeData().eras();
        for (i = 0, l = eras.length; i < l; ++i) {
            // truncate time
            val = this.clone().startOf('day').valueOf();

            if (eras[i].since <= val && val <= eras[i].until) {
                return eras[i].name;
            }
            if (eras[i].until <= val && val <= eras[i].since) {
                return eras[i].name;
            }
        }

        return '';
    }

    function getEraNarrow() {
        var i,
            l,
            val,
            eras = this.localeData().eras();
        for (i = 0, l = eras.length; i < l; ++i) {
            // truncate time
            val = this.clone().startOf('day').valueOf();

            if (eras[i].since <= val && val <= eras[i].until) {
                return eras[i].narrow;
            }
            if (eras[i].until <= val && val <= eras[i].since) {
                return eras[i].narrow;
            }
        }

        return '';
    }

    function getEraAbbr() {
        var i,
            l,
            val,
            eras = this.localeData().eras();
        for (i = 0, l = eras.length; i < l; ++i) {
            // truncate time
            val = this.clone().startOf('day').valueOf();

            if (eras[i].since <= val && val <= eras[i].until) {
                return eras[i].abbr;
            }
            if (eras[i].until <= val && val <= eras[i].since) {
                return eras[i].abbr;
            }
        }

        return '';
    }

    function getEraYear() {
        var i,
            l,
            dir,
            val,
            eras = this.localeData().eras();
        for (i = 0, l = eras.length; i < l; ++i) {
            dir = eras[i].since <= eras[i].until ? +1 : -1;

            // truncate time
            val = this.clone().startOf('day').valueOf();

            if (
                (eras[i].since <= val && val <= eras[i].until) ||
                (eras[i].until <= val && val <= eras[i].since)
            ) {
                return (
                    (this.year() - hooks(eras[i].since).year()) * dir +
                    eras[i].offset
                );
            }
        }

        return this.year();
    }

    function erasNameRegex(isStrict) {
        if (!hasOwnProp(this, '_erasNameRegex')) {
            computeErasParse.call(this);
        }
        return isStrict ? this._erasNameRegex : this._erasRegex;
    }

    function erasAbbrRegex(isStrict) {
        if (!hasOwnProp(this, '_erasAbbrRegex')) {
            computeErasParse.call(this);
        }
        return isStrict ? this._erasAbbrRegex : this._erasRegex;
    }

    function erasNarrowRegex(isStrict) {
        if (!hasOwnProp(this, '_erasNarrowRegex')) {
            computeErasParse.call(this);
        }
        return isStrict ? this._erasNarrowRegex : this._erasRegex;
    }

    function matchEraAbbr(isStrict, locale) {
        return locale.erasAbbrRegex(isStrict);
    }

    function matchEraName(isStrict, locale) {
        return locale.erasNameRegex(isStrict);
    }

    function matchEraNarrow(isStrict, locale) {
        return locale.erasNarrowRegex(isStrict);
    }

    function matchEraYearOrdinal(isStrict, locale) {
        return locale._eraYearOrdinalRegex || matchUnsigned;
    }

    function computeErasParse() {
        var abbrPieces = [],
            namePieces = [],
            narrowPieces = [],
            mixedPieces = [],
            i,
            l,
            erasName,
            erasAbbr,
            erasNarrow,
            eras = this.eras();

        for (i = 0, l = eras.length; i < l; ++i) {
            erasName = regexEscape(eras[i].name);
            erasAbbr = regexEscape(eras[i].abbr);
            erasNarrow = regexEscape(eras[i].narrow);

            namePieces.push(erasName);
            abbrPieces.push(erasAbbr);
            narrowPieces.push(erasNarrow);
            mixedPieces.push(erasName);
            mixedPieces.push(erasAbbr);
            mixedPieces.push(erasNarrow);
        }

        this._erasRegex = new RegExp('^(' + mixedPieces.join('|') + ')', 'i');
        this._erasNameRegex = new RegExp('^(' + namePieces.join('|') + ')', 'i');
        this._erasAbbrRegex = new RegExp('^(' + abbrPieces.join('|') + ')', 'i');
        this._erasNarrowRegex = new RegExp(
            '^(' + narrowPieces.join('|') + ')',
            'i'
        );
    }

    // FORMATTING

    addFormatToken(0, ['gg', 2], 0, function () {
        return this.weekYear() % 100;
    });

    addFormatToken(0, ['GG', 2], 0, function () {
        return this.isoWeekYear() % 100;
    });

    function addWeekYearFormatToken(token, getter) {
        addFormatToken(0, [token, token.length], 0, getter);
    }

    addWeekYearFormatToken('gggg', 'weekYear');
    addWeekYearFormatToken('ggggg', 'weekYear');
    addWeekYearFormatToken('GGGG', 'isoWeekYear');
    addWeekYearFormatToken('GGGGG', 'isoWeekYear');

    // ALIASES

    // PARSING

    addRegexToken('G', matchSigned);
    addRegexToken('g', matchSigned);
    addRegexToken('GG', match1to2, match2);
    addRegexToken('gg', match1to2, match2);
    addRegexToken('GGGG', match1to4, match4);
    addRegexToken('gggg', match1to4, match4);
    addRegexToken('GGGGG', match1to6, match6);
    addRegexToken('ggggg', match1to6, match6);

    addWeekParseToken(
        ['gggg', 'ggggg', 'GGGG', 'GGGGG'],
        function (input, week, config, token) {
            week[token.substr(0, 2)] = toInt(input);
        }
    );

    addWeekParseToken(['gg', 'GG'], function (input, week, config, token) {
        week[token] = hooks.parseTwoDigitYear(input);
    });

    // MOMENTS

    function getSetWeekYear(input) {
        return getSetWeekYearHelper.call(
            this,
            input,
            this.week(),
            this.weekday() + this.localeData()._week.dow,
            this.localeData()._week.dow,
            this.localeData()._week.doy
        );
    }

    function getSetISOWeekYear(input) {
        return getSetWeekYearHelper.call(
            this,
            input,
            this.isoWeek(),
            this.isoWeekday(),
            1,
            4
        );
    }

    function getISOWeeksInYear() {
        return weeksInYear(this.year(), 1, 4);
    }

    function getISOWeeksInISOWeekYear() {
        return weeksInYear(this.isoWeekYear(), 1, 4);
    }

    function getWeeksInYear() {
        var weekInfo = this.localeData()._week;
        return weeksInYear(this.year(), weekInfo.dow, weekInfo.doy);
    }

    function getWeeksInWeekYear() {
        var weekInfo = this.localeData()._week;
        return weeksInYear(this.weekYear(), weekInfo.dow, weekInfo.doy);
    }

    function getSetWeekYearHelper(input, week, weekday, dow, doy) {
        var weeksTarget;
        if (input == null) {
            return weekOfYear(this, dow, doy).year;
        } else {
            weeksTarget = weeksInYear(input, dow, doy);
            if (week > weeksTarget) {
                week = weeksTarget;
            }
            return setWeekAll.call(this, input, week, weekday, dow, doy);
        }
    }

    function setWeekAll(weekYear, week, weekday, dow, doy) {
        var dayOfYearData = dayOfYearFromWeeks(weekYear, week, weekday, dow, doy),
            date = createUTCDate(dayOfYearData.year, 0, dayOfYearData.dayOfYear);

        this.year(date.getUTCFullYear());
        this.month(date.getUTCMonth());
        this.date(date.getUTCDate());
        return this;
    }

    // FORMATTING

    addFormatToken('Q', 0, 'Qo', 'quarter');

    // PARSING

    addRegexToken('Q', match1);
    addParseToken('Q', function (input, array) {
        array[MONTH] = (toInt(input) - 1) * 3;
    });

    // MOMENTS

    function getSetQuarter(input) {
        return input == null
            ? Math.ceil((this.month() + 1) / 3)
            : this.month((input - 1) * 3 + (this.month() % 3));
    }

    // FORMATTING

    addFormatToken('D', ['DD', 2], 'Do', 'date');

    // PARSING

    addRegexToken('D', match1to2, match1to2NoLeadingZero);
    addRegexToken('DD', match1to2, match2);
    addRegexToken('Do', function (isStrict, locale) {
        // TODO: Remove "ordinalParse" fallback in next major release.
        return isStrict
            ? locale._dayOfMonthOrdinalParse || locale._ordinalParse
            : locale._dayOfMonthOrdinalParseLenient;
    });

    addParseToken(['D', 'DD'], DATE);
    addParseToken('Do', function (input, array) {
        array[DATE] = toInt(input.match(match1to2)[0]);
    });

    // MOMENTS

    var getSetDayOfMonth = makeGetSet('Date', true);

    // FORMATTING

    addFormatToken('DDD', ['DDDD', 3], 'DDDo', 'dayOfYear');

    // PARSING

    addRegexToken('DDD', match1to3);
    addRegexToken('DDDD', match3);
    addParseToken(['DDD', 'DDDD'], function (input, array, config) {
        config._dayOfYear = toInt(input);
    });

    // HELPERS

    // MOMENTS

    function getSetDayOfYear(input) {
        var dayOfYear =
            Math.round(
                (this.clone().startOf('day') - this.clone().startOf('year')) / 864e5
            ) + 1;
        return input == null ? dayOfYear : this.add(input - dayOfYear, 'd');
    }

    // FORMATTING

    addFormatToken('m', ['mm', 2], 0, 'minute');

    // PARSING

    addRegexToken('m', match1to2, match1to2HasZero);
    addRegexToken('mm', match1to2, match2);
    addParseToken(['m', 'mm'], MINUTE);

    // MOMENTS

    var getSetMinute = makeGetSet('Minutes', false);

    // FORMATTING

    addFormatToken('s', ['ss', 2], 0, 'second');

    // PARSING

    addRegexToken('s', match1to2, match1to2HasZero);
    addRegexToken('ss', match1to2, match2);
    addParseToken(['s', 'ss'], SECOND);

    // MOMENTS

    var getSetSecond = makeGetSet('Seconds', false);

    // FORMATTING

    addFormatToken('S', 0, 0, function () {
        return ~~(this.millisecond() / 100);
    });

    addFormatToken(0, ['SS', 2], 0, function () {
        return ~~(this.millisecond() / 10);
    });

    addFormatToken(0, ['SSS', 3], 0, 'millisecond');
    addFormatToken(0, ['SSSS', 4], 0, function () {
        return this.millisecond() * 10;
    });
    addFormatToken(0, ['SSSSS', 5], 0, function () {
        return this.millisecond() * 100;
    });
    addFormatToken(0, ['SSSSSS', 6], 0, function () {
        return this.millisecond() * 1000;
    });
    addFormatToken(0, ['SSSSSSS', 7], 0, function () {
        return this.millisecond() * 10000;
    });
    addFormatToken(0, ['SSSSSSSS', 8], 0, function () {
        return this.millisecond() * 100000;
    });
    addFormatToken(0, ['SSSSSSSSS', 9], 0, function () {
        return this.millisecond() * 1000000;
    });

    // PARSING

    addRegexToken('S', match1to3, match1);
    addRegexToken('SS', match1to3, match2);
    addRegexToken('SSS', match1to3, match3);

    var token, getSetMillisecond;
    for (token = 'SSSS'; token.length <= 9; token += 'S') {
        addRegexToken(token, matchUnsigned);
    }

    function parseMs(input, array) {
        array[MILLISECOND] = toInt(('0.' + input) * 1000);
    }

    for (token = 'S'; token.length <= 9; token += 'S') {
        addParseToken(token, parseMs);
    }

    getSetMillisecond = makeGetSet('Milliseconds', false);

    // FORMATTING

    addFormatToken('z', 0, 0, 'zoneAbbr');
    addFormatToken('zz', 0, 0, 'zoneName');

    // MOMENTS

    function getZoneAbbr() {
        return this._isUTC ? 'UTC' : '';
    }

    function getZoneName() {
        return this._isUTC ? 'Coordinated Universal Time' : '';
    }

    var proto = Moment.prototype;

    proto.add = add;
    proto.calendar = calendar$1;
    proto.clone = clone;
    proto.diff = diff;
    proto.endOf = endOf;
    proto.format = format;
    proto.from = from;
    proto.fromNow = fromNow;
    proto.to = to;
    proto.toNow = toNow;
    proto.get = stringGet;
    proto.invalidAt = invalidAt;
    proto.isAfter = isAfter;
    proto.isBefore = isBefore;
    proto.isBetween = isBetween;
    proto.isSame = isSame;
    proto.isSameOrAfter = isSameOrAfter;
    proto.isSameOrBefore = isSameOrBefore;
    proto.isValid = isValid$2;
    proto.lang = lang;
    proto.locale = locale;
    proto.localeData = localeData;
    proto.max = prototypeMax;
    proto.min = prototypeMin;
    proto.parsingFlags = parsingFlags;
    proto.set = stringSet;
    proto.startOf = startOf;
    proto.subtract = subtract;
    proto.toArray = toArray;
    proto.toObject = toObject;
    proto.toDate = toDate;
    proto.toISOString = toISOString;
    proto.inspect = inspect;
    if (typeof Symbol !== 'undefined' && Symbol.for != null) {
        proto[Symbol.for('nodejs.util.inspect.custom')] = function () {
            return 'Moment<' + this.format() + '>';
        };
    }
    proto.toJSON = toJSON;
    proto.toString = toString;
    proto.unix = unix;
    proto.valueOf = valueOf;
    proto.creationData = creationData;
    proto.eraName = getEraName;
    proto.eraNarrow = getEraNarrow;
    proto.eraAbbr = getEraAbbr;
    proto.eraYear = getEraYear;
    proto.year = getSetYear;
    proto.isLeapYear = getIsLeapYear;
    proto.weekYear = getSetWeekYear;
    proto.isoWeekYear = getSetISOWeekYear;
    proto.quarter = proto.quarters = getSetQuarter;
    proto.month = getSetMonth;
    proto.daysInMonth = getDaysInMonth;
    proto.week = proto.weeks = getSetWeek;
    proto.isoWeek = proto.isoWeeks = getSetISOWeek;
    proto.weeksInYear = getWeeksInYear;
    proto.weeksInWeekYear = getWeeksInWeekYear;
    proto.isoWeeksInYear = getISOWeeksInYear;
    proto.isoWeeksInISOWeekYear = getISOWeeksInISOWeekYear;
    proto.date = getSetDayOfMonth;
    proto.day = proto.days = getSetDayOfWeek;
    proto.weekday = getSetLocaleDayOfWeek;
    proto.isoWeekday = getSetISODayOfWeek;
    proto.dayOfYear = getSetDayOfYear;
    proto.hour = proto.hours = getSetHour;
    proto.minute = proto.minutes = getSetMinute;
    proto.second = proto.seconds = getSetSecond;
    proto.millisecond = proto.milliseconds = getSetMillisecond;
    proto.utcOffset = getSetOffset;
    proto.utc = setOffsetToUTC;
    proto.local = setOffsetToLocal;
    proto.parseZone = setOffsetToParsedOffset;
    proto.hasAlignedHourOffset = hasAlignedHourOffset;
    proto.isDST = isDaylightSavingTime;
    proto.isLocal = isLocal;
    proto.isUtcOffset = isUtcOffset;
    proto.isUtc = isUtc;
    proto.isUTC = isUtc;
    proto.zoneAbbr = getZoneAbbr;
    proto.zoneName = getZoneName;
    proto.dates = deprecate(
        'dates accessor is deprecated. Use date instead.',
        getSetDayOfMonth
    );
    proto.months = deprecate(
        'months accessor is deprecated. Use month instead',
        getSetMonth
    );
    proto.years = deprecate(
        'years accessor is deprecated. Use year instead',
        getSetYear
    );
    proto.zone = deprecate(
        'moment().zone is deprecated, use moment().utcOffset instead. http://momentjs.com/guides/#/warnings/zone/',
        getSetZone
    );
    proto.isDSTShifted = deprecate(
        'isDSTShifted is deprecated. See http://momentjs.com/guides/#/warnings/dst-shifted/ for more information',
        isDaylightSavingTimeShifted
    );

    function createUnix(input) {
        return createLocal(input * 1000);
    }

    function createInZone() {
        return createLocal.apply(null, arguments).parseZone();
    }

    function preParsePostFormat(string) {
        return string;
    }

    var proto$1 = Locale.prototype;

    proto$1.calendar = calendar;
    proto$1.longDateFormat = longDateFormat;
    proto$1.invalidDate = invalidDate;
    proto$1.ordinal = ordinal;
    proto$1.preparse = preParsePostFormat;
    proto$1.postformat = preParsePostFormat;
    proto$1.relativeTime = relativeTime;
    proto$1.pastFuture = pastFuture;
    proto$1.set = set;
    proto$1.eras = localeEras;
    proto$1.erasParse = localeErasParse;
    proto$1.erasConvertYear = localeErasConvertYear;
    proto$1.erasAbbrRegex = erasAbbrRegex;
    proto$1.erasNameRegex = erasNameRegex;
    proto$1.erasNarrowRegex = erasNarrowRegex;

    proto$1.months = localeMonths;
    proto$1.monthsShort = localeMonthsShort;
    proto$1.monthsParse = localeMonthsParse;
    proto$1.monthsRegex = monthsRegex;
    proto$1.monthsShortRegex = monthsShortRegex;
    proto$1.week = localeWeek;
    proto$1.firstDayOfYear = localeFirstDayOfYear;
    proto$1.firstDayOfWeek = localeFirstDayOfWeek;

    proto$1.weekdays = localeWeekdays;
    proto$1.weekdaysMin = localeWeekdaysMin;
    proto$1.weekdaysShort = localeWeekdaysShort;
    proto$1.weekdaysParse = localeWeekdaysParse;

    proto$1.weekdaysRegex = weekdaysRegex;
    proto$1.weekdaysShortRegex = weekdaysShortRegex;
    proto$1.weekdaysMinRegex = weekdaysMinRegex;

    proto$1.isPM = localeIsPM;
    proto$1.meridiem = localeMeridiem;

    function get$1(format, index, field, setter) {
        var locale = getLocale(),
            utc = createUTC().set(setter, index);
        return locale[field](utc, format);
    }

    function listMonthsImpl(format, index, field) {
        if (isNumber(format)) {
            index = format;
            format = undefined;
        }

        format = format || '';

        if (index != null) {
            return get$1(format, index, field, 'month');
        }

        var i,
            out = [];
        for (i = 0; i < 12; i++) {
            out[i] = get$1(format, i, field, 'month');
        }
        return out;
    }

    // ()
    // (5)
    // (fmt, 5)
    // (fmt)
    // (true)
    // (true, 5)
    // (true, fmt, 5)
    // (true, fmt)
    function listWeekdaysImpl(localeSorted, format, index, field) {
        if (typeof localeSorted === 'boolean') {
            if (isNumber(format)) {
                index = format;
                format = undefined;
            }

            format = format || '';
        } else {
            format = localeSorted;
            index = format;
            localeSorted = false;

            if (isNumber(format)) {
                index = format;
                format = undefined;
            }

            format = format || '';
        }

        var locale = getLocale(),
            shift = localeSorted ? locale._week.dow : 0,
            i,
            out = [];

        if (index != null) {
            return get$1(format, (index + shift) % 7, field, 'day');
        }

        for (i = 0; i < 7; i++) {
            out[i] = get$1(format, (i + shift) % 7, field, 'day');
        }
        return out;
    }

    function listMonths(format, index) {
        return listMonthsImpl(format, index, 'months');
    }

    function listMonthsShort(format, index) {
        return listMonthsImpl(format, index, 'monthsShort');
    }

    function listWeekdays(localeSorted, format, index) {
        return listWeekdaysImpl(localeSorted, format, index, 'weekdays');
    }

    function listWeekdaysShort(localeSorted, format, index) {
        return listWeekdaysImpl(localeSorted, format, index, 'weekdaysShort');
    }

    function listWeekdaysMin(localeSorted, format, index) {
        return listWeekdaysImpl(localeSorted, format, index, 'weekdaysMin');
    }

    getSetGlobalLocale('en', {
        eras: [
            {
                since: '0001-01-01',
                until: +Infinity,
                offset: 1,
                name: 'Anno Domini',
                narrow: 'AD',
                abbr: 'AD',
            },
            {
                since: '0000-12-31',
                until: -Infinity,
                offset: 1,
                name: 'Before Christ',
                narrow: 'BC',
                abbr: 'BC',
            },
        ],
        dayOfMonthOrdinalParse: /\d{1,2}(th|st|nd|rd)/,
        ordinal: function (number) {
            var b = number % 10,
                output =
                    toInt((number % 100) / 10) === 1
                        ? 'th'
                        : b === 1
                          ? 'st'
                          : b === 2
                            ? 'nd'
                            : b === 3
                              ? 'rd'
                              : 'th';
            return number + output;
        },
    });

    // Side effect imports

    hooks.lang = deprecate(
        'moment.lang is deprecated. Use moment.locale instead.',
        getSetGlobalLocale
    );
    hooks.langData = deprecate(
        'moment.langData is deprecated. Use moment.localeData instead.',
        getLocale
    );

    var mathAbs = Math.abs;

    function abs() {
        var data = this._data;

        this._milliseconds = mathAbs(this._milliseconds);
        this._days = mathAbs(this._days);
        this._months = mathAbs(this._months);

        data.milliseconds = mathAbs(data.milliseconds);
        data.seconds = mathAbs(data.seconds);
        data.minutes = mathAbs(data.minutes);
        data.hours = mathAbs(data.hours);
        data.months = mathAbs(data.months);
        data.years = mathAbs(data.years);

        return this;
    }

    function addSubtract$1(duration, input, value, direction) {
        var other = createDuration(input, value);

        duration._milliseconds += direction * other._milliseconds;
        duration._days += direction * other._days;
        duration._months += direction * other._months;

        return duration._bubble();
    }

    // supports only 2.0-style add(1, 's') or add(duration)
    function add$1(input, value) {
        return addSubtract$1(this, input, value, 1);
    }

    // supports only 2.0-style subtract(1, 's') or subtract(duration)
    function subtract$1(input, value) {
        return addSubtract$1(this, input, value, -1);
    }

    function absCeil(number) {
        if (number < 0) {
            return Math.floor(number);
        } else {
            return Math.ceil(number);
        }
    }

    function bubble() {
        var milliseconds = this._milliseconds,
            days = this._days,
            months = this._months,
            data = this._data,
            seconds,
            minutes,
            hours,
            years,
            monthsFromDays;

        // if we have a mix of positive and negative values, bubble down first
        // check: https://github.com/moment/moment/issues/2166
        if (
            !(
                (milliseconds >= 0 && days >= 0 && months >= 0) ||
                (milliseconds <= 0 && days <= 0 && months <= 0)
            )
        ) {
            milliseconds += absCeil(monthsToDays(months) + days) * 864e5;
            days = 0;
            months = 0;
        }

        // The following code bubbles up values, see the tests for
        // examples of what that means.
        data.milliseconds = milliseconds % 1000;

        seconds = absFloor(milliseconds / 1000);
        data.seconds = seconds % 60;

        minutes = absFloor(seconds / 60);
        data.minutes = minutes % 60;

        hours = absFloor(minutes / 60);
        data.hours = hours % 24;

        days += absFloor(hours / 24);

        // convert days to months
        monthsFromDays = absFloor(daysToMonths(days));
        months += monthsFromDays;
        days -= absCeil(monthsToDays(monthsFromDays));

        // 12 months -> 1 year
        years = absFloor(months / 12);
        months %= 12;

        data.days = days;
        data.months = months;
        data.years = years;

        return this;
    }

    function daysToMonths(days) {
        // 400 years have 146097 days (taking into account leap year rules)
        // 400 years have 12 months === 4800
        return (days * 4800) / 146097;
    }

    function monthsToDays(months) {
        // the reverse of daysToMonths
        return (months * 146097) / 4800;
    }

    function as(units) {
        if (!this.isValid()) {
            return NaN;
        }
        var days,
            months,
            milliseconds = this._milliseconds;

        units = normalizeUnits(units);

        if (units === 'month' || units === 'quarter' || units === 'year') {
            days = this._days + milliseconds / 864e5;
            months = this._months + daysToMonths(days);
            switch (units) {
                case 'month':
                    return months;
                case 'quarter':
                    return months / 3;
                case 'year':
                    return months / 12;
            }
        } else {
            // handle milliseconds separately because of floating point math errors (issue #1867)
            days = this._days + Math.round(monthsToDays(this._months));
            switch (units) {
                case 'week':
                    return days / 7 + milliseconds / 6048e5;
                case 'day':
                    return days + milliseconds / 864e5;
                case 'hour':
                    return days * 24 + milliseconds / 36e5;
                case 'minute':
                    return days * 1440 + milliseconds / 6e4;
                case 'second':
                    return days * 86400 + milliseconds / 1000;
                // Math.floor prevents floating point math errors here
                case 'millisecond':
                    return Math.floor(days * 864e5) + milliseconds;
                default:
                    throw new Error('Unknown unit ' + units);
            }
        }
    }

    function makeAs(alias) {
        return function () {
            return this.as(alias);
        };
    }

    var asMilliseconds = makeAs('ms'),
        asSeconds = makeAs('s'),
        asMinutes = makeAs('m'),
        asHours = makeAs('h'),
        asDays = makeAs('d'),
        asWeeks = makeAs('w'),
        asMonths = makeAs('M'),
        asQuarters = makeAs('Q'),
        asYears = makeAs('y'),
        valueOf$1 = asMilliseconds;

    function clone$1() {
        return createDuration(this);
    }

    function get$2(units) {
        units = normalizeUnits(units);
        return this.isValid() ? this[units + 's']() : NaN;
    }

    function makeGetter(name) {
        return function () {
            return this.isValid() ? this._data[name] : NaN;
        };
    }

    var milliseconds = makeGetter('milliseconds'),
        seconds = makeGetter('seconds'),
        minutes = makeGetter('minutes'),
        hours = makeGetter('hours'),
        days = makeGetter('days'),
        months = makeGetter('months'),
        years = makeGetter('years');

    function weeks() {
        return absFloor(this.days() / 7);
    }

    var round = Math.round,
        thresholds = {
            ss: 44, // a few seconds to seconds
            s: 45, // seconds to minute
            m: 45, // minutes to hour
            h: 22, // hours to day
            d: 26, // days to month/week
            w: null, // weeks to month
            M: 11, // months to year
        };

    // helper function for moment.fn.from, moment.fn.fromNow, and moment.duration.fn.humanize
    function substituteTimeAgo(string, number, withoutSuffix, isFuture, locale) {
        return locale.relativeTime(number || 1, !!withoutSuffix, string, isFuture);
    }

    function relativeTime$1(posNegDuration, withoutSuffix, thresholds, locale) {
        var duration = createDuration(posNegDuration).abs(),
            seconds = round(duration.as('s')),
            minutes = round(duration.as('m')),
            hours = round(duration.as('h')),
            days = round(duration.as('d')),
            months = round(duration.as('M')),
            weeks = round(duration.as('w')),
            years = round(duration.as('y')),
            a =
                (seconds <= thresholds.ss && ['s', seconds]) ||
                (seconds < thresholds.s && ['ss', seconds]) ||
                (minutes <= 1 && ['m']) ||
                (minutes < thresholds.m && ['mm', minutes]) ||
                (hours <= 1 && ['h']) ||
                (hours < thresholds.h && ['hh', hours]) ||
                (days <= 1 && ['d']) ||
                (days < thresholds.d && ['dd', days]);

        if (thresholds.w != null) {
            a =
                a ||
                (weeks <= 1 && ['w']) ||
                (weeks < thresholds.w && ['ww', weeks]);
        }
        a = a ||
            (months <= 1 && ['M']) ||
            (months < thresholds.M && ['MM', months]) ||
            (years <= 1 && ['y']) || ['yy', years];

        a[2] = withoutSuffix;
        a[3] = +posNegDuration > 0;
        a[4] = locale;
        return substituteTimeAgo.apply(null, a);
    }

    // This function allows you to set the rounding function for relative time strings
    function getSetRelativeTimeRounding(roundingFunction) {
        if (roundingFunction === undefined) {
            return round;
        }
        if (typeof roundingFunction === 'function') {
            round = roundingFunction;
            return true;
        }
        return false;
    }

    // This function allows you to set a threshold for relative time strings
    function getSetRelativeTimeThreshold(threshold, limit) {
        if (thresholds[threshold] === undefined) {
            return false;
        }
        if (limit === undefined) {
            return thresholds[threshold];
        }
        thresholds[threshold] = limit;
        if (threshold === 's') {
            thresholds.ss = limit - 1;
        }
        return true;
    }

    function humanize(argWithSuffix, argThresholds) {
        if (!this.isValid()) {
            return this.localeData().invalidDate();
        }

        var withSuffix = false,
            th = thresholds,
            locale,
            output;

        if (typeof argWithSuffix === 'object') {
            argThresholds = argWithSuffix;
            argWithSuffix = false;
        }
        if (typeof argWithSuffix === 'boolean') {
            withSuffix = argWithSuffix;
        }
        if (typeof argThresholds === 'object') {
            th = Object.assign({}, thresholds, argThresholds);
            if (argThresholds.s != null && argThresholds.ss == null) {
                th.ss = argThresholds.s - 1;
            }
        }

        locale = this.localeData();
        output = relativeTime$1(this, !withSuffix, th, locale);

        if (withSuffix) {
            output = locale.pastFuture(+this, output);
        }

        return locale.postformat(output);
    }

    var abs$1 = Math.abs;

    function sign(x) {
        return (x > 0) - (x < 0) || +x;
    }

    function toISOString$1() {
        // for ISO strings we do not use the normal bubbling rules:
        //  * milliseconds bubble up until they become hours
        //  * days do not bubble at all
        //  * months bubble up until they become years
        // This is because there is no context-free conversion between hours and days
        // (think of clock changes)
        // and also not between days and months (28-31 days per month)
        if (!this.isValid()) {
            return this.localeData().invalidDate();
        }

        var seconds = abs$1(this._milliseconds) / 1000,
            days = abs$1(this._days),
            months = abs$1(this._months),
            minutes,
            hours,
            years,
            s,
            total = this.asSeconds(),
            totalSign,
            ymSign,
            daysSign,
            hmsSign;

        if (!total) {
            // this is the same as C#'s (Noda) and python (isodate)...
            // but not other JS (goog.date)
            return 'P0D';
        }

        // 3600 seconds -> 60 minutes -> 1 hour
        minutes = absFloor(seconds / 60);
        hours = absFloor(minutes / 60);
        seconds %= 60;
        minutes %= 60;

        // 12 months -> 1 year
        years = absFloor(months / 12);
        months %= 12;

        // inspired by https://github.com/dordille/moment-isoduration/blob/master/moment.isoduration.js
        s = seconds ? seconds.toFixed(3).replace(/\.?0+$/, '') : '';

        totalSign = total < 0 ? '-' : '';
        ymSign = sign(this._months) !== sign(total) ? '-' : '';
        daysSign = sign(this._days) !== sign(total) ? '-' : '';
        hmsSign = sign(this._milliseconds) !== sign(total) ? '-' : '';

        return (
            totalSign +
            'P' +
            (years ? ymSign + years + 'Y' : '') +
            (months ? ymSign + months + 'M' : '') +
            (days ? daysSign + days + 'D' : '') +
            (hours || minutes || seconds ? 'T' : '') +
            (hours ? hmsSign + hours + 'H' : '') +
            (minutes ? hmsSign + minutes + 'M' : '') +
            (seconds ? hmsSign + s + 'S' : '')
        );
    }

    var proto$2 = Duration.prototype;

    proto$2.isValid = isValid$1;
    proto$2.abs = abs;
    proto$2.add = add$1;
    proto$2.subtract = subtract$1;
    proto$2.as = as;
    proto$2.asMilliseconds = asMilliseconds;
    proto$2.asSeconds = asSeconds;
    proto$2.asMinutes = asMinutes;
    proto$2.asHours = asHours;
    proto$2.asDays = asDays;
    proto$2.asWeeks = asWeeks;
    proto$2.asMonths = asMonths;
    proto$2.asQuarters = asQuarters;
    proto$2.asYears = asYears;
    proto$2.valueOf = valueOf$1;
    proto$2._bubble = bubble;
    proto$2.clone = clone$1;
    proto$2.get = get$2;
    proto$2.milliseconds = milliseconds;
    proto$2.seconds = seconds;
    proto$2.minutes = minutes;
    proto$2.hours = hours;
    proto$2.days = days;
    proto$2.weeks = weeks;
    proto$2.months = months;
    proto$2.years = years;
    proto$2.humanize = humanize;
    proto$2.toISOString = toISOString$1;
    proto$2.toString = toISOString$1;
    proto$2.toJSON = toISOString$1;
    proto$2.locale = locale;
    proto$2.localeData = localeData;

    proto$2.toIsoString = deprecate(
        'toIsoString() is deprecated. Please use toISOString() instead (notice the capitals)',
        toISOString$1
    );
    proto$2.lang = lang;

    // FORMATTING

    addFormatToken('X', 0, 0, 'unix');
    addFormatToken('x', 0, 0, 'valueOf');

    // PARSING

    addRegexToken('x', matchSigned);
    addRegexToken('X', matchTimestamp);
    addParseToken('X', function (input, array, config) {
        config._d = new Date(parseFloat(input) * 1000);
    });
    addParseToken('x', function (input, array, config) {
        config._d = new Date(toInt(input));
    });

    //! moment.js

    hooks.version = '2.30.1';

    setHookCallback(createLocal);

    hooks.fn = proto;
    hooks.min = min;
    hooks.max = max;
    hooks.now = now;
    hooks.utc = createUTC;
    hooks.unix = createUnix;
    hooks.months = listMonths;
    hooks.isDate = isDate;
    hooks.locale = getSetGlobalLocale;
    hooks.invalid = createInvalid;
    hooks.duration = createDuration;
    hooks.isMoment = isMoment;
    hooks.weekdays = listWeekdays;
    hooks.parseZone = createInZone;
    hooks.localeData = getLocale;
    hooks.isDuration = isDuration;
    hooks.monthsShort = listMonthsShort;
    hooks.weekdaysMin = listWeekdaysMin;
    hooks.defineLocale = defineLocale;
    hooks.updateLocale = updateLocale;
    hooks.locales = listLocales;
    hooks.weekdaysShort = listWeekdaysShort;
    hooks.normalizeUnits = normalizeUnits;
    hooks.relativeTimeRounding = getSetRelativeTimeRounding;
    hooks.relativeTimeThreshold = getSetRelativeTimeThreshold;
    hooks.calendarFormat = getCalendarFormat;
    hooks.prototype = proto;

    // currently HTML5 input type only supports 24-hour formats
    hooks.HTML5_FMT = {
        DATETIME_LOCAL: 'YYYY-MM-DDTHH:mm', // <input type="datetime-local" />
        DATETIME_LOCAL_SECONDS: 'YYYY-MM-DDTHH:mm:ss', // <input type="datetime-local" step="1" />
        DATETIME_LOCAL_MS: 'YYYY-MM-DDTHH:mm:ss.SSS', // <input type="datetime-local" step="0.001" />
        DATE: 'YYYY-MM-DD', // <input type="date" />
        TIME: 'HH:mm', // <input type="time" />
        TIME_SECONDS: 'HH:mm:ss', // <input type="time" step="1" />
        TIME_MS: 'HH:mm:ss.SSS', // <input type="time" step="0.001" />
        WEEK: 'GGGG-[W]WW', // <input type="week" />
        MONTH: 'YYYY-MM', // <input type="month" />
    };

    return hooks;

})));

},{}]},{},[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]);
