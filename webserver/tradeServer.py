
from flask import Flask, request
import numpy as np
from tradeDllApi import Tradedll
from accountConfig import *
import json
import pandas as pd

app = Flask(__name__)



@app.route('/connect', methods=["POST"])
def connect():
    accountId = request.json["accountId"]
    accountCfg = getAccountConfig(accountId)
    resp= {"rc":-1, "accountId":accountId, "clientId": -1, "errMessage":""}
    #
    if accountCfg:
        tradeApi = getTradeApiInstance(accountId)
        if tradeApi:
            print("Trade API instance has been created for account %s" %accountId)
        else:
            # create trade api instance for account Id
            tradeApi = Tradedll(accountCfg)
            accountToTradeApiInst[accountId] = tradeApi
            tradeApi.connect()
            accountCfg["clientId"] = tradeApi.clientId

        resp["clientId"] = tradeApi.clientId
        resp["rc"] = 0
    else:
        resp["rc"] = -1
        resp["errMessage"] = "Account Id is not configured at Trade Server"

    return json.dumps(resp)


@app.route("/position", methods=["POST"])
def position():
    accountId = request.json["accountId"]
    tradeApi = getTradeApiInstance(accountId)
    df = tradeApi.queryPosition()
    return df.to_json()

@app.route("/account", methods=["POST"])
def account():
    accountId = request.json["accountId"]
    tradeApi = getTradeApiInstance(accountId)

    resp = {"rc": -1, "accountId": accountId, "accountDf": "", "errMessage": ""}

    rc, accountDf = tradeApi.queryAccountMoney()
    resp["rc"] = rc
    if rc == 0:
        resp["accountDf"] = accountDf.to_json()
    else:
        resp["errMessage"] = accountDf
    return json.dumps(resp)


@app.route("/sendorder", methods=["POST"])
def sendOrder():
    accountId = request.json["accountId"]
    symbol = request.json["symbol"]
    tradeDirection = request.json["tradeDirection"]
    price = request.json["price"]
    volume = request.json["volume"]
    tradeApi = getTradeApiInstance(accountId)

    resp = {"rc": -1, "accountId": accountId, "orderId":-1, "errMessage": ""}

    orderId, errorMsg = tradeApi.sendOrder(tradeDirection, symbol, price, volume)
    if orderId != tradeApi.INVALID_ORDER_ID:
        resp["rc"] = 0
    else:
        resp["rc"] = -1
        resp["errMessage"] = errorMsg

    resp["orderId"] = orderId
    return json.dumps(resp)

@app.route("/cancelorder", methods=["POST"])
def cancelOrder():
    accountId = request.json["accountId"]
    symbol = request.json["symbol"]
    orderId = request.json["orderId"]
    tradeApi = getTradeApiInstance(accountId)

    resp = {"rc": -1, "accountId": accountId, "orderId":-1, "errMessage": ""}

    rc, message = tradeApi.cancelOrder(orderId, symbol)

    resp["rc"] = rc
    resp["orderId"] = orderId
    resp["errMessage"] = message

    return json.dumps(resp)

@app.route("/queryOrderState", methods=["POST"])
def queryOrderState():
    accountId = request.json["accountId"]
    symbol = request.json["symbol"]
    orderId = request.json["orderId"]
    tradeApi = getTradeApiInstance(accountId)

    resp = {"rc": -1, "state":"submit", "accountId": accountId, "orderId": -1, "errMessage": ""}

    orderDf = tradeApi.queryTodayOrder()


    resp["orderId"] = orderId
    resp["rc"] = 0
    resp["state"] = "XXXX"
    return json.dumps(resp)

@app.route("/queryOrder", methods=["POST"])
def queryOrder():
    accountId = request.json["accountId"]
    tradeApi = getTradeApiInstance(accountId)

    resp = {"rc": -1, "accountId": accountId, "orderDf": "", "errMessage": ""}

    rc, orderDf = tradeApi.queryTodayOrder()
    resp["rc"] = rc
    if rc == 0:
        resp["orderDf"] = orderDf.to_json()
    else:
        resp["errMessage"] = orderDf
    return json.dumps(resp)

@app.route("/queryTrade", methods=["POST"])
def queryTrade():
    accountId = request.json["accountId"]
    tradeApi = getTradeApiInstance(accountId)
    ignoreApply = request.json["ignoreApply"]

    resp = {"rc": -1, "accountId": accountId, "tradeDf": "{}", "errMessage": ""}

    rc, tradeDf = tradeApi.queryTodayTrade(ignoreApply)
    resp["rc"] = rc
    if rc == 0:
        resp["tradeDf"] = tradeDf.to_json()
    else:
        resp["errMessage"] = tradeDf
    return json.dumps(resp)

@app.route("/queryHistoryTrade", methods=["POST"])
def queryHistoryTrade():
    accountId = request.json["accountId"]
    tradeApi = getTradeApiInstance(accountId)

    startDate = request.json["startDate"]
    endDate = request.json["endDate"]
    ignoreApply = request.json["ignoreApply"]

    resp = {"rc": -1, "accountId": accountId, "historyTradeDf": "{}", "errMessage": ""}

    rc, tradeDf = tradeApi.queryHistoryTrade(startDate, endDate, ignoreApply)
    resp["rc"] = rc
    if rc == 0:
        resp["historyTradeDf"] = tradeDf.to_json()
    else:
        resp["errMessage"] = tradeDf
    return json.dumps(resp)

if __name__ == "__main__":
    app.run()