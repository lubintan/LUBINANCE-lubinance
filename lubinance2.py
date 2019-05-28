from interactData import *
from analyzerFunctions import *




def lubinance(coin='BTC', startUSDT = '',buyMargin = 0.9975,sellingMargin=1.008,pollingInterval = 20):

    client = Client(apiK, sK)
    pair = coin + 'USDT'


    #region:check for outstanding orders
    print()
    openOrders = get_open_orders(client, pair)

    cancelOrders = None

    while len(openOrders) > 0:
        print(len(openOrders), "currently exist!")
        for each in openOrders:
            print(each)


        if cancelOrders == None:
            a = input("Enter 'y' to automatically cancel ALL orders. Anything else will wait for orders to complete")
            if a =='y':
                for each in openOrders:
                    orderId = each['orderId']
                    cancelOrders = cancel_order(client,pair,orderId)
                    time.sleep(0.3)
                    print('Cancelled Order', each)
            else:
                cancelOrders = False

        time.sleep(pollingInterval)
        openOrders = get_open_orders(client, pair)

    print('No Open Orders Found For', pair)

    #check how much you have
    btcAssets = get_asset_balance(client,coin)
    if btcAssets < 0.001:
        # longPosition = False
        print('Currently not holding', coin,'. Starting with USDT.')
    else:
        # longPosition = True
        print('Currently holding',btcAssets,coin)
    #endregion

    if startUSDT=='':
        assets = getUSDTFromBasket(coin+'.txt')
    else:
        assets = float(startUSDT)

    btcAssets = 0
    txFeePercent = 0.001

    failSafePercentLimit = 0.955 #lose at most 4.5%
    failSafePercentStop = 0.96 # triggered at 4.0% loss

    fileName = coin+'txLog_'+datetime.utcnow().strftime("%y%m%d_%H:%M:%S")+'.txt'


    openBuyId = None
    openSellId = None
    failSafeId = None

    postSellRest = 3600 # 1 hour

    longPosition = False

    counterFive = 0
    nowTime = None

    waitForBuyBreak = False
    buyBreakPercent = 1.003
    buyBarrierFactor = 0.8
    gap = 0.9975
    sellStopPercent = 0.9991
    sellLimitPercent = 0.9986
    sellMin = 1e5

    belowBolliPercent = 0.9995
    lowThreshold = 0
    bolliDate = datetime(2019,1,1)
    bolliDelay = 35 * 60  # 35 mins
    bolliBroken = False

    while True:
        try:
            time.sleep(pollingInterval)

            start_time = time.time()
            dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

            print('----- D-A-T-E ----', dataPoints.iloc[-1].date)

            maClose = np.mean(dataPoints.iloc[-6:-1].close)
            maHigh = np.mean(dataPoints.iloc[-6:-1].high)
            currentPrice = get_price(client, pair)

            print(currentPrice,', maClose',maClose,', maHigh',maHigh, 'USDT assets', assets, 'coin assets', btcAssets)
            print('longPosition:', longPosition, 'waitforbuybreak', waitForBuyBreak, 'sellmin', sellMin)

            if longPosition:
                print('openSellId:', openSellId)
                if openSellId == None:

                    # if failSafeId == None:
                    #     if currentPrice < (failSafePercentStop * buyPrice):
                    #         # put in stop loss order
                    #         # failSafeStop = buyPrice * failSafePercentStop
                    #         failSafeLimit = buyPrice * failSafePercentLimit
                    #         # failSafeStop, failSafeQty = formattedPrcQty(coin,failSafeStop,btcAssets)
                    #         failSafeLimit, failSafeQty = formattedPrcQty(coin,failSafeLimit,btcAssets)
                    #
                    #         failSafeId = limit_sell(client,pair,quantity=failSafeQty,price=failSafeLimit)
                    #
                    #         print('Fail Stop In!', 'Order Num',failSafeId,'limit', failSafeLimit, 'qty', failSafeQty)
                    #         continue
                    #
                    # else:
                    #     if get_order_status(client,pair,failSafeId) == client.ORDER_STATUS_FILLED:
                    #         uptrendFound = False
                    #         longPosition = False
                    #
                    #         sellMin = 1e5
                    #         orderData = get_order(client, pair, failSafeId)
                    #         totalUSDT = float(orderData['cummulativeQuoteQty'])
                    #         assets = (1 - txFeePercent) * totalUSDT
                    #
                    #         print('fail safe filled', failSafeId)
                    #         failSafeId = None
                    #     elif currentPrice >= (failSafePercentStop * buyPrice):
                    #         # cancel fail safe stop loss
                    #         # if failSafeId !=None:
                    #         cancel_order(client,pair,failSafeId)
                    #         print('fail safe cancelled', failSafeId)
                    #         failSafeId = None



                    uptrendData = dataPoints.iloc[-4:-1]
                    uptrendFound = uptrendFinder(uptrendData)

                    print('uptrend foud? ==>', uptrendFound)
                    # check that last 4 all above each other
                    if uptrendFound:
                        if (currentPrice*gap) > sellMin:
                            #set stop and limit
                            sellStop = currentPrice * sellStopPercent
                            sellLimit = currentPrice * sellLimitPercent
                            btcAssets = get_asset_balance(client,coin)
                            stopPrice, sellQty = formattedPrcQty(coin,sellStop,btcAssets)
                            limitPrice, sellQty = formattedPrcQty(coin,sellLimit, btcAssets)

                            try:
                                openSellId = stop_limit_sell(client,pair,quantity=sellQty,stopprice=stopPrice,limitprice=limitPrice)
                                sellMin = sellStop

                                print('!! S-E-L-L !!', 'order num', openSellId, 'stop', stopPrice, 'limit', limitPrice,
                                      'qty', sellQty)
                                continue
                            except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                                   BinanceOrderMinPriceException,
                                   BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                                   BinanceRequestException) as e:
                                print(e)
                                print("Binance API Error")
                                if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                                    openSellId = limit_sell(client,pair,sellQty,limitPrice)
                                    print('LIMIT SELL', openSellId)
                                    continue
                                else:
                                    exit(3000)
                    else:
                        continue
                else:
                    status = get_order_status(client,pair, openSellId)
                    if ((currentPrice * gap) > sellMin) and (status=='NEW'):
                        cancel_order(client,pair,openSellId)
                        print('cancel', openSellId)
                        #set stop and limit
                        sellStop = currentPrice * sellStopPercent
                        sellLimit = currentPrice * sellLimitPercent
                        btcAssets = get_asset_balance(client, coin)
                        stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
                        limitPrice, sellQty = formattedPrcQty(coin, sellLimit, btcAssets)
                        try:
                            openSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                                                         limitprice=limitPrice)
                            sellMin = sellStop

                            print('!! S-E-L-L !!', 'order num',openSellId,'stop',stopPrice,'limit',limitPrice, 'qty', sellQty, 'buyId', openBuyId, 'sellId',openSellId)
                            continue
                        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                               BinanceOrderMinPriceException,
                               BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                               BinanceRequestException) as e:
                            print(e)
                            print("Binance API Error")
                            if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                                openSellId = limit_sell(client, pair, sellQty, limitPrice)
                                print('LIMIT SELL', openSellId)
                                continue
                            else:
                                exit(3000)

                    elif status==client.ORDER_STATUS_FILLED:
                        uptrendFound = False
                        longPosition = False

                        sellMin = 1e5
                        orderData = get_order(client,pair,openSellId)
                        totalUSDT = float(orderData['cummulativeQuoteQty'])
                        assets = (1-txFeePercent)*totalUSDT

                        print('orderFilled', openSellId)
                        openSellId = None

                        # Buffer Time
                        print('Rest 1 hour from', datetime.fromtimestamp(time.time()), '(UTC+8)')
                        time.sleep(postSellRest)
                        continue

                        #cancel fail safe stop loss
                        # if failSafeId !=None:
                        #     cancel_order(client,pair,failSafeId)
                        #     print('fail safe cancelled', failSafeId)
                        #     failSafeId = None


            print('waitForBuyBreak:', waitForBuyBreak)

            if waitForBuyBreak:

                hourPoint = getPricePanda(client, pair, client.KLINE_INTERVAL_1HOUR, '120 minutes ago UTC')
                hourPoint = hourPoint.iloc[0]
                buyBarrier = (hourPoint.high - hourPoint.low) * buyBarrierFactor + hourPoint.low

                buyBreakThresh = maHigh * buyBreakPercent
                print('buyBreakThresh', buyBreakThresh, 'buyBarrier', buyBarrier)

                if (currentPrice > buyBreakThresh) and (currentPrice < buyBarrier):
                    # put in buy limit order for currentPrice * buyBreakLimit
                    buyPrice = maHigh* (buyBreakPercent + 0.0007)
                    buyQty = assets/buyPrice
                    price,quantity = formattedPrcQty(coin,price=buyPrice,quantity=buyQty)
                    openBuyId = limit_buy(client,pair,quantity=quantity,price=price)

                    print('!!Order in!!!', openBuyId, 'price',price,'qty',quantity)

                    # wait for order to be filled
                    # while len(get_open_orders(client,pair))>0:
                    print('waiting for order to fill...','| current Time', datetime.utcnow())
                    while (get_order_status(client,pair,openBuyId) != client.ORDER_STATUS_FILLED):
                        time.sleep(pollingInterval)

                    longPosition = True
                    sellMin = buyPrice * sellingMargin
                    waitForBuyBreak = False
                    counterFive = 0

                    orderData = get_order(client,pair,openBuyId)
                    buyQty = float(orderData['executedQty'])
                    btcAssets = get_asset_balance(client,coin)
                    assets = 0

                    print('BUY AT:', buyPrice, 'buy qty:',buyQty, 'after tx fee',btcAssets, 'order num', openBuyId)
                    openBuyId = None

                    # # put in stop loss order
                    # failSafeStop = buyPrice * failSafePercentStop
                    # failSafeLimit = buyPrice * failSafePercentLimit
                    # failSafeStop, failSafeQty = formattedPrcQty(coin,failSafeStop,btcAssets)
                    # failSafeLimit, failSafeQty = formattedPrcQty(coin,failSafeLimit,btcAssets)
                    #
                    # failSafeId = stop_limit_sell(client,pair,quantity=failSafeQty,stopprice=failSafeStop,limitprice=failSafeLimit)
                    #
                    # print('Fail Stop In!', 'Order Num',failSafeId,'stop', failSafeStop, 'limit', failSafeLimit, 'qty', failSafeQty)

                    continue



            if dataPoints.iloc[-1].date == nowTime:
                continue

            nowTime = dataPoints.iloc[-1].date



            if longPosition == False: #ie. looking to buy

            #     latestBar = dataPoints.iloc[-2]
            #
            #     if latestBar.close < maClose:
            #         counterFive +=1
            #
            #         if counterFive > 5:
            #             waitForBuyBreak = True
            #     else:
            #         counterFive = 0
            #         print('counterFive reset')
            #
            # print('counterFive:', counterFive)
                print('bolliBroken:', bolliBroken)
                if bolliBroken:

                    bolliTimeSince = datetime.utcnow() - bolliDate
                    print('Bolli Time Since:', bolliTimeSince)

                    if bolliTimeSince.seconds > bolliDelay:
                        #reset
                        bolliBroken = False
                        bolliDate = datetime(2019,1,1)
                        lowThreshold = 0

                    prevLowest = lowThreshold*buyMargin
                    print('currentPrice', currentPrice, 'lowTresh x buyMarg', prevLowest)
                    if currentPrice < prevLowest:
                        waitForBuyBreak = True
                        bolliBroken = False
                        bolliDate = datetime(2019, 1, 1)
                        lowThreshold = 0



                latestBolliValue = bollingerLow(dataPoints.iloc[-6:-1].close)
                latestBar = dataPoints.iloc[-2]
                latestLow = latestBar.low
                bolliThresh = latestBolliValue * belowBolliPercent

                print('latestLow', latestLow, 'bolliThresh', bolliThresh, 'lowThresh', lowThreshold)

                if (latestLow < bolliThresh) and (latestLow!=lowThreshold):
                    lowThreshold = latestLow
                    bolliDate = latestBar.date
                    bolliBroken = True




        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                OSError) as e:

            try:
                errorHandler(e)
                time.sleep(10)
            except (KeyboardInterrupt):
                print('Saving files..')
                putUSDTToBasket(coin+'.txt',assets)
                print('Files saved.')
                exit('Shut down complete.')

        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                BinanceOrderMinPriceException,
                BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceRequestException) as e:
            print(e)
            print("Binance API Error")
            # if str(e).strip()=='APIError(code=-2010): Order would trigger immediately.':
            #     print('continuing..')
            #     continue

            exit(3000)

        except (KeyboardInterrupt):
            try:
                print('Shutting Down, please wait and do not press anything..')

            finally:
                print('*** Current USDT Allocation:', assets, '***')
                print('Saving files..')
                putUSDTToBasket(coin + '.txt', assets)
                print('Files saved.')
                exit('Shut down complete.')


if __name__ == '__main__':
    symbol =  input('Enter Coin Ticker:').upper()
    startUSDT = input('Enter beginning USDT')

    lubinance(symbol, startUSDT)

