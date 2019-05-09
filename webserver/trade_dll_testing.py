
# encoding: utf-8
import tradeDllApi as trade
import numpy as np
import pandas as pd
import time

def getField(str, line, col):
    lines = str.split('\n')
    cols= lines[line].split('\t')
    return cols[col]

ta=trade.Tradedll()

#获取登录账号信息
user_info = np.loadtxt('user_info.txt', dtype=str, delimiter=',')
#登录账户
clientId=ta.login(user_info[0],user_info[1],user_info[2],user_info[3],user_info[4],
                  user_info[5],user_info[6],user_info[7])
if clientId == 0:
    print "账户登录成功"
else:
    print "账户登录失败，请检查登录信息"
    exit()

#查询持仓数据
# query_result= ta.queryData(clientId, 1)
# print "11--",query_result.iloc[8]

#查询当日委托
# query_result= ta.queryData(clientId, 2)
#
# #查询当日成交


df=pd.DataFrame()
df= ta.query_revoke()
print df
po=ta.query_position()
print po
# orderid=ta.Order(clientId, 0, 0, "A271677010","601988", 0.05, 100)
# print "委托已提交，编号为%s" % orderid
#
# ta.CancelOrder(clientId,"1",orderid)
ta.Logoff(clientId)
ta.CloseTdx()


