# encoding: utf-8
from ctypes import *
import string
import ctypes
import pandas as pd

def toGBK(str):
    return str.decode("gbk")

#获取str中line行col列的数据
def getField(str, line, col):
    lines = str.split('\n')
    cols= lines[line].split('\t')
    return cols[col]

#登录
def login(Ip, Port, Version, YybID, AccountNo, TradeAccount, JyPassword, TxPassword):
    Port=string.atoi(Port)
    YybID=string.atoi(YybID)
    clientId = Objdll.Logon(c_char_p(Ip),c_short(Port),c_char_p(Version),YybID,c_char_p(AccountNo),c_char_p(TradeAccount),
                            c_char_p(JyPassword),c_char_p(TxPassword),pErr)
    return clientId



# 查询账户信息数据
def queryData(clientId, category):
    df = pd.DataFrame()
    Objdll.QueryData(clientId, category, pRes, pErr)
    str1 = toGBK(pRes.value)
    if category==0:
        df.loc[0, '币种'] = getField(str1, 1, 0)
        df.loc[0, '资金余额'] = getField(str1, 1, 1)
        df.loc[0, '可用资金'] = getField(str1, 1, 2)
        df.loc[0, '冻结资金'] = getField(str1, 1, 3)
        df.loc[0, '可取资金'] = getField(str1, 1, 4)
        df.loc[0, '总资产'] = getField(str1, 1, 5)
    return df

#下单
def Order(ClientId, Category, PriceType, Gddm, Zqdm, Price, Quantity):
    price = c_float()
    price.value = Price
    Objdll.SendOrder(ClientId, Category, PriceType, c_char_p(Gddm), c_char_p(Zqdm), price, Quantity, pRes, pErr)
    str1 = toGBK(pRes.value)
    err=toGBK(pErr.value)

    if str1=='':
        return err
    else:
        orderId = getField(str1, 1, 0)
        return orderId

#撤单
def CancelOrder(ClientId, ExchangeID, OrderId):
    Objdll.CancelOrder(ClientId, c_char_p(ExchangeID), OrderId, pRes, pErr)
    result=pRes.value


#注销
def Logoff(ClientId):
    Objdll.Logoff(ClientId)

#关闭
def CloseTdx():
    Objdll.CloseTdx()


Objdll = ctypes.windll.LoadLibrary("trade.dll")
Objdll.OpenTdx()
#定义
buferr = ' ' * 1024
pErr = c_char_p()
pErr.value = buferr
bufres = ' ' * 1024*512
pRes = c_char_p()
pRes.value = bufres