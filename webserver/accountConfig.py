

accountToTradeApiInst = {}

accountConfig= \
    {"20155562":
         {"dllName":"trade.dll", "gddmSH":"A271677010", "gddmSZ":"0246288098", "clientId": -1},
     "XXXXX":
         {}
     }


def getAccountConfig(accountId):
    if accountId in accountConfig:
        return accountConfig[accountId]
    else:
        return None


def getTradeApiInstance(accountId):
    if accountId in accountToTradeApiInst:
        return accountToTradeApiInst[accountId]
    else:
        return None

def releaseTradeApiInstance(accountId):
    if accountId in accountToTradeApiInst:
        del accountToTradeApiInst[accountId]