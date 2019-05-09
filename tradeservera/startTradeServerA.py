import socket, select
import json
import pandas as pd
import numpy as np

refresh_interval = 60

f = None



def handle_request(data, addr=None):
    req_dict = json.loads(data)
    req_type = req_dict['req_type']

    switch_req = {
        "shake_hands": shake_hands,
        "query_account_info": query_account_info,
        "query_position": query_position,
        "buy": buy,
        "sell": sell,
        "cancel": cancel
    }

    result, close_or_keep = switch_req[req_type](req_dict, addr)
    return result, close_or_keep

def query_account_info(req_dict, addr):
    df = f.account_info()
    print df
    result = df.to_json(orient='split')
    print result
    return result, 'keep'

def shake_hands(req_dict,addr):
    hello_msg = req_dict['hello_msg']

    if hello_msg == 'This is zxw':
        return "welcome to WebTrader", "keep"
    else:
        return "Invalid connection", "close"


def query_position(req_dict, addr):
    df = f.account_position()
    print df
    result = df.to_json(orient='split')
    print result
    return result, "keep"

def buy(req_dict, addr):
    code = req_dict['stock_code']
    price = req_dict['price']
    volume = req_dict['volume']
    result = f.buy(code, price, volume)
    return result, "keep"


def sell(req_dict, addr):
    code = req_dict['stock_code']
    price = req_dict['price']
    volume = req_dict['volume']
    result = f.sell(code, price, volume)
    return result, "keep"

def cancel(req_dict,addr):
    list = req_dict["order_list"]
    order_list = ','.join(list)
    result = f.cancel_order(order_list)
    return 'Cancelled', "keep"

if __name__ == '__main__':


    s = socket.socket()
    host = "10.0.0.5"
    port = 9999
    s.bind((host,port))
    s.listen(5)

    inputs = [s]

    while True:
        rs, ws, es = select.select(inputs, [], [], refresh_interval)

        if not rs:
            print("select timeout, continue")
            print f.account_position()
            continue

        for r in rs:
            if r is s:
                c, addr = s.accept()
                print "got connection from", addr
                inputs.append(c)
            else:
                try:
                    data = r.recv(1024)
                    disconnected = not data
                except socket.error:
                    disconnected = True

                if disconnected:
                    print r.getpeername(), "disconnected"
                    inputs.remove(r)
                else:
                    print "received data:", data
                    result1, need_close = handle_request(data)
                    r.send(result1)
                    if need_close == 'close':
                        inputs.remove(r)
                        r.close()