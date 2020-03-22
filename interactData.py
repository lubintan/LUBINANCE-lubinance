import pytz,time
from datetime import datetime
from binance.client import Client
from binance.exceptions import *
import pandas as pd
import numpy as np
import decimal

# sK = 
# apiK = 

# All previous keys have previously been invalidated.
# Request new key from dashboard and paste above. Take care to not upload to github.
# TODO: Modify script to obtain keys from a separate file.



#region: triangle mkts
trgPairs = {}

# USDT BTC 41
trgPairs['USDTBTC'] = 'ETH','BNB','NEO','LTC','QTUM','ADA','XRP','EOS','IOTA','XLM','ONT','TRX','ETC','ICX','NULS','BCHABC','LINK','WAVES','ONG','ZIL','ZRX','FET','BAT','XMR','CELR','NANO','OMG','THETA','ENJ','MITH','MATIC','ATOM','TFUEL','FTM',

# USDT ETH 29
trgPairs['USDTETH'] = 'BNB','NEO','LTC','QTUM','ADA','XRP','EOS','IOTA','XLM','ONT','TRX','ETC','ICX','NULS','LINK','WAVES','ZIL','ZRX','BAT','XMR','NANO','OMG','THETA','ENJ',

# PAX BTC 22
trgPairs['PAXBTC'] = 'BNB','ETH','XRP','EOS','XLM','LINK','WAVES','BCHABC','LTC','TRX','BTT','ZEC','ADA','NEO','ATOM','ETC','BAT','PHB','TFUEL','ONE','FTM','BCPT',

# PAX ETH 14
trgPairs['PAXETH'] = 'BNB','XRP','EOS','XLM','LINK','WAVES','LTC','TRX','ZEC','ADA','NEO','ETC','BAT','BCPT',

# TUSD BTC 22
trgPairs['TUSDBTC'] = 'ETH','BNB','XRP','EOS','XLM','ADA','TRX','NEO','LINK','WAVES','BCHABC','LTC','BTT','ZEC','ATOM','ETC','BAT','PHB','TFUEL','ONE','FTM','BCPT',

# TUSD ETH 14
trgPairs['TUSDETH'] = 'BNB','XRP','EOS','XLM','ADA','TRX','NEO','LINK','WAVES','LTC','ZEC','ETC','BAT','BCPT',

# USDC BTC 22
trgPairs['USDCBTC'] = 'BNB','ETH','XRP','EOS','XLM','LINK','WAVES','BCHABC','LTC','TRX','BTT','ZEC','ADA','NEO','ATOM','ETC','BAT','PHB','TFUEL','ONE','FTM','BCPT',

# USDC ETH 14
trgPairs['USDCETH'] = 'BNB','XRP','EOS','XLM','LINK','WAVES','LTC','TRX','ZEC','ADA','NEO','ETC','BAT','BCPT',

#endregion


#region: PRECISION
precision={}
precision['BTC'] = [2,6]
precision['BNB'] = [4,2]
precision['LTC'] = [2,5]
precision['ETH'] = [2,5]
precision['XRP'] = [5,1]
precision['EOS'] = [4,2]
precision['ONE'] = [5,1]
precision['TRX'] = [5,1]
precision['BCHABC'] = [2,5]
precision['BTT'] = [7,0]
precision['MATIC'] = [5,1]
precision['ATOM'] = [3,3]
precision['NEO'] = [3,3]
precision['ZIL'] = [5,1]
precision['ADA'] = [5,1]
precision['FET'] = [4,2]
precision['ETC'] = [4,2]
precision['LINK'] = [4,2]
precision['IOTA'] = [4,2]
precision['CELR'] = [5,1]
precision['ONT'] = [4,2]
precision['XLM'] = [5,1]
precision['VET'] = [6,0]
precision['ICX'] = [4,2]
precision['TFUEL'] = [5,1]
precision['ZRX'] = [4,2]
precision['BAT'] = [4,2]
precision['HOT'] = [7,0]
precision['WAVES'] = [4,2]
precision['IOST'] = [6,0]
precision['QTUM'] = [3,3]
precision['NANO'] = [4,2]
precision['DASH'] = [2,5]
precision['ZEC'] = [2,5]
precision['ENJ'] = [5,1]
precision['OMG'] = [4,2]
precision['XMR'] = [2,5]
precision['NULS'] = [4,2]
precision['THETA'] = [5,1]
precision['MITH'] = [5,1]
precision['ONG'] = [4,2]
# 
# precision['ETHBTC'] = [6,3]
# precision['BNBBTC'] = [7,2]
# precision['NEOBTC'] = [6,2]
# precision['LTCBTC'] = [6,2]
# precision['QTUMBTC'] = [6,2]
# precision['ADABTC'] = [8,0]
# precision['XRPBTC'] = [8,0]
# precision['EOSBTC'] = [7,2]
# precision['IOTABTC'] = [8,0]
# precision['XLMBTC'] = [8,0]
# precision['ONTBTC'] = [7,2]
# precision['TRXBTC'] = [8,0]
# precision['ETCBTC'] = [6,2]
# precision['ICXBTC'] = [7,2]
# precision['NULSBTC'] = [8,0]
# precision['VETBTC'] = [8,0]
# precision['BCHABCBTC'] = [6,3]
# precision['LINKBTC'] = [8,0]
# precision['WAVESBTC'] = [7,2]
# precision['BTTBTC'] = [8,0]
# precision['ONGBTC'] = [8,0]
# precision['HOTBTC'] = [8,0]
# precision['ZILBTC'] = [8,0]
# precision['ZRXBTC'] = [8,0]
# precision['FETBTC'] = [8,0]
# precision['BATBTC'] = [8,0]
# precision['XMRBTC'] = [6,3]
# precision['ZECBTC'] = [6,3]
# precision['IOSTBTC'] = [8,0]
# precision['CELRBTC'] = [8,0]
# precision['DASHBTC'] = [6,3]
# precision['NANOBTC'] = [7,2]
# precision['OMGBTC'] = [6,2]
# precision['THETABTC'] = [8,0]
# precision['ENJBTC'] = [8,0]
# precision['MITHBTC'] = [8,0]
# precision['MATICBTC'] = [8,0]
# precision['ATOMBTC'] = [7,2]
# precision['TFUELBTC'] = [8,0]
# precision['ONEBTC'] = [8,0]
# precision['FTMBTC'] = [8,0]
# 
# precision['BNBETH'] = [6,2]
# precision['NEOETH'] = [6,2]
# precision['LTCETH'] = [5,3]
# precision['QTUMETH'] = [6,2]
# precision['ADAETH'] = [8,0]
# precision['XRPETH'] = [8,0]
# precision['EOSETH'] = [6,2]
# precision['IOTAETH'] = [8,0]
# precision['XLMETH'] = [8,0]
# precision['ONTETH'] = [6,2]
# precision['TRXETH'] = [8,0]
# precision['ETCETH'] = [6,2]
# precision['ICXETH'] = [6,2]
# precision['NULSETH'] = [8,0]
# precision['VETETH'] = [8,0]
# precision['LINKETH'] = [8,0]
# precision['WAVESETH'] = [6,2]
# precision['HOTETH'] = [8,0]
# precision['ZILETH'] = [8,0]
# precision['ZRXETH'] = [8,0]
# precision['BATETH'] = [8,0]
# precision['XMRETH'] = [5,3]
# precision['ZECETH'] = [5,3]
# precision['IOSTETH'] = [8,0]
# precision['DASHETH'] = [5,3]
# precision['NANOETH'] = [6,2]
# precision['OMGETH'] = [6,2]
# precision['THETAETH'] = [8,0]
# precision['ENJETH'] = [8,0]



#endregion

#region: PRECISION CODE
# coins = pd.read_csv('Binance_USDT_pairs.csv')
#
#             for i, r in coins.iterrows():
#
#                 coin = r.coin
#
#                 info = getPrecision(client,coin+'USDT')
#                 for each in info['filters']:
#                     if each['filterType'] == 'PRICE_FILTER':
#                         tickSize = float(each['tickSize'])
#                     if each['filterType'] == 'LOT_SIZE':
#                         stepSize = float(each['stepSize'])
#
#                 a = 0
#                 while tickSize!=1:
#                     tickSize = tickSize * 10
#                     a += 1
#
#                 b = 0
#                 while stepSize != 1:
#                     stepSize = stepSize * 10
#                     b += 1
#
#                 print("precision['" + coin + "'] = ["+str(a)+","+str(b)+"]")
#endregion

# region RATE LIMITS
# 'rateLimitType': 'ORDERS', 'interval': 'SECOND', 'intervalNum': 1, 'limit': 10
# every 0.1 s on avg
#
# 'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200
#  every 0.05 s on avg
#
# 'rateLimitType': 'ORDERS', 'interval': 'DAY', 'intervalNum': 1, 'limit': 100000
# every 1.2 s on avg
#
# endregion

def errorHandler(e,file):
    #send email

    utcNow = datetime.utcnow()
    nowNow = datetime.now()
    print(e)
    print('UTC:', utcNow, file=file)
    print('UTC+8:', nowNow, file=file)
    # if file != None:
    print(e,file=file)



def getPriceData(client,symbol, interval,start_str):
    # usage: data = getPriceData(client,'BNBUSDT',client.KLINE_INTERVAL_1MINUTE,'30 minutes ago UTC')

    try:
        while True:
            try:
                data = client.get_historical_klines(symbol=symbol,interval=interval,start_str=start_str)
            except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                    OSError) as e:
                print(e)
                time.sleep(2)
                continue
            break
        return data

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def timestampConverter(serverTime):
    serverTime = np.floor(serverTime / 1000)
    serverTime = serverTime - (serverTime % 60)
    serverTime = datetime.utcfromtimestamp(serverTime)
    return serverTime


def getPricePanda(client,symbol, interval,start_str):
    data = getPriceData(client,symbol, interval,start_str)

    df = pd.DataFrame(data=data, columns=['date', 'open', 'high', 'low', 'close', 'vol','1','2','3','4','5','6'])

    df.drop(columns=['1','2','3','4','5','6'],inplace=True)


    df['date'] = [timestampConverter(x) for x in df['date']]
    df['low'] = [pd.to_numeric(x) for x in df['low']]
    df['high'] = [pd.to_numeric(x) for x in df['high']]
    df['open'] = [pd.to_numeric(x) for x in df['open']]
    df['close'] = [pd.to_numeric(x) for x in df['close']]

    return df

def is_legit(client,pair):
    try:
        info = client.get_symbol_info(pair)

        if info == None:
            return False

        if info['status'] == 'BREAK':
            return False

        return True
    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def create_test_order(client,symbol,buySell,quantity,price):
    if buySell: side=client.SIDE_BUY
    if not buySell: side=client.SIDE_SELL

    try:
        order = client.create_test_order(
            symbol=symbol,
            side=side,
            type=client.ORDER_TYPE_LIMIT,
            timeInForce=client.TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=price)

        return order

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e


def limit_buy(client,symbol,quantity,price):
    try:
        limitBuy =  client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=price)

        #time.sleep(1)

        return limitBuy['orderId']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def stop_limit_buy(client,symbol,quantity,stopprice, limitprice):
    try:
        limitBuy =  client.create_order(
            symbol = symbol,
            quantity = quantity,
            stopPrice = stopprice,
            price = limitprice,
            side = client.SIDE_BUY,
            type = client.ORDER_TYPE_STOP_LOSS_LIMIT,
            timeInForce = client.TIME_IN_FORCE_GTC,
        )
        #time.sleep(1)
        return limitBuy['orderId']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def limit_sell(client,symbol,quantity,price):
    try:
        limitSell =  client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price=price)
        #time.sleep(1)
        return limitSell['orderId']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def stop_limit_sell(client,symbol,quantity,stopprice,limitprice):
    try:
        limitSell =  client.create_order(
            symbol = symbol,
            quantity = quantity,
            stopPrice = stopprice,
            price = limitprice,
            side = client.SIDE_SELL,
            type = client.ORDER_TYPE_STOP_LOSS_LIMIT,
            timeInForce = client.TIME_IN_FORCE_GTC,
        )
        #time.sleep(1)
        return limitSell['orderId']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
            raise e
        else:
            errorHandler(e)
            raise e

def market_buy(client,symbol,quantity):
    try:
        marketBuy= client.order_market_buy(
            symbol=symbol,
            quantity=quantity)
        #time.sleep(1)
        return marketBuy['orderId']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e


def market_sell(client,symbol,quantity):
    try:
        marketSell = client.order_market_sell(
            symbol=symbol,
            quantity=quantity)
        #time.sleep(1)
        return marketSell['orderId']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_order(client,symbol,orderId):
    try:
        while True:
            try:
                getOrder= client.get_order(
                symbol=symbol,
                orderId=orderId)

            except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
            OSError) as e:
                print(e)
                time.sleep(2)
                continue

            return getOrder

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def cancel_order(client,symbol,orderId):
    try:
        cancelOrder = client.cancel_order(
        symbol=symbol,
        orderId=orderId)
        # #time.sleep(1)
        return cancelOrder

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_open_orders(client,symbol):
    try:
        getOpenOrders= client.get_open_orders(symbol=symbol)
        return getOpenOrders

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_all_orders(client,symbol,n=None):
    try:
        if n == None:
            getAllOrders = client.get_all_orders(symbol=symbol)
            return getAllOrders
        else:
            getAllOrders = client.get_all_orders(symbol=symbol,limit=n)
            return getAllOrders

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_asset_balance(client, asset):
    try:
        getAssetBalance = client.get_asset_balance(asset=asset)
        return float(getAssetBalance['free'])

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_locked_asset_balance(client, asset):
    try:
        getAssetBalance = client.get_asset_balance(asset=asset)
        return float(getAssetBalance['locked'])

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_price(client,symbol):
    try:
        while True:

            try:
                prices = client.get_all_tickers()
            except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                    OSError) as e:
                print(e)
                time.sleep(2)
                continue
            break

        for each in prices:
            if each['symbol'] == symbol:
                return float(each['price'])

        print('No Price Found')
        return None

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e


def get_account(client):
    # for each in info:
    #     print(each, info[each])
    try:
        getAccount = client.get_account()
        return getAccount

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_account_status(client):
    # output: {'msg': 'Normal', 'success': True}
    try:
        getAccountStatus=client.get_account_status()
        return getAccountStatus

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_asset_details(client):
    # for each in info:
    #     print(each, info[each])
    try:
        getAssetDetails=client.get_asset_details
        return getAssetDetails

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_order_book(client, pair, limit='10'):
    try:
        a = client.get_order_book(symbol=pair, limit=limit)
        return a

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_trades(client,symbol):
    try:
        getTrades=client.get_my_trades(symbol=symbol)
        return getTrades

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_trade_fee(client, symbol):
    try:
        getTradeFee=client.get_trade_fee(symbol=symbol)
        return getTradeFee

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_order_status(client, pair, id):
    # can be 'NEW','FILLED','CANCELED'
    try:
        getOrder=get_order(client,pair,id)
        return getOrder['status']

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_order_price_cumQty(client, pair, id):
    try:
        getOrder=get_order(client,pair,id)
        return float(getOrder['price']),float(getOrder['cummulativeQuoteQty'])

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def get_cumQty(client, pair, id):
    try:
        getOrder=get_order(client,pair,id)
        return float(getOrder['cummulativeQuoteQty'])

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def cancel_all(client,symbol):
    try:
        openOrders = get_open_orders(client, symbol)

        for each in openOrders:
            orderId = each['orderId']
            cancel_order(client, symbol, orderId)

        #time.sleep(1)
        return True

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

    return False


def get_past_volume(client, pair, interval=Client.KLINE_INTERVAL_1MINUTE, when='3 minutes ago UTC'):
    data = getPricePanda(client, pair, interval, when)

    data['vol'] = [pd.to_numeric(x) for x in data['vol']]

    # vol is just qty, number of units,, without price factored in

    totalVol = sum(data.vol)

    return totalVol

# get_symbol_info(pairname)
# {'filterType': 'PRICE_FILTER', 'minPrice': '0.01000000', 'maxPrice': '10000000.00000000', 'tickSize': '0.01000000'}
# {'filterType': 'PERCENT_PRICE', 'multiplierUp': '10', 'multiplierDown': '0.1', 'avgPriceMins': 5}
# {'filterType': 'LOT_SIZE', 'minQty': '0.00000100', 'maxQty': '10000000.00000000', 'stepSize': '0.00000100'}
# {'filterType': 'MIN_NOTIONAL', 'minNotional': '10.00000000', 'applyToMarket': True, 'avgPriceMins': 5}
# {'filterType': 'ICEBERG_PARTS', 'limit': 10}
# {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}

def getPrecision(client, symbol):
    try:
        precision = client.get_symbol_info(symbol)
        return (precision)
        # return precision['filters'][3], float(precision['filters'][2]['stepSize'])
        # return float(precision['filters'][2]['stepSize'])  #for qty

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def getServerTime(client):
    try:
        serverTime = client.get_server_time()
        serverTime = serverTime['serverTime']


        return timestampConverter(serverTime)

    except (BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:
        errorHandler(e)
        raise e

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def format_price(priceFloat,precision, truncation=False):
    # return str(truncate(priceFloat,precision))
    if truncation:
        return "{:0.0{}f}".format(truncate(priceFloat,precision), precision)
    return "{:0.0{}f}".format(priceFloat, precision)


def formattedPrcQty(coin,price,quantity=None):
    # coin = coin+base

    prc = format_price(price,precision[coin][0])
    if quantity!=None:
        qty = format_price(quantity,precision[coin][1],truncation=True)
        return prc,qty

    return prc

def performanceData(pair):
    start = 1559059200000
    end = 1559318400000

    a = get_all_orders(client, pair)

    totalBuys = 0
    totalSells = 0
    buyValue = 0
    sellValue = 0
    startingCapital = 0

    lastClosePrice = float(
        (client.get_historical_klines(pair, client.KLINE_INTERVAL_1MINUTE, start_str=str(end), end_str=str(end)))[
            0][1])

    for each in a:
        timestamp = int(each['time'])
        status = each['status']
        side = each['side']
        value = float(each['cummulativeQuoteQty'])
        qty = float(each['executedQty'])

        if timestamp < end and timestamp > start and status == client.ORDER_STATUS_FILLED:
            if side == client.SIDE_BUY:

                if totalBuys == 0:
                    startingCapital = value

                totalBuys += 1
                lastBuy = value
                lastBuyQty = qty
                buyValue += lastBuy
            elif side == client.SIDE_SELL:
                totalSells += 1
                lastSell = value
                sellValue += lastSell

    # print('num buys - num sells = ', totalBuys - totalSells)

    if totalSells < totalBuys:
        sellValue += lastBuyQty * lastClosePrice

    totalMade = (sellValue*.999) - (buyValue*1.001)
    percentGain = 100.0 * totalMade / startingCapital

    print('Absolute Gain:', '%.2f' % totalMade, 'USDT')
    print('Percentage Gain:', '%.2f' % percentGain, '%')

    marketPerformance(pair)

def marketPerformance(pair):
    data = pd.read_csv(pair+'_1m.csv')
    open = data.iloc[0].open
    close = data.iloc[-1].close
    high = max(data.high)
    low = min(data.low)

    highDate = data[data.high == high].DateTime.values[0]
    lowDate = data[data.low == low].DateTime.values[0]

    if highDate > lowDate:
        maxGain = 100 * (high - low) / low
    else:
        maxGain = 100 * (low - high) / high

    periodGain = 100 * (close - open) / open

    print('period gain:', '%.2f' % periodGain, '% | max possible gain:', '%.2f' % maxGain, '%')

def totalCurrentValue():
    USDTbalance = get_asset_balance(client, 'USDT')
    totalVal = USDTbalance

    for coin in precision.keys():
        qty = get_asset_balance(client,coin)
        qty += get_locked_asset_balance(client,coin)
        price = get_price(client,coin+'USDT')
        totalVal += (qty*price)


    return totalVal



def pieChunk(client,piePercent=0.1):
    #TODO: For those that open position, should take into account 'locked' amounts also?
    USDTbalance = get_asset_balance(client, 'USDT')

    # print('USDT', USDTbalance)

    totalPieValue = USDTbalance
    index = -1

    for coin in precision.keys():
        n = 10
        this = get_all_orders(client, coin + 'USDT', n=n)
        time.sleep(1.2)
        latest = None

        n = len(this)
        # print("Coin:", coin, 'n:',n)

        if n > 0:


            for i in range(index, index - n, -1):
                if (this[i]['status'] == Client.ORDER_STATUS_CANCELED):
                    continue
                if (this[i]['side'] == Client.SIDE_SELL) and ((this[i]['status'] == Client.ORDER_STATUS_FILLED) or (this[i]['status'] == Client.ORDER_STATUS_PARTIALLY_FILLED)):
                    break

                if this[i]['side'] == Client.SIDE_BUY:
                    if (this[i]['status'] == Client.ORDER_STATUS_FILLED) or (this[i]['status'] == Client.ORDER_STATUS_NEW):
                        latest = this[i]
                        break

        if latest == None: continue

        # print(latest['symbol'],latest['price'],latest['origQty'],latest['cummulativeQuoteQty'])

        # usdt = float(latest['price']) * float(latest['origQty'])
        latestPrice = float(latest['price'])
        latestQty = get_asset_balance(client,coin)


        # usdt = float(latest['cummulativeQuoteQty']) * 0.99
        usdt = latestPrice * latestQty
        # print(coin, usdt)

        totalPieValue += usdt

    print('Total Pie Value',totalPieValue)


    allocation = totalPieValue * piePercent
    # if USDTbalance > allocation:
    #     return allocation
    # else:
    #     return None

    print('Allocation Value:', allocation, 'USDT')
    return allocation




if __name__ == '__main__':
    ###
    ### GTC (Good-Til-Canceled) orders are effective until they are executed or canceled.
    ### IOC (Immediate or Cancel) orders fills all or part of an order immediately and cancels the remaining part of the order.
    ### FOK (Fill or Kill) orders fills all in its entirety, otherwise, the entire order will be cancelled.
    ###
    while True:
        try:
            client = Client(apiK, sK)
        except(ConnectionError,OSError) as e:
            print(e)
            time.sleep(10)
            continue
        break

    b = pieChunk(client)

    exit()

    a = get_order_status(client,'NANOUSDT','10575670')

    print(a)

    exit()

    # coins = trgPairs['USDTETH']
    #
    # for coin in coins:
    #
    #     info = getPrecision(client,coin+'ETH')
    #     for each in info['filters']:
    #         if each['filterType'] == 'PRICE_FILTER':
    #             tickSize = float(each['tickSize'])
    #         if each['filterType'] == 'LOT_SIZE':
    #             stepSize = float(each['stepSize'])
    #
    #     a = 0
    #     while tickSize!=1:
    #         tickSize = tickSize * 10
    #         a += 1
    #
    #     b = 0
    #     while stepSize != 1:
    #         stepSize = stepSize * 10
    #         b += 1
    #
    #     print("precision['" + coin + "ETH'] = ["+str(a)+","+str(b)+"]")
    #
    # exit()

    nano = get_all_orders(client,'NANOUSDT',n=10)

    # print(nano)

    for each in nano:
        print(each)

    exit()

    time1 = time.time()
    price1 = get_price(client,'LTCUSDT')
    time1end = time.time()
    time2 = time.time()

    # data= getPricePanda(client,'BTCUSDT',Client.KLINE_INTERVAL_1MINUTE,'1 minute ago UTC')

    data = getPriceData(client, 'LTCUSDT', Client.KLINE_INTERVAL_1MINUTE,'2 minute ago UTC')
    time2end = time.time()
    price2 = data[-1]
    price2 = float(price2[4])

    # df = pd.DataFrame(data=data, columns=['date', 'open', 'high', 'low', 'close', 'vol', '1', '2', '3', '4', '5', '6'])
    #
    # df.drop(columns=['1', '2', '3', '4', '5', '6'], inplace=True)
    #
    # df['date'] = [timestampConverter(x) for x in df['date']]
    # df['low'] = [pd.to_numeric(x) for x in df['low']]
    # df['high'] = [pd.to_numeric(x) for x in df['high']]
    # df['open'] = [pd.to_numeric(x) for x in df['open']]
    # df['close'] = [pd.to_numeric(x) for x in df['close']]
    #
    # return df

    # price2 = data.iloc[-1].close

    print(price1, time1end-time1)
    print(price2, time2end-time2)



    exit()

    while True:
        try:
            startTime = time.time()

            client = Client(apiK,sK)

            a = client.get_exchange_info()

            # aa = is_legit(client,'BCCUSDT')
            # bb = is_legit(client,'BTCUSDT')
            # cc = is_legit(client,'USDTBTC')
            #
            # print(aa,bb,cc)
            #
            # exit()

            symbols = a['symbols']

            # rateLimits = a['rateLimits']
            # # for each in a:
            # #     print(each)
            #
            # print(rateLimits)
            #
            # # print(get_order_book(client,'XLMUSDT'))
            # exit()

            coins = {}
            for mkt in ['BNB','BTC','ETH','XRP','USDT','PAX','TUSD','USDC']:
                c = 0
                coins[mkt] = []
                for sym in symbols:
                    if sym['quoteAsset'] == mkt:
                        c+=1
                        coins[mkt].append(sym['baseAsset'])


                print(mkt,c)

            print()

            # for each in coins:
            #     print(each)
            #     print(coins[each])
            #     print()
            # exit()
            stableCoins = ['USDT','PAX','TUSD','USDC']
            mainMkts = ['BTC','ETH']

            triangleOpps = {}
            print('trgPairs = {}')

            for sc in stableCoins:
                for mm in mainMkts:
                    triangleOpps[sc+mm] = []

                    for ticker in coins[sc]:
                        if not is_legit(client,ticker+sc):
                            print('# unlegit',ticker+sc)
                            continue

                        if ticker in coins[mm]:
                            if not is_legit(client, ticker + mm):
                                print('# unlegit', ticker + mm)
                                continue
                            triangleOpps[sc+mm].append(ticker)

                    print('#',sc,mm, len(triangleOpps[sc+mm]))

                    strBuilder = "trgPairs[" + "'" +sc+mm+"'] = "
                    for ticker in triangleOpps[sc+mm]:
                        strBuilder = strBuilder + "'" + ticker + "',"
                    print(strBuilder)
                    print()





            exit()

            # print(getPrecision(client,'BTCUSDT'))
            # # print(getPrecision(client, 'ETHUSDT'))
            # # print(getPrecision(client, 'QTUMUSDT'))
            # print(getPrecision(client, 'XLMUSDT'))
            # # print(getPrecision(client, 'ATOMUSDT'))
            # print(getPrecision(client, 'EOSUSDT'))
            # print(getPrecision(client, 'BTTUSDT'))
            # print(getPrecision(client, 'ZECUSDT'))



            # result = get_order(client,'BNBUSDT','131735466')
            # print(result['status'])
            #
            # a = get_open_orders(client,'ETHUSDT')
            # for each in a:
            #     print(each)
            #     print(datetime.fromtimestamp(int(each['time'])/1000))

            # print(datetime.fromtimestamp(time.time()))
            # buyBarrierFactor = 0.8
            # pair = 'XLMUSDT'
            # hourPoint = getPricePanda(client, pair , client.KLINE_INTERVAL_1HOUR, '60 minutes ago UTC')
            # hourPoint = hourPoint.iloc[0]
            # buyBarrier = (hourPoint.high - hourPoint.low)*buyBarrierFactor + hourPoint.low
            #
            # print(buyBarrier)

            # a = get_price(client,'EOSUSDT')
            # print(a)
            # c = float(a)*0.995
            # price,qty=formattedPrcQty('EOS',c,6.59)
            # b = limit_sell(client,'EOSUSDT',qty,price)



            exit()
            # coins = pd.read_csv('Binance_USDT_pairs.csv')
            #
            # print(coins)
            # exit()


            elapsed = time.time() - startTime
            print('Time taken: %.4f'%elapsed)

            #time.sleep(3)

        except (ConnectionError,ConnectionAbortedError,ConnectionRefusedError,ConnectionResetError,
            OSError,BinanceAPIException,BinanceOrderException,BinanceOrderMinAmountException,BinanceOrderMinPriceException,
            BinanceOrderMinTotalException,BinanceOrderUnknownSymbolException,BinanceRequestException) as e:

            errorHandler(e)
            #time.sleep(10)

        except (KeyboardInterrupt):
            try:
                print('Shutting Down, please wait and do not press anything..')

            finally:
                print('Saving files..')
                print('shut down completed')
                exit('shut down complete.')



