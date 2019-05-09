# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from pandas import DataFrame
from futuquant import *
import futuquant as ft

from stock_quote import *
from catch_open_stratage import *




"""
错误退出，关闭行情接口
"""
def exit_on_error(ret_code,ret_data=''):
    trd_ctx.close()
    quote_ctx.close()
    print ret_data
    exit(ret_code)

"""
订阅相应股票的QUOTE事件
获取当前时间之前的N条股票QUOTE信息作为初始化数据
"""
def init_stock_quote_data(stock_list):
    for code in stock_list:
        ret_code, ret_data = quote_ctx.subscribe(code, ft.SubType.QUOTE)
        if ret_code != RET_OK:
            exit_on_error(ret_code,ret_data)
        #初始化报价列表
        quote_all[code] = stock_quote()


class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(StockQuoteTest,self).on_recv_rsp(rsp_str) # 基类的on_recv_rsp方法解包返回了报价信息，格式与get_stock_quote一样
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        stock_code = content.iloc[0]['code']
        list1 = list(content.iloc[0])
        quote_all[stock_code].append_quote(list1)
        # print "股票代码:%s 股票价格:%f 时间:%s 当前时间:%s" % (stock_code, content.iloc[0]['last_price'], content.iloc[0]['data_time'], datetime.datetime.now())

        #验证是否符合策略
        # run_catch_open_stratage(clientId,quote_all[stock_code])
        sell_buy_sell(clientId,quote_all[stock_code])
        return RET_OK, content


if __name__ == '__main__':

    ip = '127.0.0.1'
    port = 22221
    quote_all = {}
    tick_data = {}
    code = 'HK.00123'
    unlock_pwd = '887886'
    trd_env = ft.TrdEnv.SIMULATE
    order_type = ft.OrderType.SPECIAL_LIMIT

    quote_ctx = ft.OpenQuoteContext(ip, port)
    trd_ctx = ft.OpenHKTradeContext(ip, port)
    # 获取登录账号信息
    user_info = np.loadtxt('user_info.txt', dtype=str, delimiter=',')

    # 登录账户
    clientId = tda.login(user_info[0], user_info[1], user_info[2], user_info[3], user_info[4],
                         user_info[5], user_info[6], user_info[7])
    if clientId == 0:
        print "账户登录成功"
    else:
        print "账户登录失败，请检查登录信息"

    # data = xlrd.open_workbook('d:/monitor_harden.xlsx')
    # table = data.sheets()[1]#通过索引顺序获取
    # col=table.col_values(0);
    #
    # full_code_list=[]
    # for i in range(len(col)):
    #     if col[i] == "":
    #         continue
    #     col_each_value = col[i]
    #     market = col_each_value[-2:]
    #     code = col_each_value[0:6]
    #     full_code = market + '.' + code
    #     full_code_list.append(full_code)  # 整理股票代码，变成 SZ.xxxxxx格式

    """
    定义股票池
    """
    # d = {'code':full_code_list}
    # stock_priority = DataFrame(d)
    # stock_monitor_list = list(stock_priority['code'])
    stock_monitor_list=['SH.600150']
    """
    初始化quote数据
    """
    init_stock_quote_data(stock_monitor_list)


    if True:
        priceList = [
                   [u'SH.600150', u'2019-04-10', u'15:00:00', 27.02, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
                   0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 27.00, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 26.88, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 27.00, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 25.34, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 27.02, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 25.72, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 25.99, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 27.02, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 27.02, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [u'SH.600150', u'2019-04-10', u'15:00:00', 25.02, 27.02, 27.02, 27.02, 24.56, 1329369, 35919550.0,
             0.096, 0.0, False, u'1998-05-20', 0.01, 'N/A', 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
        # for i in range(10000):
        for price in priceList:
            quote_all['SH.600150'].append_quote(price)
            sell_buy_sell(clientId, quote_all['SH.600150'])
            time.sleep(2)

        print("Finish ------------------")
        exit(0)

    quote_ctx.set_handler(StockQuoteTest())
    quote_ctx.start()