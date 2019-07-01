from interactData import *
from analyzerFunctions import *
import random

TRADE_INTERVAL = Client.KLINE_INTERVAL_15MINUTE
TRADE_WINDOW = '105 minutes ago UTC'

profitPercent = 0.01
subprofitPercent = 0.006
pollingInterval = 90
dropPercent = 0.985
feePercent = 0.001

bolliDelay = 35 * 60  # 35 mins
buyBreakPercent = 1.003
buyBarrierFactor = 0.8
buyMargin = 0.9975
sellingMargin = 1.008
belowBolliPercent = 0.9995
marginCapPercent = 0.015

gap = 0.9975
sellStopPercent = 0.9991
sellLimitPercent = 0.9986
postSellRest = 3600  # 1 hour

txFee = 0.001

btcAssets = 0
assets = 0
triggerPercent = 0.003

rebalancingDeviationThresh = 0.2
piePercent = 0.04

#region: logging header
header = 'Date,'+\
          'Current Price,'+ \
          'assets,' + \
          'btcAssets,' + \
          'Bolli Broken,'+\
          'Wait Buy Break,'+\
          'Buy Order Cancelled,'+\
          'Buy Order,'+\
          'Stop,'+\
          'Limit,'+\
          'Buy Executed,'+\
          'Buy Price,'+\
          'Target,'+\
    'Margin,'+\
          'Drop Threshold,'+\
          'Sell Order Cancelled,'+\
          'Sell Order,'+\
          'Sell Stop,'+\
          'Sell Limit,'+\
          'Sell Executed,'+\
          'Sell Price,'+\
'Mini Sell Order Cancelled,'+\
          'Mini Sell Order,'+\
          'Mini Sell Stop,'+\
          'Mini Sell Limit,'+\
          'Mini Sell Executed,'+\
          'Mini Sell Price,'+\
        'Open Phase Entered,' +\
    'Open Phase Exited,' +\
    'Close Phase Entered,' +\
    'Close Phase Exited'
#endregion

def closedPhase(client, coin, sellPrice=None, margin=None, ):
    global file
    global btcAssets, assets

    print('**********')
    print('***', coin, 'Closed Phase ***')
    print('**********')

    phaseId = datetime.utcnow()


    buyPrice = None
    pair = coin + 'USDT'
    waitForBuyBreak = False
    lowThreshold = 0
    bolliDate = datetime(2019, 1, 1)
    bolliBroken = False

    nowTime = None

    if margin != None:
        buyPrice = sellPrice
        stopBuyTrigger = (1-triggerPercent) * buyPrice


    else:
        buyOrderId = None



    while True:
        try:
            time.sleep(pollingInterval)


            dataPoints = getPricePanda(client, pair, TRADE_INTERVAL, TRADE_WINDOW)

            current = dataPoints.iloc[-1]
            findUptrend = uptrendFinder(dataPoints.iloc[-6:-1],file)
            currentPrice = get_price(client, pair)
            if (margin != None) and findUptrend and (currentPrice > stopBuyTrigger):

                buyPrice = currentPrice

                margin = margin + (buyPrice * feePercent)

                if margin > (marginCapPercent * buyPrice):
                    margin = marginCapPercent * buyPrice

                usdtBalance = get_asset_balance(client, 'USDT')
                if assets > usdtBalance:
                    # reset and just continue
                    waitForBuyBreak = False
                    lowThreshold = 0
                    bolliDate = datetime(2019, 1, 1)
                    bolliBroken = False
                    print('Not enough USDT to spend', file=file)
                    continue

                buyQty = assets / buyPrice
                price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
                openBuyId = limit_buy(client, pair, quantity=quantity, price=price)

                print('!!Order in!!!', openBuyId, 'price', price, 'qty', quantity)
                print('waiting for order to fill...', '| current UTC Time', datetime.utcnow())

                time.sleep(6)
                while (get_order_status(client, pair, openBuyId) != client.ORDER_STATUS_FILLED):
                    time.sleep(pollingInterval)

                btcAssets = get_asset_balance(client,coin)
                assets = 0

                #region: logging
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Bolli Broken'] = bolliBroken
                printerDict['Wait Buy Break'] = waitForBuyBreak
                printerDict['Buy Executed'] = True
                printerDict['Buy Price'] = buyPrice
                printerDict['Buy Order'] = openBuyId
                printerDict['Margin'] = margin
                printerDict['Open Phase Entered'] = phaseId
                printer(printerDict,file=file)
                #endregion

                break

            maHigh = np.mean(dataPoints.iloc[-6:-1].high)

            if waitForBuyBreak:
                hourPoint = getPricePanda(client, pair, client.KLINE_INTERVAL_1HOUR, '120 minutes ago UTC')
                hourPoint = hourPoint.iloc[0]
                buyBarrier = (hourPoint.high - hourPoint.low) * buyBarrierFactor + hourPoint.low

                buyBreakThresh = maHigh * buyBreakPercent

                buyingUptrend = uptrendFinder(uptrendData=dataPoints[-5:-1],file=file)

                if (currentPrice > buyBreakThresh) and (currentPrice < buyBarrier) and buyingUptrend:
                    # put in buy limit order for currentPrice * buyBreakLimit

                    if margin!=None:
                        #region: logging
                        printerDict={}
                        printerDict['Date'] = current.date
                        printerDict['Current Price'] = currentPrice
                        printerDict['assets'] = assets
                        printerDict['btcAssets'] = btcAssets
                        printerDict['Bolli Broken'] = bolliBroken
                        printerDict['Wait Buy Break'] = waitForBuyBreak
                        printerDict['Buy Order Cancel'] = buyPrice
                        printerDict['Open Phase Entered'] = phaseId
                        printer(printerDict,file)
                        #endregion

                    usdtBalance = get_asset_balance(client, 'USDT')
                    if assets > usdtBalance:
                        # reset and just continue
                        waitForBuyBreak = False
                        lowThreshold = 0
                        bolliDate = datetime(2019, 1, 1)
                        bolliBroken = False
                        print('Not enough USDT to spend', file=file)
                        continue

                    buyPrice = currentPrice
                    buyQty = assets / buyPrice
                    price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
                    openBuyId = limit_buy(client, pair, quantity=quantity, price=price)

                    print('!!Order in!!!', openBuyId, 'price', price, 'qty', quantity)

                    # wait for order to be filled
                    # while len(get_open_orders(client,pair))>0:
                    print('waiting for order to fill...', '| current Time', datetime.utcnow())
                    time.sleep(6)
                    while (get_order_status(client, pair, openBuyId) != client.ORDER_STATUS_FILLED):
                        time.sleep(pollingInterval)

                    assets = 0
                    btcAssets = get_asset_balance(client,coin)
                    waitForBuyBreak = False
                    break

            if dataPoints.iloc[-1].date == nowTime:
                continue

            nowTime = dataPoints.iloc[-1].date

            if bolliBroken:
                bolliTimeSince = current.date - bolliDate

                if bolliTimeSince.seconds > bolliDelay:
                    # reset
                    bolliBroken = False
                    bolliDate = datetime(2019, 1, 1)
                    lowThreshold = 0

                prevLowest = lowThreshold * buyMargin

                if currentPrice < prevLowest:
                    waitForBuyBreak = True
                    bolliBroken = False
                    bolliDate = datetime(2019, 1, 1)
                    lowThreshold = 0

            latestBolliValue = bollingerLow(dataPoints.iloc[-6:-1].close)
            latestBar = dataPoints.iloc[-2]
            latestLow = latestBar.low
            bolliThresh = latestBolliValue * belowBolliPercent

            if (latestLow < bolliThresh) and (latestLow != lowThreshold):
                lowThreshold = latestLow
                bolliDate = latestBar.date
                bolliBroken = True

        # except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
        #         OSError) as e:
        #
        #     try:
        #         errorHandler(e, file=file)
        #         time.sleep(10)
        #     except (KeyboardInterrupt):
        #         print('Saving files..', file=file)
        #         # putUSDTToBasket(coin + '.txt', assets)
        #         # print('Files saved.', file=file)
        #         exit('Shut down complete.')

        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
               BinanceOrderMinPriceException,
               BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceRequestException) as e:
            errorHandler(e, file=file)
            print("Binance API Error",e, file=file)

            exit(3000)

        except (KeyboardInterrupt):
            try:
                print('Shutting Down, please wait and do not press anything..', file=file)

            finally:
                print('*** Current USDT Allocation:', assets, '***', file=file)
                print('Saving files..', file=file)
                # putUSDTToBasket(coin + '.txt', assets)
                # print('Files saved.', file=file)
                exit('Shut down complete.')

        #region: logging
        printerDict = {}
        printerDict['Date'] = current.date
        printerDict['Current Price'] = currentPrice
        printerDict['assets'] = assets
        printerDict['btcAssets'] = btcAssets
        printerDict['Bolli Broken'] = bolliBroken
        printerDict['Wait Buy Break'] = waitForBuyBreak
        printerDict['Buy Price'] = buyPrice
        printerDict['Margin'] = margin
        printerDict['Open Phase Entered'] = phaseId
        printer(printerDict,file)
        #endregion

    #region: logging
    printerDict={}
    printerDict['Date'] = current.date
    printerDict['Current Price'] = currentPrice
    printerDict['assets'] = assets
    printerDict['btcAssets'] = btcAssets
    printerDict['Bolli Broken'] = bolliBroken
    printerDict['Wait Buy Break'] = waitForBuyBreak
    printerDict['Buy Price'] = buyPrice
    printerDict['Margin'] = margin
    printerDict['Open Phase Exited'] = phaseId
    printer(printerDict,file)
    #endregion

    result, assets = openPhase(client, coin, buyPrice, margin)

    return result, assets


def openPhase(client, coin, buyPrice=None, margin=None, ):
    global file
    global btcAssets, assets

    print('**********')
    print('***', coin, 'Open Phase ***')
    print('**********')

    pair = coin + 'USDT'
    phaseId = datetime.utcnow()
    dataPoints = getPricePanda(client, pair, TRADE_INTERVAL, TRADE_WINDOW)

    if margin == None:
        margin = profitPercent * buyPrice
    target = buyPrice + margin
    miniTarget = buyPrice * (1+subprofitPercent)

    btcAssets = get_asset_balance(client,coin)

    # region: set stop limit sell
    sellPrice = buyPrice * dropPercent
    sellDropStop = sellPrice * (1 + triggerPercent)
    limitPrice, sellQty = formattedPrcQty(coin, sellPrice, btcAssets)
    sellDropStopfrmtd = formattedPrcQty(coin, sellDropStop)

    print('==== BTC ASSETS ====', btcAssets)
    print('==== sellQty =======', sellQty)


    try:
        stopSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=sellDropStopfrmtd, limitprice=limitPrice)
        print('!! Exit S-E-L-L order in !!', 'order num', stopSellId, 'stop', sellDropStopfrmtd, 'limit', limitPrice,
              'qty', sellQty)

    except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
           BinanceOrderMinPriceException,
           BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
           BinanceRequestException) as e:
        print(e)
        print("Binance API Error",e,file=file)
        if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
            stopSellId = limit_sell(client, pair, sellQty, limitPrice)
            print('LIMIT SELL', stopSellId)
        else:
            exit(3000)
    #endregion

    openSellId = None  # sell stop limit
    miniSellId = None

    #region:logging
    printerDict = {}
    printerDict['Date'] = dataPoints.iloc[-1].date
    printerDict['assets'] = assets
    printerDict['btcAssets'] = btcAssets
    printerDict['Target'] = target
    printerDict['Margin'] = margin
    printerDict['Drop Threshold'] = sellDropStop
    printerDict['Close Phase Entered'] = phaseId
    printer(printerDict,file)
    #endregion

    while True:
        time.sleep(pollingInterval)
        dataPoints = getPricePanda(client, pair, TRADE_INTERVAL, TRADE_WINDOW)
        current = dataPoints.iloc[-1]
        currentPrice = get_price(client,pair)

        if (get_order_status(client,pair,stopSellId) == Client.ORDER_STATUS_FILLED):
            print("Exit Sell Completed", stopSellId)
            if openSellId!=None:
                #cancel open sells

                cancel_order(client,pair,openSellId)
                print('Main Sell Cancelled', openSellId)
                #region: logging
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Sell Order Cancelled'] = openSellId
                printerDict['Close Phase Entered'] = phaseId
                printer(printerDict, file)
                openSellId = None
                #endregion

            if miniSellId!=None:
                #cancel open sells

                cancel_order(client,pair,miniSellId)
                print('mini Sell Cancelled', miniSellId)
                #region: logging
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Mini Sell Order Cancelled'] = miniSellId
                printerDict['Close Phase Entered'] = phaseId
                printer(printerDict, file)
                miniSellId = None
                #endregion


            sellPrice, totalUSDT = get_order_price_cumQty(client,pair,stopSellId)

            assets = (1 - txFee) * totalUSDT
            btcAssets = 0

            loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
            margin = margin + loss

            #region: logging
            printerDict = {}
            printerDict['Date'] = current.date
            printerDict['Current Price'] = currentPrice
            printerDict['assets'] = assets
            printerDict['btcAssets'] = btcAssets
            printerDict['Target'] = target
            printerDict['Margin'] = margin
            printerDict['Drop Threshold'] = sellDropStop
            printerDict['Close Phase Entered'] = phaseId
            printer(printerDict,file)
            #endregion

            break

        if openSellId!=None:
            if (get_order_status(client,pair,openSellId) == Client.ORDER_STATUS_FILLED):
                sellPrice, totalUSDT = get_order_price_cumQty(client, pair, openSellId)

                assets = (1 - txFee) * totalUSDT
                btcAssets = 0
                #region: loggig
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Sell Executed'] = True
                printerDict['Sell Price'] = sellPrice
                printerDict['Close Phase Exited'] = phaseId
                printerDict['Target'] = target
                printerDict['Margin'] = margin
                printer(printerDict,file)
                #endregion
                openSellId = None

                return True, assets

        if miniSellId != None:
            if (get_order_status(client,pair,miniSellId) == Client.ORDER_STATUS_FILLED):
                sellPrice, totalUSDT = get_order_price_cumQty(client, pair, miniSellId)

                assets = (1 - txFee) * totalUSDT
                btcAssets = 0
                loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
                margin = margin + loss

                #region: logging
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Mini Sell Executed'] = True
                printerDict['Mini Sell Price'] = sellPrice
                printerDict['Close Phase Exited'] = phaseId
                printerDict['Target'] = target
                printerDict['Margin'] = margin
                printer(printerDict,file)
                #endregion

                openSellId = None
                miniSellId = None

                break

        upTrendFound = uptrendFinder(dataPoints.iloc[-5:-1],file)

        if (not upTrendFound) and ((currentPrice * gap) > target):
            # #sellFinish

            if miniSellId != None:
                ## CANCEL mini sell ###
                cancel_order(client,pair,miniSellId)
                miniSellId = None
                #region: logging
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Target'] = target
                printerDict['Margin'] = margin
                printerDict['Drop Threshold'] = sellDropStop
                printerDict['Mini Sell Order Cancelled'] = miniSellId
                printerDict['Close Phase Entered'] = phaseId
                printer(printerDict, file)
                #endregion


            if openSellId != None:
                ### CANCEL the previous SELL STOP ###
                cancel_order(client,pair,openSellId)
                openSellId = None
                #region: logging
                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Target'] = target
                printerDict['Margin'] = margin
                printerDict['Drop Threshold'] = sellDropStop
                printerDict['Sell Order Cancelled'] = openSellId
                printerDict['Close Phase Entered'] = phaseId
                printer(printerDict, file)
                #endregion

            # Cancel exit drop stop
            stopSellStatus = get_order_status(client, pair, stopSellId)
            if (stopSellStatus!=Client.ORDER_STATUS_FILLED) and (stopSellStatus!=Client.ORDER_STATUS_CANCELED):
                cancel_order(client,pair,stopSellId)
                print("Exit Sell Cancelled", stopSellId)

            # set stop and limit

            # region: set stop limit sell
            sellStop = currentPrice * sellStopPercent
            sellLimit = currentPrice * sellLimitPercent
            stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
            limitPrice = formattedPrcQty(coin, sellLimit)

            try:
                openSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                                             limitprice=limitPrice)
                print('!! MAIN S-E-L-L !!', 'order num', openSellId, 'stop', stopPrice, 'limit', limitPrice,
                      'qty', sellQty)

            except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                   BinanceOrderMinPriceException,
                   BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                   BinanceRequestException) as e:
                print(e)
                print("Binance API Error",e,file=file)
                if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                    openSellId = limit_sell(client, pair, sellQty, limitPrice)
                    print('MAIN LIMIT SELL', openSellId)
                else:
                    exit(3000)
            # endregion

            target = sellStop
            #region: logging
            printerDict = {}
            printerDict['Date'] = current.date
            printerDict['Current Price'] = currentPrice
            printerDict['assets'] = assets
            printerDict['btcAssets'] = btcAssets
            printerDict['Sell Order'] = True
            printerDict['Sell Stop'] = sellStop
            printerDict['Sell Limit'] = sellLimit
            printerDict['Close Phase Entered'] = phaseId
            printerDict['Target'] = target
            printerDict['Margin'] = margin
            printer(printerDict, file)
            #endregion


        else: # (currentPrice * gap) <= target
            if (not upTrendFound) and ((currentPrice*gap) > miniTarget):
                gains, losses = gainLossCounter(dataPoints[:-1])
                choiceList = [True]*losses + [False] * gains
                toSellOrNotToSell = random.choice(choiceList)

                if toSellOrNotToSell:
                    if miniSellId != None:
                        ### CANCEL the previous SELL STOP ###
                        cancel_order(client,pair,miniSellId)
                        #region: logging
                        printerDict = {}
                        printerDict['Date'] = current.date
                        printerDict['Current Price'] = currentPrice
                        printerDict['assets'] = assets
                        printerDict['btcAssets'] = btcAssets
                        printerDict['Target'] = target
                        printerDict['Margin'] = margin
                        printerDict['Drop Threshold'] = sellDropStop
                        printerDict['Mini Sell Order Cancelled'] = miniSellId
                        printerDict['Close Phase Entered'] = phaseId
                        printer(printerDict, file)
                        #endregion

                    if openSellId != None:
                        ### CANCEL the previous SELL STOP ###
                        cancel_order(client, pair, openSellId)
                        openSellId = None
                        # region: logging
                        printerDict = {}
                        printerDict['Date'] = current.date
                        printerDict['Current Price'] = currentPrice
                        printerDict['assets'] = assets
                        printerDict['btcAssets'] = btcAssets
                        printerDict['Target'] = target
                        printerDict['Margin'] = margin
                        printerDict['Drop Threshold'] = sellDropStop
                        printerDict['Sell Order Cancelled'] = openSellId
                        printerDict['Close Phase Entered'] = phaseId
                        printer(printerDict, file)
                        # endregion

                    # Cancel exit drop stop
                    stopSellStatus = get_order_status(client, pair, stopSellId)
                    if (stopSellStatus != Client.ORDER_STATUS_FILLED) and (stopSellStatus != Client.ORDER_STATUS_CANCELED):
                        cancel_order(client, pair, stopSellId)
                        print("Exit Sell Cancelled", stopSellId)

                    # region: set stop limit sell
                    miniSellStop = currentPrice * sellStopPercent
                    miniSellLimit = currentPrice * sellLimitPercent
                    stopPrice, sellQty = formattedPrcQty(coin, miniSellStop, btcAssets)
                    limitPrice = formattedPrcQty(coin, miniSellLimit)

                    try:
                        miniSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                                                     limitprice=limitPrice)
                        print('!! mini S-E-L-L !!', 'order num', miniSellId, 'stop', stopPrice, 'limit', limitPrice,
                              'qty', sellQty)

                    except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                           BinanceOrderMinPriceException,
                           BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                           BinanceRequestException) as e:
                        print(e)
                        print("Binance API Error",e,file=file)
                        if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                            miniSellId = limit_sell(client, pair, sellQty, limitPrice)
                            print('mini LIMIT SELL', miniSellId)
                        else:
                            exit(3000)
                    # endregion


                    miniTarget = miniSellStop

                    if miniTarget > target:
                        target = miniTarget
                    #region: logging
                    printerDict = {}
                    printerDict['Date'] = current.date
                    printerDict['Current Price'] = currentPrice
                    printerDict['assets'] = assets
                    printerDict['btcAssets'] = btcAssets
                    printerDict['Mini Sell Order'] = True
                    printerDict['Mini Sell Stop'] = miniSellStop
                    printerDict['Mini Sell Limit'] = miniSellLimit
                    printerDict['Close Phase Entered'] = phaseId
                    printerDict['Target'] = target
                    printerDict['Margin'] = margin
                    printer(printerDict, file)
                    #endregion
                    continue



    result, assets = closedPhase(client, coin, sellPrice, margin)
    print('Returned to Open Phase Id', phaseId, file=file)
    return result, assets


def lubinance(coin):


    print('**********')
    print('***', coin, '***')
    print('**********')

    # random.seed(seed)
    pair = coin + 'USDT'
    global file
    global btcAssets, assets



    file = open("logs//" + coin + '_' + datetime.utcnow().strftime("%d%m%y_%H:%M:%S") + ".csv", "a")
    print(header,file=file)

    client = Client(apiK, sK)

    assets = pieChunk(client,piePercent=piePercent)
    initial_assets = assets

    print('Initial USDT', assets)
    print('Initial USDT', assets,file=file)
    while True:

        case, assets = closedPhase(client, coin, sellPrice=None, margin=None)

        print('Current USDT', assets)
        print('Current USDT', assets,file=file)

        #region: Rebalancing
        if (np.abs(assets-initial_assets)/initial_assets) > rebalancingDeviationThresh:
            assets = pieChunk(client, piePercent=piePercent)
            print('Rebalancing. USDT:',assets)
            print('Rebalancing. USDT:', assets, file=file)
        #endregion

        # Buffer Time
        print('Rest 1 hour', file=file)
        time.sleep(postSellRest)
        print()





    return



if __name__ == '__main__':
    inputs = sys.argv

    symbol = inputs[1].upper()


    lubinance(coin=symbol)



