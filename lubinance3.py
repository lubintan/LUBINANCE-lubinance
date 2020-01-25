from interactData import *
from analyzerFunctions import *


profitPercent = 0.008
pollingInterval = 20
dropPercent = 0.96
feePercent = 0.0015

bolliDelay = 35 * 60  # 35 mins
buyBreakPercent = 1.003
buyBarrierFactor = 0.8
buyMargin = 0.9975
sellingMargin = 1.008
belowBolliPercent = 0.9995

gap = 0.9975
sellStopPercent = 0.9991
sellLimitPercent = 0.9986
postSellRest = 3600 # 1 hour




def closedPhase(client, coin, sellPrice=None, margin=None, assets=0):
    global file

    phaseId = datetime.utcnow()
    print('Closed Phase ID', phaseId,file=file)
    print('sellPrice',sellPrice,'margin',margin,'assets',assets,file=file)

    pair = coin + 'USDT'
    waitForBuyBreak = False
    lowThreshold = 0
    bolliDate = datetime(2019, 1, 1)
    bolliBroken = False

    nowTime = None

    if margin != None:
        # setLimitBuy at sellPrice
        buyPrice = sellPrice
        buyOrderId = '12345' # limit buy
        buyQty = assets / buyPrice
        price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
        buyOrderId = limit_buy(client, pair, quantity=quantity, price=price)

        print('Waiting for Buy Order to Fill, price:',buyPrice,file=file)

    else:
        buyOrderId = None

    while True:
        try:
            time.sleep(pollingInterval)
            ### see if buy order fulfilled ###
            # get status of the buy order id

            if (buyOrderId!= None) and (get_order_status(client,pair,buyOrderId) == Client.ORDER_STATUS_FILLED):
                margin = margin + (buyPrice*feePercent)

                print('Regain Buy Filled at price:', buyPrice,file=file)

                break

            # if fulfilled:
            #   break. margin = margin + (buyPrice*feePercent).
            #   Go to open phase.

            dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

            print('----- D-A-T-E ----', dataPoints.iloc[-1].date,file=file)

            # maClose = np.mean(dataPoints.iloc[-6:-1].close)
            maHigh = np.mean(dataPoints.iloc[-6:-1].high)
            currentPrice = get_price(client, pair)


            print('waitForBuyBreak:', waitForBuyBreak,file=file)

            if waitForBuyBreak:

                hourPoint = getPricePanda(client, pair, client.KLINE_INTERVAL_1HOUR, '120 minutes ago UTC')
                hourPoint = hourPoint.iloc[0]
                buyBarrier = (hourPoint.high - hourPoint.low) * buyBarrierFactor + hourPoint.low

                buyBreakThresh = maHigh * buyBreakPercent
                print('buyBreakThresh', buyBreakThresh, 'buyBarrier', buyBarrier,file=file)

                if (currentPrice > buyBreakThresh) and (currentPrice < buyBarrier):
                    # put in buy limit order for currentPrice * buyBreakLimit
                    buyPrice = maHigh * (buyBreakPercent + 0.0007)
                    buyQty = assets / buyPrice
                    price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
                    openBuyId = limit_buy(client, pair, quantity=quantity, price=price)

                    print('!!Order in!!!', openBuyId, 'price', price, 'qty', quantity,file=file)

                    # wait for order to be filled
                    # while len(get_open_orders(client,pair))>0:
                    print('waiting for order to fill...', '| UTC Time', datetime.utcnow(),file=file)
                    while (get_order_status(client, pair, openBuyId) != client.ORDER_STATUS_FILLED):
                        time.sleep(pollingInterval)

                    print('Regular Buy Filled at price:', buyPrice,file=file)

                    waitForBuyBreak = False

                    orderData = get_order(client, pair, openBuyId)
                    buyQty = float(orderData['executedQty'])
                    btcAssets = get_asset_balance(client, coin)
                    assets = 0

                    print('BUY AT:', buyPrice, 'buy qty:', buyQty, 'after tx fee', btcAssets, 'order num', openBuyId,file=file)

                    break

            if dataPoints.iloc[-1].date == nowTime:
                continue

            nowTime = dataPoints.iloc[-1].date

            print('bolliBroken:', bolliBroken,file=file)
            if bolliBroken:
                bolliTimeSince = datetime.utcnow() - bolliDate
                print('Bolli Time Since:', bolliTimeSince,file=file)

                if bolliTimeSince.seconds > bolliDelay:
                    # reset
                    bolliBroken = False
                    bolliDate = datetime(2019, 1, 1)
                    lowThreshold = 0

                prevLowest = lowThreshold * buyMargin
                print('currentPrice', currentPrice, 'lowTresh x buyMarg', prevLowest,file=file)
                if currentPrice < prevLowest:
                    waitForBuyBreak = True
                    bolliBroken = False
                    bolliDate = datetime(2019, 1, 1)
                    lowThreshold = 0

            latestBolliValue = bollingerLow(dataPoints.iloc[-6:-1].close)
            latestBar = dataPoints.iloc[-2]
            latestLow = latestBar.low
            bolliThresh = latestBolliValue * belowBolliPercent

            print('latestLow', latestLow, 'bolliThresh', bolliThresh, 'lowThresh', lowThreshold,file=file)

            if (latestLow < bolliThresh) and (latestLow != lowThreshold):
                lowThreshold = latestLow
                bolliDate = latestBar.date
                bolliBroken = True

        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                OSError) as e:

            try:
                errorHandler(e,file=file)
                time.sleep(10)
            except (KeyboardInterrupt):
                print('Saving files..',file=file)
                putUSDTToBasket(coin+'.txt',assets)
                print('Files saved.',file=file)
                exit('Shut down complete.')

        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                BinanceOrderMinPriceException,
                BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceRequestException) as e:
            errorHandler(e,file=file)
            print("Binance API Error",file=file)

            exit(3000)

        except (KeyboardInterrupt):
            try:
                print('Shutting Down, please wait and do not press anything..',file=file)

            finally:
                print('*** Current USDT Allocation:', assets, '***',file=file)
                print('Saving files..',file=file)
                putUSDTToBasket(coin + '.txt', assets)
                print('Files saved.',file=file)
                exit('Shut down complete.')

    result = openPhase(client,coin,buyPrice,margin,assets)

    print('Returned to Closed Phase ID', phaseId,file=file)
    print('',file=file)
    return result



def openPhase(client, coin, buyPrice=None, margin=None,assets=0):
    global file

    phaseId = datetime.utcnow()
    print('Open Phase ID', phaseId,file=file)

    pair = coin + 'USDT'
    if margin==None:
        margin = profitPercent * buyPrice
    target = buyPrice + margin

    print('buyPrice', buyPrice, 'margin', margin, 'assets', assets, 'TARGET',  target,file=file)

    #set stop limit sell
    sellPrice = buyPrice * dropPercent
    sellDropStop = sellPrice * 1.0005
    btcAssets = get_asset_balance(client, coin)
    stopPrice, sellQty = formattedPrcQty(coin, sellDropStop, btcAssets)
    limitPrice, sellQty = formattedPrcQty(coin, sellPrice, btcAssets)
    sellOrderId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                                     limitprice=limitPrice)


    print('Drop Sell Order In At Price:', limitPrice,'Trigger:',sellDropStop,file=file)

    openSellId = None # sell stop limit


    while True:
        time.sleep(pollingInterval)

        dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

        print('----- D-A-T-E ----', dataPoints.iloc[-1].date,file=file)

        currentPrice = get_price(client, pair)

        if get_order_status(client, pair, sellOrderId) == Client.ORDER_STATUS_FILLED:
            loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
            margin = margin + loss

            print('Drop SELL filled at price:', sellPrice, 'new margin:', margin,file=file)

            break

        if (currentPrice * gap) > target:
            # #sellFinish
            uptrendData = dataPoints.iloc[-4:-1]
            uptrendFound = uptrendFinder(uptrendData)

            print('uptrend found?', uptrendFound,file=file)
            # check that last 4 all above each other
            if uptrendFound:
                if openSellId==None:

                    # set stop and limit
                    sellStop = currentPrice * sellStopPercent
                    sellLimit = currentPrice * sellLimitPercent
                    btcAssets = get_asset_balance(client, coin)
                    stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
                    limitPrice, sellQty = formattedPrcQty(coin, sellLimit, btcAssets)

                    try:
                        if get_order_status(client,pair,sellOrderId) != Client.ORDER_STATUS_FILLED:
                            cancel_order(client,pair,sellOrderId)
                            print('Drop SELL CANCELLED',file=file)
                        else:
                            loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
                            margin = margin + loss
                            print('Last Minute Drop SELL filled at price:', sellPrice, 'new margin:', margin,file=file)
                            break

                        openSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                                                     limitprice=limitPrice)
                        target = sellStop

                        print('Sell Stop Order Put In', 'order num', openSellId, 'stop', stopPrice, 'limit', limitPrice,
                              'qty', sellQty,file=file)
                        continue
                    except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                           BinanceOrderMinPriceException,
                           BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                           BinanceRequestException) as e:
                        errorHandler(e,file=file)
                        print("Binance API Error",file=file)
                        if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                            openSellId = limit_sell(client, pair, sellQty, limitPrice)
                            print('CONTINGENCY LIMIT SELL', openSellId,file=file)
                            continue
                        else:
                            exit(3000)

                else: # openSellId exists
                    status = get_order_status(client, pair, openSellId)
                    if ((currentPrice * gap) > target) and (status == 'NEW'):
                        cancel_order(client, pair, openSellId)
                        print('Drop SELL CANCELLED',file=file)
                        # set stop and limit
                        sellStop = currentPrice * sellStopPercent
                        sellLimit = currentPrice * sellLimitPercent
                        btcAssets = get_asset_balance(client, coin)
                        stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
                        limitPrice, sellQty = formattedPrcQty(coin, sellLimit, btcAssets)
                        try:
                            openSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                                                         limitprice=limitPrice)
                            target = sellStop

                            print('Sell Stop Order Put In', 'order num', openSellId, 'stop', stopPrice, 'limit',
                                  limitPrice,'qty', sellQty,file=file)
                            continue

                        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                               BinanceOrderMinPriceException,
                               BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                               BinanceRequestException) as e:
                            errorHandler(e,file=file)
                            print("Binance API Error",file=file)
                            if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                                openSellId = limit_sell(client, pair, sellQty, limitPrice)
                                print('CONTINGENCY LIMIT SELL', openSellId,file=file)
                                continue
                            else:
                                exit(3000)

                    elif status == client.ORDER_STATUS_FILLED:
                        # uptrendFound = False
                        # longPosition = False

                        orderData = get_order(client, pair, openSellId)
                        totalUSDT = float(orderData['cummulativeQuoteQty'])
                        sellPrice = float(orderData['price'])
                        # margin = None

                        assets = (1 - 0.001) * totalUSDT

                        print('SELL order Filled', openSellId, 'at price', sellPrice, 'Total USDT:', assets,file=file)
                        print('Closing Open Phase Id',phaseId,file=file)
                        return True,assets




    closedPhase(client,coin,sellPrice,margin,assets)
    print('Returned to Open Phase Id', phaseId,file=file)




def lubinance(coin='BTC', startUSDT = '',buyMargin = 0.9975,sellingMargin=1.008,pollingInterval = 20):

    global file
    file = open("logs//"+coin+datetime.utcnow().strftime("%y%m%d_%H:%M:%S") +".txt", "a")
    client = Client(apiK, sK)
    pair = coin + 'USDT'


    #region:check for outstanding orders
    print('',file=file)
    openOrders = get_open_orders(client, pair)

    cancelOrders = None

    while len(openOrders) > 0:
        print(len(openOrders), "currently exist!",file=file)
        for each in openOrders:
            print(each,file=file)


        if cancelOrders == None:
            a = input("Enter 'y' to automatically cancel ALL orders. Anything else will wait for orders to complete")
            if a =='y':
                for each in openOrders:
                    orderId = each['orderId']
                    cancelOrders = cancel_order(client,pair,orderId)
                    time.sleep(0.3)
                    print('Cancelled Order', each,file=file)
            else:
                cancelOrders = False

        time.sleep(pollingInterval)
        openOrders = get_open_orders(client, pair)

    print('No Open Orders Found For', pair,file=file)

    #check how much you have
    btcAssets = get_asset_balance(client,coin)
    if btcAssets < (1/(10**precision[coin][1])):
        # longPosition = False
        print('Currently not holding', coin,'. Starting with USDT.',file=file)
    else:
        # longPosition = True
        print('Currently holding',btcAssets,coin,file=file)
    #endregion

    if startUSDT=='':
        assets = getUSDTFromBasket(coin+'.txt')
    else:
        assets = float(startUSDT)



    while True:
        case, assets = closedPhase(client,coin,sellPrice=None,margin=None,assets=assets)

        print('Case Closed?', case,file=file)

        # Buffer Time
        print('Rest 1 hour from', datetime.fromtimestamp(time.time()), '(UTC+8)',file=file)
        time.sleep(postSellRest)



if __name__ == '__main__':
    inputs = sys.argv

    symbol = inputs[1].upper()
    startUSDT = inputs[2]


    lubinance(symbol, startUSDT)

