# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import pandas as pd

class stock_quote(object):

    field_index = {
        'code':0,
        'data_date':1,
        'data_time':2,
        'last_price':3,
        'open_price':4,
        'high_price':5,
        'low_price':6,
        'prev_close_price':7,
        'volume':8,
        'turnover':9,
        'turnover_rate':10,
        'amplitude':11,
        'suspension':12,
        'listing_date':13,
        'price_spread':14,
        'dark_status': 15,
        'strike_price': 16,
        'contract_size': 17,
        'open_interest': 18,
        'implied_volatility': 19,
        'premium': 20,
        'delta': 21,
        'gamma': 22,
        'vega': 23,
        'theta': 24,
        'rho': 25,


    }

    field_count = len(field_index)

    def __init__(self):
        self.quote_list = []
        self.highest_price = 0

    def __str__(self):
        return self.quote_list.__str__()

    def append_quote(self, new_quote):
        assert len(new_quote) == stock_quote.field_count

        # 是否需要维护最高价？
        #self.highest_price = new_quote[stock_quote.field_index['high_price']]
        self.quote_list.append(new_quote)

    def get_highest_price(self):
        return self.highest_price

    def get_quote_df(self):
        return pd.DataFrame(self.quote_list)

    def get_latest_quote_info(self):
        latest_quote = self.quote_list[-1]
        code = latest_quote[stock_quote.field_index['code']]
        last_price = latest_quote[stock_quote.field_index['last_price']]
        high_price = latest_quote[stock_quote.field_index['high_price']]
        data_time = latest_quote[stock_quote.field_index['data_time']]
        prev_close_price = latest_quote[stock_quote.field_index['prev_close_price']]
        return code, last_price, high_price, data_time, prev_close_price


    def get_previous_quote_info(self):
        quote = self.quote_list[-2]
        last_price = quote[stock_quote.field_index['last_price']]
        data_time = quote[stock_quote.field_index['data_time']]
        return last_price, data_time

    def get_lowest_price_within_interval(self,time_str):
        #quote_list的所有quote信息都是按照时间推送过来，所以纪录是按照时间递增排序的
        #根据传入的time_str找到所有比time_str时间晚的报价信息，并且找到其中的最低价格

        #遍历报价列表，找到指定日期的切片
        total_index = len(self.quote_list) - 1
        attempt_index = total_index -1
        lowest_price = 9999
        while attempt_index >= 0:
            quote = self.quote_list[attempt_index]
            last_price = quote[stock_quote.field_index['last_price']]
            data_time = quote[stock_quote.field_index['data_time']]

            lowest_price = min(last_price, lowest_price)
            if data_time < time_str:
                break
            attempt_index = attempt_index - 1

        #quote_slice = self.quote_list[attempt_index:total_index]
        return lowest_price


    def __len__(self):
        return len(self.quote_list)