# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from futuquant import *
import trade_dll_api as tda
from stock_quote import *
import numpy as np


MPLITUDE_RADIO=0.05     #与涨停的振幅比例
BUY_RADIO=0.08     #与涨停的振幅比例,跌了BUY_RADIO进行买入
SELL_NUMBER=100     #卖出数量
BUY_NUMBER=100 #买出数量
SZ_GDDM="0246288098"  #深圳股东代码
SH_GDDM="A271677010"  #上海股东代码

# 已经卖过的股票
sold_stock = []
# 已经买过的股票
bought_stock=[]

tradeState = 1  # 1等待开板卖   2开板后上穿买   3等待再次封板  4再次开板后卖
lowestPriceAfterBreaking = 999 # 第一次开板后最低价
breakConfirm = 0.005 # 开板确认幅度0.5%，跌多少认为开板
upConfirm = 0.02 # 开板后再次买入的反弹确认涨幅2%， 反弹多少认为又要封板了
tVolume = 100  # 做t用的仓位100股， 根据不同账号的情况来设置买卖交易量，  每次买卖都是相同的数量。

all_data_df=pd.DataFrame(columns = ["code", "last_price", "data_time", "now_data_time"])
def already_sold(code):
    return code in sold_stock

def mark_stock_sold(code):
    sold_stock.append(code)

def already_bought(code):
    return code in bought_stock

def mark_stock_bought(code):
    bought_stock.append(code)


def run_catch_open_stratage(clientId,quote):
    # 至少有2条报价信息再进行判断
    #if len(quote) < 2:
    #    return
    code, last_price, high_price, data_time, prev_close_price = quote.get_latest_quote_info()
    harden_price=round(prev_close_price *1.1,2)  #涨停
    fall_price=round(prev_close_price *0.9,2)  #跌停
    # 已经卖过就不再卖，进入判断是否可以买的阶段

    if already_sold(code):
        catch_buy(clientId, code, last_price, harden_price, prev_close_price)
        return
    if last_price > round(prev_close_price * (1.1 - MPLITUDE_RADIO), 2):
    #if last_price <round(prev_close_price * (1.1 - MPLITUDE_RADIO), 2):
        if code[:2] == "SZ":  # 深圳股东代码
            gddm = SZ_GDDM
        elif code[:2] == 'SH':  # 上海股东代码
            gddm = SH_GDDM
        #下单
        re = tda.Order(clientId, 1, 0, gddm, code[3:], harden_price, SELL_NUMBER)
        #re=tda.Order(clientId, 1, 1, gddm, code[3:], fall_price, SELL_NUMBER)
        print "--",re
        mark_stock_sold(code)

def catch_buy(clientId,code,last_price, harden_price,prev_close_price):
    if already_bought(code):
        return
    if last_price < round(prev_close_price * (1.1 - BUY_RADIO), 2):
        if code[:2] == "SZ":  # 深圳股东代码
            gddm = SZ_GDDM
        elif code[:2] == 'SH':  # 上海股东代码
            gddm = SH_GDDM
            # 下单
        re = tda.Order(clientId, 0, 0, gddm, code[3:], harden_price, BUY_NUMBER)
        print re
        mark_stock_bought(code)



def sell_buy_sell(clientId,quote):

    global tradeState  # 1等待开板卖   2开板后上穿买   3等待再次封板  4再次开板后卖
    global lowestPriceAfterBreaking # 第一次开板后最低价
    re = 0

    code, last_price, high_price, data_time, prev_close_price = quote.get_latest_quote_info()
    harden_price=round(prev_close_price *1.1,2)  #涨停
    fall_price=round(prev_close_price *0.9,2)  #跌停
    breakConfirmPrice = round(prev_close_price * (1.1 - breakConfirm),2)
    upConfirmPrice = round((lowestPriceAfterBreaking + (prev_close_price * upConfirm)), 2)

    print("当前价格[%s] 涨停价[%s] 开板确认价[%s] 第一次开板后最低价[%s] 第一次开板后反弹确认[%s]" \
          %(last_price, harden_price, breakConfirmPrice, lowestPriceAfterBreaking, upConfirmPrice))

    if code[:2] == "SZ":  # 深圳股东代码
        gddm = SZ_GDDM
    elif code[:2] == 'SH': # 上海股东代码
        gddm = SH_GDDM

    if tradeState == 1:
        if last_price < breakConfirmPrice:
            # 开板挂跌停价卖出
            re = tda.Order(clientId, 1, 0, gddm, code[3:], fall_price, tVolume)
            print("触发第一次开板卖[%s] orderId[%s]" %(last_price,re))
            tradeState = 2
            lowestPriceAfterBreaking = last_price
    elif tradeState == 2:
        if last_price < lowestPriceAfterBreaking:
            lowestPriceAfterBreaking = last_price

        pre_price, date_time = quote.get_previous_quote_info()
        # 只在价格上升趋势时候才买, 并且价格<breakConfirmPrice(尽量留出空间保证买进来)
        if last_price > pre_price and last_price < breakConfirmPrice:
            upConfirmPrice = round((lowestPriceAfterBreaking + (prev_close_price * upConfirm)), 2)
            # 如果跌幅不足upConfirm， 则last_price 最大为涨停价，是不会出现 > upConfirmPrice 的情况的。
            if last_price > upConfirmPrice:
                # 开板后上穿买入
                re = tda.Order(clientId, 0, 0, gddm, code[3:], harden_price, tVolume)
                print("开板后上穿买入[%s] orderId[%s]" %(last_price,re))
                tradeState = 3
    elif tradeState == 3:
        # 等待再次封板
        if last_price == harden_price:
            tradeState = 4
    elif tradeState == 4:
        if last_price < breakConfirmPrice:
            # 二次开板挂跌停价卖出
            re = tda.Order(clientId, 1, 0, gddm, code[3:], fall_price, tVolume)
            print("触发第二次开板卖[%s] orderId[%s]" %(last_price,re))
            tradeState = 0

