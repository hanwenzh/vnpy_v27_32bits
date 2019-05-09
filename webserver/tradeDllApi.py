# encoding: utf-8
from ctypes import *
import string
import ctypes
import pandas as pd
import numpy as np

class Tradedll(object):

    INVALID_CLIENT_ID = -1
    DIRECTION_BUY = "BUY"
    DIRECTION_SELL = "SELL"
    PRICE_TYPE = 0 # 两市限价单   报价方式 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格  2(市价委托)深圳本方最优价格
    INVALID_ORDER_ID = -1

    def __init__(self, config):

        self.Objdll = None
        self.clientId = self.INVALID_CLIENT_ID
        self.dllName = config["dllName"]

        self.gddmSH = config["gddmSH"]
        self.gddmSZ = config["gddmSZ"]

    def allocateBuf(self, resSize=1024*512, errSize=1024):
        pRes = c_char_p()
        pRes.value = "0" * resSize
        pErr = c_char_p()
        pErr.value = "0" * errSize
        
        return pRes, pErr

    def toGBK(self,str):
        return str.decode("gbk")

    #获取str中line行col列的数据
    def getField(self,str, line, col):
        lines = str.split('\n')
        cols= lines[line].split('\t')
        return cols[col]

    # 拆解api返回的信息成 二维数组
    def getData(self,str):
        lines = str.split('\n')
        arr=[]
        for line in lines:
            cols = line.split('\t')
            arr.append(cols)
        return arr

    def getGddm(self,symbol):
        if symbol[:1] == "6":
            return self.gddmSH
        else:
            return self.gddmSZ

    #撤单 exchangeID: 1:上海  深圳：0
    def getExchangeId(self,symbol):
        if symbol[:1] == "6":
            return "1"
        else:
            return "0"

    def connect(self):
        self.Objdll = ctypes.windll.LoadLibrary(self.dllName)
        self.Objdll.OpenTdx()

        user_info = np.loadtxt('user_info.txt', dtype=str, delimiter=',')
        self.clientId = self.login(user_info[0], user_info[1], user_info[2], user_info[3], user_info[4],
                                  user_info[5], user_info[6], user_info[7])

    #登录
    def login(self,ip, port, version, yybID, accountNo, tradeAccount, jyPassword, txPassword):
        """
        登录程序
        :param
        ip: 券商交易服务器IP
        port：券商交易服务器端口
        version：设置通达信客户端的版本号
        yybID：营业部代码
        accountNo：完整的登录账号
        tradeAccount：交易账号
        jyPassword：交易密码
        txPassword：通讯密码
        :return: clientId:返回结果 0通过 -1失败
        """
        
        pRes, pErr = self.allocateBuf()
        
        port=string.atoi(port)
        yybID=string.atoi(yybID)
        clientId = self.Objdll.Logon(c_char_p(ip), c_short(port), c_char_p(version), yybID, c_char_p(accountNo), c_char_p(tradeAccount),
                                c_char_p(jyPassword), c_char_p(txPassword), pErr)

        print(self.toGBK(pErr.value))
        return clientId


    # 查询账户信息数据  category： 0：0资金  1持仓   2当日委托  3当日成交  4可撤单
    def queryAccountMoney(self):
        pRes, pErr = self.allocateBuf()
        
        self.Objdll.QueryData(self.clientId, 0, pRes, pErr)
        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))

        # 没有错误信息则表示成功
        if not pErr.value:
            str1 = self.toGBK(pRes.value)
            if str1=="":
                arr=[]
            else:
                arr = self.getData(str1)
            colList = ['currencyType', 'balance', 'avaMoney', 'freezedMoney', 'withdrawMoney',
                       'totalAsset', 'marketValue', 'luckyAmount', 'data1', 'data2', 'reserve1']
            df = pd.DataFrame(arr[1:], columns=colList)
            # df = pd.DataFrame(arr,columns=['币种', '资金余额', '可用资金', '冻结资金', '可取资金',
            #               '总资产', '最新市值', '中签金额', '操作数据', '句柄', '保留信息'])
            return 0, df
        else:
            return -1, self.toGBK(pErr.value)

    def queryTodayOrder(self):
        pRes, pErr = self.allocateBuf()

        self.Objdll.QueryData(self.clientId, 2, pRes, pErr)

        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))

        # 没有错误信息则表示成功
        if not pErr.value:
            str1 = self.toGBK(pRes.value)
            if str1=="":
                arr=[]
            else:
                arr = self.getData(str1)
            colList = ['time','symbol','name', 'buyOrSellFlag', 'flagName', 'orderType', 'orderState', 'orderPrice', 'orderVolume',
                       'orderId', 'tradePrice', 'tradeVolume', 'cancelVolume', 'entrustType', 'quoteType', 'gddm',
                       'accountType','exchangeId','reserve1']
            df = pd.DataFrame(arr[1:], columns=colList)
            return 0, df
        else:
            return -1, self.toGBK(pErr.value)


    # 查询持仓信息数据
    def queryPosition(self):
        pRes, pErr = self.allocateBuf()

        self.Objdll.QueryData(0, 1, pRes, pErr)
        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))
        str1 = self.toGBK(pRes.value)
        colList = ['symbol','name','totalVol', 'canSellVol', 'currentVol', 'costPrice', 'currentPrice', 'totalValue',
                   'profit', 'profitPct', 'gddm', 'todayInVol', 'todayOutVol', 'zhlb', 'exchangeCode', 'delistDate',
                   'reserve1']
        returnColList = []
        if str1=="":
            df = pd.DataFrame()
        else:
            arr = self.getData(str1)
            df = pd.DataFrame(arr[1:], columns=colList)
        # df = pd.DataFrame(arr,columns=['证券代码', '证券名称', '证券数量', '可卖数量', '当前数量',
        #               '参考成本价', '当前价', '最新市值', '参考盈亏', '参考盈亏比例(%)', '股东代码',
        #               '当日买入数量', '当日卖出数量', '帐号类别', '交易所代码', '退市日期', '保留信息'])
        # df.columns = ['code', 'name', 'total_number', 'avail_number', 'hold_number',
        #               'cost', 'last_price', 'latest_market_value', 'change', 'change_ratio', 'gddm',
        #               'day_buy', 'day_sell', 'account_type', 'exchange_code', 'delisting_date', 'retain_info']
        return df

    #查询当日委托
    def query_delegate(self):
        pRes, pErr = self.allocateBuf()

        self.Objdll.QueryData(0, 2, pRes, pErr)
        str1 = self.toGBK(pRes.value)
        if str1=="":
            arr=[]
        else:
            arr = self.getData(str1)
        df = pd.DataFrame(arr,columns=['委托时间', '证券代码', '证券名称', '买卖标志', '买卖标志', '委托类别',
                      '状态说明 ', '委托价格', '委托数量', '委托编号', '成交价格', '成交数量',
                      '撤单数量', '委托方式', '报价方式', '股东代码', '帐号类别', '交易所代码', '保留信息'])
        # df.columns = ['entrust_time', 'code', 'name', 'business_logo_int', 'business_logo_str', 'entrust_category',
        #               'state ', 'entrust_price', 'entrust_amount', 'entrust_number', 'deal_price', 'deal_amount', 'revoke_amount',
        #               'entrust_way', 'offer_way', 'gddm', 'account_type', 'exchange_code', 'retain_info']
        return df

    # 查询当日成交
    def queryTodayTrade(self,ignoreApply):
        pRes, pErr = self.allocateBuf()

        self.Objdll.QueryData(self.clientId, 3, pRes, pErr)
        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))

        # 没有错误信息则表示成功
        if not pErr.value:
            str1 = self.toGBK(pRes.value)
            if str1=="":
                arr=[]
            else:
                arr = self.getData(str1)
            colList = ['time','symbol','name', 'buyOrSellFlag', 'flagName', 'tradePrice', 'tradeVolume', 'tradeMoney',
                       'tradeId', 'orderId', 'gddm', 'accountType','reserve1']
            df = pd.DataFrame(arr[1:], columns=colList)
            return 0, df
        else:
            return -1, self.toGBK(pErr.value)

    # 查询历史成交
    def queryHistoryTrade(self, startDate, endDate, ignoreApply):
        pRes, pErr = self.allocateBuf()

        # startDate and endDate's formate:  yyyyMMdd
        self.Objdll.QueryHistoryData(self.clientId, 1, c_char_p(startDate), c_char_p(endDate), pRes, pErr)
        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))

        # 没有错误信息则表示成功
        if not pErr.value:
            str1 = self.toGBK(pRes.value)
            if str1=="":
                arr=[]
            else:
                arr = self.getData(str1)
            colList = ['date','time','symbol','name', 'buyOrSellFlag', 'flagName', 'tradePrice', 'tradeVolume',
                       'tradeId', 'orderId', 'gddm', 'accountType','tradeMoney',
                       'commission', 'tax', 'transferFee','otherFee', 'comment', 'transactionFee','reserve1']
            returnedCols = ['date','time','symbol','name', 'buyOrSellFlag', 'flagName', 'tradePrice', 'tradeVolume',
                       'tradeMoney', 'gddm', 'accountType',
                       'commission', 'tax', 'transferFee','otherFee','transactionFee']
            df = pd.DataFrame(arr[1:], columns=colList)
            if ignoreApply:
                # 去掉申购记录
                df = df[returnedCols][df["flagName"] != u"申购配号"].reset_index(drop=True)
            else:
                df = df[returnedCols]
            return 0, df
        else:
            return -1, self.toGBK(pErr.value)


    #查询可撤单
    def query_revoke(self):
        pRes, pErr = self.allocateBuf()

        self.Objdll.QueryData(0, 4, pRes, pErr)
        str1 = self.toGBK(pRes.value)
        if str1 =="":
            arr=[]
        else:
            arr = self.getData(str1)
        df = pd.DataFrame(arr,columns=['委托时间', '证券代码', '证券名称', '买卖标志', '买卖标志', '委托类别',
                      '状态说明', '委托价格', '委托数量', '委托编号', '成交价格', '成交数量',
                      '委托方式', '报价方式', '股东代码', '帐号类别', '交易所代码', '保留信息'])
        # columns = ['entrust_time', 'code', 'name', 'business_logo_int', 'business_logo_str', 'entrust_category',
        #            'state', 'entrust_price', 'entrust_amount', 'entrust_number', 'deal_price', 'deal_amount',
        #            'entrust_way', 'offer_way', 'gddm', 'account_type', 'exchange_code', 'retain_info']
        return df

    def sendOrder(self, direction, symbol, price, quantity):
        orderPrice = c_float()
        orderPrice.value = price
        gddm = self.getGddm(symbol)
        if direction == self.DIRECTION_BUY:
            apiDirection = 0
        elif direction == self.DIRECTION_SELL:
            apiDirection = 1

        pRes, pErr = self.allocateBuf()

        self.Objdll.SendOrder(self.clientId, apiDirection, self.PRICE_TYPE, c_char_p(gddm),
                              c_char_p(symbol), orderPrice, quantity, pRes, pErr)

        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))

        # 没有错误信息则表示成功
        if not pErr.value:
            str1 = self.toGBK(pRes.value)
            orderId = self.getField(str1, 1, 0)
        else:
            orderId = self.INVALID_ORDER_ID

        return orderId, self.toGBK(pErr.value)

    def cancelOrder(self,orderId,symbol):
        # 撤单 exchangeID: 1:上海  深圳：0
        exchangeID = self.getExchangeId(symbol)

        pRes, pErr = self.allocateBuf()

        self.Objdll.CancelOrder(self.clientId, c_char_p(exchangeID), c_char_p(orderId), pRes, pErr)
        print(self.toGBK(pRes.value))
        print(self.toGBK(pErr.value))

        # 没有错误信息则表示成功
        if not pErr.value:
            return 0, ""
        else:
            return -1, self.toGBK(pErr.value)

    #注销
    def Logoff(self):
        if self.clientId != self.INVALID_CLIENT_ID:
            self.Objdll.Logoff(self.clientId)

    #关闭
    def CloseTdx(self):
        if self.Objdll:
            self.Objdll.CloseTdx()


