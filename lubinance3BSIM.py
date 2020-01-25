from interactData import *
from analyzerFunctions import *
import random
from plotly.graph_objs import Scatter, Ohlc, Figure, Layout, Candlestick
import plotly

profitPercent = 0.01
subprofitPercent = 0.006
pollingInterval = 20
dropPercent = 0.985
feePercent = 0.001

bolliDelay = 35 * 60  # 35 mins
buyBreakPercent = 1.003
buyBarrierFactor = 0.8
buyMargin = 0.9975
sellingMargin = 1.008
belowBolliPercent = 0.9995

gap = 0.995#0.9975
sellStopPercent = 0.9995#0.9991
sellLimitPercent = 0.9990#0.9986
postSellRest = 3600  # 1 hour

txFee = 0.001

counter = 7
# data = None
btcAssets = 0
assets = 100
triggerPercent = 0.003

buyDate = []
buyPriceList = []
sellDate = []
sellPriceList = []
miniSellDate = []
miniSellPrice = []

sellOrderDate = []
sellOrderStop = []
sellOrderLimit = []

buyOrderDate = []
buyOrderStop = []
buyOrderLimit = []

miniSellOrderDate = []
miniSellOrderStop = []
miniSellOrderLimit = []

cancelDate = []
cancelPrice = []

bolliThreshList = []
bolliThreshDate = []
buyBreakerDate = []
buyBreaker = []
buyBarrierDate = []
buyBarrierList = []

prevThreshDate = []
prevThreshList = []

targetDate = []
targetList = []
miniTargetDate = []
miniTargetList = []


def resetter():
    global buyDate, buyPriceList, sellDate, sellPriceList, miniSellDate, miniSellPrice
    global sellOrderDate, sellOrderStop, sellOrderLimit, buyOrderDate, buyOrderLimit
    global miniSellOrderDate, miniSellOrderLimit, miniSellOrderStop
    global bolliThreshList, bolliThreshDate, buyBreaker, buyBreakerDate, prevThreshList, prevThreshDate
    global targetDate, targetList, miniTargetDate, miniTargetList
    buyDate = []
    buyPriceList = []
    sellDate = []
    sellPriceList = []
    miniSellDate = []
    miniSellPrice = []

    sellOrderDate = []
    sellOrderStop = []
    sellOrderLimit = []

    buyOrderDate = []
    buyOrderStop = []
    buyOrderLimit = []

    miniSellOrderDate = []
    miniSellOrderStop = []
    miniSellOrderLimit = []

    cancelDate = []
    cancelPrice = []

    bolliThreshList = []
    bolliThreshDate = []
    buyBreakerDate = []
    buyBreaker = []
    buyBarrierDate = []
    buyBarrierList = []

    prevThreshDate = []
    prevThreshList = []

    targetDate = []
    targetList = []
    miniTargetDate = []
    miniTargetList = []


header = 'Date,' + \
         'Current Price,' + \
         'assets,' + \
         'btcAssets,' + \
         'Bolli Broken,' + \
         'Wait Buy Break,' + \
         'Buy Order Cancelled,' + \
         'Buy Order,' + \
         'Stop,' + \
         'Limit,' + \
         'Buy Executed,' + \
         'Buy Price,' + \
         'Target,' + \
         'Margin,' + \
         'Drop Threshold,' + \
         'Sell Order Cancelled,' + \
         'Sell Order,' + \
         'Sell Stop,' + \
         'Sell Limit,' + \
         'Sell Executed,' + \
         'Sell Price,' + \
         'Mini Sell Order Cancelled,' + \
         'Mini Sell Order,' + \
         'Mini Sell Stop,' + \
         'Mini Sell Limit,' + \
         'Mini Sell Executed,' + \
         'Mini Sell Price,' + \
         'Open Phase Entered,' + \
         'Open Phase Exited,' + \
         'Close Phase Entered,' + \
         'Close Phase Exited'


def closedPhase(client, coin, sellPrice=None, margin=None, ):
    global file
    global counter, data, btcAssets, assets
    global buyDate, buyPriceList, sellDate, sellPriceList, miniSellDate, miniSellPrice
    global sellOrderDate, sellOrderStop, sellOrderLimit, buyOrderDate, buyOrderLimit, buyOrderStop
    global miniSellOrderDate, miniSellOrderLimit, miniSellOrderStop
    global cancelDate, cancelPrice, buyBarrierDate, buyBarrierList
    global bolliThreshList, bolliThreshDate, buyBreaker, buyBreakerDate, prevThreshDate, prevThreshList

    phaseId = datetime.utcnow()

    buyPrice = None
    pair = coin + 'USDT'
    waitForBuyBreak = False
    lowThreshold = 0
    bolliDate = datetime(2019, 1, 1)
    bolliBroken = False

    nowTime = None
    dataPoints = data.iloc[(counter - 7):counter]

    if margin != None:
        # setLimitStop Buy at sellPrice
        buyPrice = sellPrice
        stopBuyTrigger = (1 - triggerPercent) * buyPrice
        # buyQty = assets / buyPrice
        # price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
        # buyOrderId = limit_buy(client, pair, quantity=quantity, price=price)
        # buyOrderId = 1

        # buyOrderDate = buyOrderDate + [dataPoints.iloc[-1].date]
        # buyOrderStop = buyOrderStop + [stopBuyTrigger]
        # buyOrderLimit = buyOrderLimit + [buyPrice]
        #
        # printerDict={}
        # printerDict['Date'] = dataPoints.iloc[-1].date
        # printerDict['assets'] = assets
        # printerDict['btcAssets'] = btcAssets
        # printerDict['Buy Order'] = True
        # printerDict['Stop'] = '%.3f'%(stopBuyTrigger)
        # printerDict['Limit'] = '%.3f'%(buyPrice)
        # printerDict['Open Phase Entered'] = phaseId
        # printer(printerDict, file=file)

    else:
        buyOrderId = None

    miniCounter = 0

    while True:
        try:

            miniCounter += 1
            miniCounter = miniCounter % (60 / pollingInterval)
            if miniCounter == 0:
                counter += 1

            dataPoints = data.iloc[(counter - 7):counter]
            if len(dataPoints) < 7:
                global finalClose

                print('-----END----', file=file)
                print('USDT', assets, file=file)
                print('Coin', btcAssets, file=file)
                print('Final Close', finalClose, file=file)
                print('TOTAL VALUE', assets + (btcAssets * finalClose), file=file)
                print(coin, 'TOTAL VALUE', assets + (btcAssets * finalClose), file=file)

                finalValue = assets + (btcAssets * finalClose)

                return 'next', finalValue

            current = dataPoints.iloc[-1]
            currentPrice = random.uniform(current.low, current.high)

            findUptrend = uptrendFinder(dataPoints.iloc[-6:-1], file)

            # if (buyOrderId!= None) and (get_order_status(client,pair,buyOrderId) == Client.ORDER_STATUS_FILLED):
            if (margin != None) and findUptrend and (currentPrice > stopBuyTrigger):
                buyPrice = currentPrice

                margin = margin + (buyPrice * feePercent)
                if margin > (0.015 * buyPrice):
                    margin = 0.015*buyPrice

                buyDate = buyDate + [current.date]
                buyPriceList = buyPriceList + [buyPrice]

                buyQty = assets / buyPrice
                btcAssets = buyQty * (1 - txFee)
                assets = 0

                # buyOrderDate = buyOrderDate + [dataPoints.iloc[-1].date]
                # buyOrderStop = buyOrderStop + [stopBuyTrigger]
                # buyOrderLimit = buyOrderLimit + [buyPrice]

                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Bolli Broken'] = bolliBroken
                printerDict['Wait Buy Break'] = waitForBuyBreak
                printerDict['Buy Executed'] = True
                printerDict['Buy Price'] = buyPrice
                printerDict['Margin'] = margin
                printerDict['Open Phase Entered'] = phaseId
                printer(printerDict, file=file)

                break

            # if fulfilled:
            #   break. margin = margin + (buyPrice*feePercent).
            #   Go to open phase.

            # dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

            # print('----- D-A-T-E ----', dataPoints.iloc[-1].date, file=file)

            # maClose = np.mean(dataPoints.iloc[-6:-1].close)
            maHigh = np.mean(dataPoints.iloc[-6:-1].high)

            # print('waitForBuyBreak:', waitForBuyBreak, file=file)

            if waitForBuyBreak:

                hourData = pd.read_csv('030619_to_060619_analysis//' + pair + '_1h.csv')
                hourData.columns = ['date', 'open', 'high', 'low', 'close', 'vol']

                hourData['date'] = [pd.to_datetime(x) for x in hourData['date']]
                hourData['low'] = [pd.to_numeric(x) for x in hourData['low']]
                hourData['high'] = [pd.to_numeric(x) for x in hourData['high']]
                hourData['open'] = [pd.to_numeric(x) for x in hourData['open']]
                hourData['close'] = [pd.to_numeric(x) for x in hourData['close']]

                hourBehind = dataPoints.iloc[-1].date - timedelta(days=1)
                whichHour = None
                for i in range(len(hourData)):
                    if hourData.iloc[i].date > hourBehind:
                        whichHour = i - 1

                        break

                hourPoint = hourData.iloc[whichHour]
                buyBarrier = (hourPoint.high - hourPoint.low) * buyBarrierFactor + hourPoint.low

                buyBreakThresh = maHigh * buyBreakPercent

                buyBreakerDate = buyBreakerDate + [current.date]
                buyBreaker = buyBreaker + [buyBreakThresh]
                buyBarrierDate = buyBarrierDate + [current.date]
                buyBarrierList = buyBarrierList + [buyBarrier]

                buyingUptrend = uptrendFinder(uptrendData=dataPoints[-5:-1], file=file)

                if (currentPrice > buyBreakThresh) and (currentPrice < buyBarrier) and buyingUptrend:
                    # put in buy limit order for currentPrice * buyBreakLimit

                    if margin != None:
                        ### CANCEL stop buy order ###
                        cancelDate = cancelDate + [current.date]
                        cancelPrice = cancelPrice + [buyPrice]

                        printerDict = {}
                        printerDict['Date'] = current.date
                        printerDict['Current Price'] = currentPrice
                        printerDict['assets'] = assets
                        printerDict['btcAssets'] = btcAssets
                        printerDict['Bolli Broken'] = bolliBroken
                        printerDict['Wait Buy Break'] = waitForBuyBreak
                        printerDict['Buy Order Cancelled'] = buyPrice
                        printerDict['Open Phase Entered'] = phaseId
                        printer(printerDict, file)

                    buyPrice = currentPrice
                    buyQty = assets / buyPrice
                    price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
                    # openBuyId = limit_buy(client, pair, quantity=quantity, price=price)

                    assets = 0
                    btcAssets = buyQty * (1 - txFee)

                    buyDate = buyDate + [current.date]
                    buyPriceList = buyPriceList + [buyPrice]
                    # print('Regular Buy Filled at price:', buyPrice, file=file)

                    waitForBuyBreak = False

                    # print('BUY AT:', buyPrice, 'buy qty:', buyQty, 'after tx fee', btcAssets, file=file)

                    break

            if dataPoints.iloc[-1].date == nowTime:
                continue

            nowTime = dataPoints.iloc[-1].date

            # print('bolliBroken:', bolliBroken, file=file)
            if bolliBroken:
                bolliTimeSince = current.date - bolliDate
                # print('Bolli Time Since:', bolliTimeSince, file=file)

                if bolliTimeSince.seconds > bolliDelay:
                    # reset
                    bolliBroken = False
                    bolliDate = datetime(2019, 1, 1)
                    lowThreshold = 0

                prevLowest = lowThreshold * buyMargin
                if prevLowest > 0:
                    prevThreshDate = prevThreshDate + [current.date]
                    prevThreshList = prevThreshList + [prevLowest]

                if currentPrice < prevLowest:
                    waitForBuyBreak = True
                    bolliBroken = False
                    bolliDate = datetime(2019, 1, 1)
                    lowThreshold = 0

            latestBolliValue = bollingerLow(dataPoints.iloc[-6:-1].close)
            latestBar = dataPoints.iloc[-2]
            latestLow = latestBar.low
            bolliThresh = latestBolliValue * belowBolliPercent

            bolliThreshDate = bolliThreshDate + [latestBar.date]
            bolliThreshList = bolliThreshList + [bolliThresh]

            if (latestLow < bolliThresh) and (latestLow != lowThreshold):
                lowThreshold = latestLow
                bolliDate = latestBar.date
                bolliBroken = True





        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                OSError) as e:

            try:
                errorHandler(e, file=file)
                time.sleep(10)
            except (KeyboardInterrupt):
                print('Saving files..', file=file)
                putUSDTToBasket(coin + '.txt', assets)
                print('Files saved.', file=file)
                exit('Shut down complete.')

        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
               BinanceOrderMinPriceException,
               BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceRequestException) as e:
            errorHandler(e, file=file)
            print("Binance API Error", file=file)

            exit(3000)

        except (KeyboardInterrupt):
            try:
                print('Shutting Down, please wait and do not press anything..', file=file)

            finally:
                print('*** Current USDT Allocation:', assets, '***', file=file)
                print('Saving files..', file=file)
                putUSDTToBasket(coin + '.txt', assets)
                print('Files saved.', file=file)
                exit('Shut down complete.')

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
        printer(printerDict, file)

    printerDict = {}
    printerDict['Date'] = current.date
    printerDict['Current Price'] = currentPrice
    printerDict['assets'] = assets
    printerDict['btcAssets'] = btcAssets
    printerDict['Bolli Broken'] = bolliBroken
    printerDict['Wait Buy Break'] = waitForBuyBreak
    printerDict['Buy Price'] = buyPrice
    printerDict['Margin'] = margin
    printerDict['Open Phase Exited'] = phaseId
    printer(printerDict, file)

    counter += 1
    result, assets = openPhase(client, coin, buyPrice, margin)

    # print('Returned to Closed Phase ID', phaseId, file=file)
    # print('', file=file)

    return result, assets


def openPhase(client, coin, buyPrice=None, margin=None, ):
    global file
    global counter, data, btcAssets, assets

    global buyDate, buyPriceList, sellDate, sellPriceList, miniSellDate, miniSellPrice
    global sellOrderDate, sellOrderStop, sellOrderLimit, buyOrderDate, buyOrderLimit, buyOrderStop
    global miniSellOrderDate, miniSellOrderLimit, miniSellOrderStop
    global cancelDate, cancelPrice, targetDate, targetList, miniTargetDate, miniTargetList
    global bolliThreshList, bolliThreshDate, buyBreaker, buyBreakerDate

    phaseId = datetime.utcnow()
    # print('Open Phase ID', phaseId, file=file)

    dataPoints = data.iloc[(counter - 7):counter]

    pair = coin + 'USDT'
    if margin == None:
        margin = profitPercent * buyPrice
    target = buyPrice + margin
    miniTarget = buyPrice * (1 + subprofitPercent)

    targetDate = targetDate + [dataPoints.iloc[-1].date]
    targetList = targetList + [target]
    miniTargetDate = miniTargetDate + [dataPoints.iloc[-1].date]
    miniTargetList = miniTargetList + [miniTarget]

    # print('buyPrice', buyPrice, 'margin', margin, 'assets', assets, 'TARGET', target, file=file)

    # set stop limit sell
    sellPrice = buyPrice * dropPercent
    sellDropStop = sellPrice * (1 + triggerPercent)
    limitPrice, sellQty = formattedPrcQty(coin, sellPrice, btcAssets)
    sellDropStopfrmtd, sellQty = formattedPrcQty(coin, sellDropStop, btcAssets)
    # sellOrderId = limit_sell(client,pair,sellQty,limitPrice) # sell limit

    # print('Drop Sell Order In At Price:', limitPrice, 'Trigger:', sellDropStop, file=file)

    sellOrderDate = sellOrderDate + [dataPoints.iloc[-1].date]
    sellOrderStop = sellOrderStop + [sellDropStop]
    sellOrderLimit = sellOrderLimit + [sellPrice]

    openSellId = None  # sell stop limit
    miniSellId = None

    miniCounter = 0

    printerDict = {}
    printerDict['Date'] = dataPoints.iloc[-1].date
    printerDict['assets'] = assets
    printerDict['btcAssets'] = btcAssets
    printerDict['Target'] = target
    printerDict['Margin'] = margin
    printerDict['Drop Threshold'] = sellDropStop
    printerDict['Close Phase Entered'] = phaseId
    printer(printerDict, file)

    while True:
        miniCounter += 1
        miniCounter = miniCounter % (60 / pollingInterval)
        if miniCounter == 0:
            counter += 1

        dataPoints = data.iloc[(counter - 7):counter]
        if len(dataPoints) < 7:
            global finalClose

            print('-----END----', file=file)
            print('USDT', assets, file=file)
            print('Coin', btcAssets, file=file)
            print('Final Close', finalClose, file=file)
            print('TOTAL VALUE', assets + (btcAssets * finalClose), file=file)
            print(coin, 'TOTAL VALUE', assets + (btcAssets * finalClose), file=file)

            finalValue = assets + (btcAssets * finalClose)

            return 'next', finalValue

        current = dataPoints.iloc[-1]
        currentPrice = random.uniform(current.low, current.high)

        # print('----- D-A-T-E ----', dataPoints.iloc[-1].date, currentPrice, file=file)

        if (currentPrice < sellDropStop):
            if openSellId != None:
                # cancel open sells

                cancelDate = cancelDate + [current.date]
                cancelPrice = cancelPrice + [sellLimit]

                printerDict = {}
                printerDict['Date'] = current.date
                printerDict['Current Price'] = currentPrice
                printerDict['assets'] = assets
                printerDict['btcAssets'] = btcAssets
                printerDict['Sell Order Cancelled'] = openSellId
                printerDict['Close Phase Entered'] = phaseId
                printer(printerDict, file)
                openSellId = None

            # sellPrice = sellLimit

            totalUSDT = sellPrice * btcAssets

            assets = (1 - txFee) * totalUSDT
            btcAssets = 0

            printerDict = {}
            printerDict['Date'] = current.date
            printerDict['Current Price'] = currentPrice
            printerDict['assets'] = assets
            printerDict['btcAssets'] = btcAssets
            printerDict['Target'] = target
            printerDict['Margin'] = margin
            printerDict['Drop Threshold'] = sellDropStop
            printerDict['Close Phase Entered'] = phaseId
            printer(printerDict, file)

            sellPrice = currentPrice
            loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
            margin = margin + loss
            # print('Drop SELL filled at price:', sellPrice, 'new margin:', margin, file=file)

            sellDate = sellDate + [current.date]
            sellPriceList = sellPriceList + [sellPrice]

            break

        if openSellId != None and (currentPrice < sellStop):
            sellPrice = sellLimit

            totalUSDT = sellPrice * btcAssets

            assets = (1 - txFee) * totalUSDT
            btcAssets = 0

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
            printer(printerDict, file)

            # print('SELL order Filled', openSellId, 'at price', sellPrice, 'Total USDT:', assets, file=file)
            # print('Closing Open Phase Id', phaseId, file=file)

            openSellId = None

            sellDate = sellDate + [current.date]
            sellPriceList = sellPriceList + [sellPrice]

            return True, assets

        if miniSellId != None and (currentPrice < miniSellStop):
            sellPrice = miniSellLimit

            totalUSDT = sellPrice * btcAssets

            assets = (1 - txFee) * totalUSDT
            btcAssets = 0

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
            printer(printerDict, file)

            # print('Mini SELL order Filled', miniSellId, 'at price', sellPrice, 'Total USDT:', assets, file=file)
            # print('Closing Open Phase Id', phaseId, file=file)

            miniSellDate = miniSellDate + [current.date]
            miniSellPrice = miniSellPrice + [sellPrice]

            openSellId = None
            miniSellId = None

            # print()
            # print('margin', margin)
            # print('buy-sell', buyPrice-sellPrice)

            loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
            margin = margin + loss

            # print('loss', loss)
            # print('newMargin', margin)

            break

        upTrendFound = uptrendFinder(dataPoints.iloc[-5:-1], file)

        # print('Date:', current.date, 'upTrend found:',upTrendFound,file=file)
        # print(dataPoints.iloc[-5:-1],file=file)

        if (not upTrendFound) and ((currentPrice * gap) > target):
            # #sellFinish

            if True:
                if miniSellId != None:
                    ## CANCEL mini sell ###
                    cancelDate = cancelDate + [current.date]
                    cancelPrice = cancelPrice + [miniSellLimit]
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

                    miniSellId = None

                if openSellId != None:
                    ### CANCEL the previous SELL STOP ###
                    cancelDate = cancelDate + [current.date]
                    cancelPrice = cancelPrice + [sellLimit]

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

                    openSellId += 1
                else:
                    openSellId = 1

                # set stop and limit
                sellStop = currentPrice * sellStopPercent
                sellLimit = currentPrice * sellLimitPercent
                stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
                limitPrice, sellQty = formattedPrcQty(coin, sellLimit, btcAssets)

                target = sellStop

                targetDate = targetDate + [dataPoints.iloc[-1].date]
                targetList = targetList + [target]

                try:

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

                    # print('Sell Stop Order Put In', 'order num', openSellId, 'stop', stopPrice, 'limit', limitPrice,
                    #       'qty', sellQty, file=file)

                    sellOrderDate = sellOrderDate + [current.date]
                    sellOrderLimit = sellOrderLimit + [sellLimit]
                    sellOrderStop = sellOrderStop + [sellStop]

                    continue
                except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                       BinanceOrderMinPriceException,
                       BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                       BinanceRequestException) as e:
                    errorHandler(e, file=file)
                    print("Binance API Error", file=file)
                    if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                        openSellId = limit_sell(client, pair, sellQty, limitPrice)
                        print('CONTINGENCY LIMIT SELL', openSellId, file=file)
                        continue
                    else:
                        exit(3000)

        else:  # (currentPrice * gap) <= target
            if (not upTrendFound) and ((currentPrice * gap) > miniTarget):
                gains, losses = gainLossCounter(data.iloc[(counter - 7):counter])
                choiceList = [True] * losses + [False] * gains
                toSellOrNotToSell = random.choice(choiceList)

                if toSellOrNotToSell:
                    if miniSellId != None:
                        ### CANCEL the previous SELL STOP ###

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

                        miniSellId += 1
                    else:
                        miniSellId = 1

                    # set stop and limit
                    miniSellStop = currentPrice * sellStopPercent
                    miniSellLimit = currentPrice * sellLimitPercent
                    stopPrice, sellQty = formattedPrcQty(coin, miniSellStop, btcAssets)
                    limitPrice, sellQty = formattedPrcQty(coin, miniSellLimit, btcAssets)

                    miniTarget = miniSellStop
                    miniTargetDate = miniTargetDate + [dataPoints.iloc[-1].date]
                    miniTargetList = miniTargetList + [miniTarget]

                    if miniTarget > target:
                        target = miniTarget
                        targetDate = targetDate + [dataPoints.iloc[-1].date]
                        targetList = targetList + [target]

                    try:

                        # print('Mini Sell Stop Order Put In', 'order num', openSellId, 'stop', stopPrice, 'limit', limitPrice,
                        #       'qty', sellQty, file=file)

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

                        miniSellOrderDate = miniSellOrderDate + [current.date]
                        miniSellOrderStop = miniSellOrderStop + [miniSellStop]
                        miniSellOrderLimit = miniSellOrderLimit + [miniSellLimit]

                        continue
                    except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                           BinanceOrderMinPriceException,
                           BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException,
                           BinanceRequestException) as e:
                        errorHandler(e, file=file)
                        print("Binance API Error", file=file)
                        if str(e).strip() == 'APIError(code=-2010): Order would trigger immediately.':
                            openSellId = limit_sell(client, pair, sellQty, limitPrice)
                            print('CONTINGENCY LIMIT SELL', openSellId, file=file)
                            continue
                        else:
                            exit(3000)

    counter += 1
    result, assets = closedPhase(client, coin, sellPrice, margin)
    print('Returned to Open Phase Id', phaseId, file=file)
    return result, assets


def lubinance(coin, interval, seed=37):
    random.seed(seed)
    pair = coin + 'USDT'
    global file
    global counter, data, finalClose, btcAssets, assets

    global buyDate, buyPriceList, sellDate, sellPriceList, miniSellDate, miniSellPrice
    global sellOrderDate, sellOrderStop, sellOrderLimit, buyOrderDate, buyOrderLimit
    global miniSellOrderDate, miniSellOrderLimit, miniSellOrderStop
    global bolliThreshList, bolliThreshDate, buyBreaker, buyBreakerDate, prevThreshList, prevThreshDate
    global targetDate, targetList, miniTargetDate, miniTargetList

    counter = 7
    resetter()

    print('Beginning Sim,', coin, 'assets', assets, 'seed', seed)
    file = open("logs//" + coin + '_' + str(seed) + '_' + interval + '_' + datetime.utcnow().strftime(
        "%d%m%y_%H:%M:%S") + ".csv", "a")
    print(header, file=file)

    # client = Client(apiK, sK)
    client = None

    data.columns = ['date', 'open', 'high', 'low', 'close', 'vol']

    data['date'] = [pd.to_datetime(x) for x in data['date']]
    data['low'] = [pd.to_numeric(x) for x in data['low']]
    data['high'] = [pd.to_numeric(x) for x in data['high']]
    data['open'] = [pd.to_numeric(x) for x in data['open']]
    data['close'] = [pd.to_numeric(x) for x in data['close']]

    length = len(data) - counter

    print('Running sim on', pair, 'data, 29 May 2019 to 31 May 2019 UTC', file=file)
    dataOpen = data.iloc[0].open
    dataClose = data.iloc[-1].close

    percentChange = 100 * (dataClose - dataOpen) / dataOpen
    print("Actual % change over period", percentChange)
    print()

    finalClose = data.iloc[-1].close

    while counter < length:

        case, assets = closedPhase(client, coin, sellPrice=None, margin=None)

        if case == 'next':
            # region: charts
            # mainData = Candlestick(open=data.open, high=data.high, low=data.low, close=data.close, x=data.date)
            #
            # bolliDate = []
            # bolliLow = []
            #
            # for i,r in data.iterrows():
            #     if i<8: continue
            #
            #     bolliDate.append(r.date)
            #     bolliLow.append(bollingerLow(data.iloc[i-5:i].close))
            #
            #
            #
            # bolliData = Scatter(name='Bolli',x=bolliDate,y=bolliLow,marker=dict(color='navy',size=4))
            # prevThreshData = Scatter(name='prevLow',x=prevThreshDate,y=prevThreshList,mode='markers',marker=dict(symbol='square',color='red',size=3))
            # buyBreakData = Scatter(name='buyBreak',x=buyBreakerDate,y=buyBreaker,mode='markers',marker=dict(symbol='square',color='brown',size=3))
            # buyBarrierData = Scatter(name='buyBar',x=buyBarrierDate,y=buyBarrierList,mode='markers',marker=dict(symbol='square',color='blue',size=3))
            # targetData =Scatter(name='target',x=targetDate,y=targetList,mode='markers',marker=dict(symbol='triangle-up',color='blue',size=4))
            # miniTargetData = Scatter(name='miniTarget',x=miniTargetDate,y=miniTargetList,mode='markers',marker=dict(symbol='triangle-up',color='pink',size=3))
            #
            # buyData = Scatter(name= 'Buy',mode='markers', marker=dict(symbol = 'circle-open-dot',color='royalblue', size=14), x=buyDate, y=buyPriceList)
            # sellData = Scatter(name='Sell',mode='markers', marker=dict(symbol='circle-open-dot',color = 'black', size=14), x=sellDate, y=sellPriceList)
            # miniSellData = Scatter(name='miniSell',mode='markers', marker=dict(symbol='circle-open-dot',color='darkgreen', size=10), x=miniSellDate, y=miniSellPrice)
            #
            # buyStopData = Scatter(name='buyStop',mode='markers', marker=dict(symbol='diamond',color='black', size=7), x=buyOrderDate, y=buyOrderStop)
            # buyLimitData = Scatter(name='buyLimit',mode='markers', marker=dict(symbol='diamond-open',color='black', size=7), x=buyOrderDate, y=buyOrderLimit)
            #
            # sellStopData = Scatter(name='sellStop',mode='markers', marker=dict(symbol='diamond',color='orange', size=7), x=sellOrderDate, y=sellOrderStop)
            # sellLimitData = Scatter(name='sellLimit',mode='markers', marker=dict(symbol='diamond-open',color='orange', size=7), x=sellOrderDate,
            #                         y=sellOrderLimit)
            #
            # miniSellStopData = Scatter(name='miniSellStop',mode='markers', marker=dict(symbol='diamond',color='red', size=7), x=miniSellOrderDate,
            #                            y=miniSellOrderStop)
            # miniSellLimitData = Scatter(name='miniSellLimit',mode='markers', marker=dict(symbol='diamond-open',color='red', size=7), x=miniSellOrderDate,
            #                             y=miniSellOrderLimit)
            #
            # cancelData = Scatter(name='cancel',mode='markers', marker=dict(color='grey', size=7,symbol='cross'), x=cancelDate, y=cancelPrice)
            #
            # majorFig = Figure(
            #     data=[mainData, bolliData,prevThreshData,buyBreakData,buyBarrierData,targetData,miniTargetData,
            #           buyData, sellData, miniSellData, buyStopData, buyLimitData, sellStopData, sellLimitData,
            #           miniSellStopData, miniSellLimitData, cancelData],
            #     layout=Layout(
            #         xaxis=dict(
            #             rangeslider=dict(
            #                 visible=False
            #             ),
            #             showgrid=True,
            #         )))
            #
            # print('printing graph...')
            # plotly.offline.plot(majorFig,
            #                     # show_link=False,
            #                     # # output_type='div',
            #                     # include_plotlyjs=False,
            #                     filename='charts//'+coin+'_'+str(seed)+'_'+ interval+ '_'+datetime.utcnow().strftime("%d%m%y_%H:%M:%S")+'.html',
            #                     auto_open=False,
            #                     config={'displaylogo': False,
            #                             'modeBarButtonsToRemove': ['sendDataToCloud', 'select2d', 'zoomIn2d',
            #                                                        'zoomOut2d',
            #                                                        'resetScale2d', 'hoverCompareCartesian',
            #                                                        'lasso2d'],
            #                             'displayModeBar': True
            #                             })
            # endregion

            return float(assets)

        print('Case Closed?', case, file=file)

        # Buffer Time
        print('Rest 1 hour', file=file)
        # print('================================', file=file)
        # time.sleep(postSellRest)
        counter += 60

    print('-----END----', file=file)
    print('USDT', assets, file=file)
    print('Coin', btcAssets, file=file)
    print('Final Close', finalClose, file=file)
    print('TOTAL VALUE', assets + (btcAssets * finalClose), file=file)
    print(coin, 'TOTAL VALUE', assets + (btcAssets * finalClose), file=file)

    finalValue = assets + (btcAssets * finalClose)

    # region: charts
    # mainData = Candlestick(open=data.open, high=data.high, low=data.low, close=data.close, x=data.date)
    #
    # bolliDate = []
    # bolliLow = []
    #
    # for i, r in data.iterrows():
    #     if i < 8: continue
    #
    #     bolliDate.append(r.date)
    #     bolliLow.append(bollingerLow(data.iloc[i - 5:i].close))
    #
    #
    # bolliData = Scatter(name='Bolli', x=bolliDate, y=bolliLow, marker=dict(color='navy', size=4))
    # prevThreshData = Scatter(name='prevLow', x=prevThreshDate, y=prevThreshList, mode='markers',
    #                          marker=dict(symbol='square', color='red', size=3))
    # buyBreakData = Scatter(name='buyBreak', x=buyBreakerDate, y=buyBreaker, mode='markers',
    #                        marker=dict(symbol='square', color='brown', size=3))
    # buyBarrierData = Scatter(name='buyBar', x=buyBarrierDate, y=buyBarrierList, mode='markers',
    #                          marker=dict(symbol='square', color='blue', size=3))
    # targetData = Scatter(name='target', x=targetDate, y=targetList, mode='markers',
    #                      marker=dict(symbol='triangle-up', color='blue', size=4))
    # miniTargetData = Scatter(name='miniTarget', x=miniTargetDate, y=miniTargetList, mode='markers',
    #                          marker=dict(symbol='triangle-up', color='pink', size=3))
    #
    # buyData = Scatter(name='Buy', mode='markers', marker=dict(symbol='circle-open-dot', color='royalblue', size=14),
    #                   x=buyDate, y=buyPriceList)
    # sellData = Scatter(name='Sell', mode='markers', marker=dict(symbol='circle-open-dot', color='black', size=14),
    #                    x=sellDate, y=sellPriceList)
    # miniSellData = Scatter(name='miniSell', mode='markers',
    #                        marker=dict(symbol='circle-open-dot', color='darkgreen', size=10), x=miniSellDate,
    #                        y=miniSellPrice)
    #
    # buyStopData = Scatter(name='buyStop', mode='markers', marker=dict(symbol='diamond', color='black', size=7),
    #                       x=buyOrderDate, y=buyOrderStop)
    # buyLimitData = Scatter(name='buyLimit', mode='markers', marker=dict(symbol='diamond-open', color='black', size=7),
    #                        x=buyOrderDate, y=buyOrderLimit)
    #
    # sellStopData = Scatter(name='sellStop', mode='markers', marker=dict(symbol='diamond', color='orange', size=7),
    #                        x=sellOrderDate, y=sellOrderStop)
    # sellLimitData = Scatter(name='sellLimit', mode='markers',
    #                         marker=dict(symbol='diamond-open', color='orange', size=7), x=sellOrderDate,
    #                         y=sellOrderLimit)
    #
    # miniSellStopData = Scatter(name='miniSellStop', mode='markers', marker=dict(symbol='diamond', color='red', size=7),
    #                            x=miniSellOrderDate,
    #                            y=miniSellOrderStop)
    # miniSellLimitData = Scatter(name='miniSellLimit', mode='markers',
    #                             marker=dict(symbol='diamond-open', color='red', size=7), x=miniSellOrderDate,
    #                             y=miniSellOrderLimit)
    #
    # cancelData = Scatter(name='cancel', mode='markers', marker=dict(color='grey', size=7, symbol='cross'), x=cancelDate,
    #                      y=cancelPrice)
    #
    # majorFig = Figure(
    #     data=[mainData, bolliData, prevThreshData, buyBreakData, buyBarrierData, targetData, miniTargetData,
    #           buyData, sellData, miniSellData, buyStopData, buyLimitData, sellStopData, sellLimitData,
    #           miniSellStopData, miniSellLimitData, cancelData],
    #     layout=Layout(
    #         xaxis=dict(
    #             rangeslider=dict(
    #                 visible=False
    #             ),
    #             showgrid=True,
    #         )))
    #
    # print('printing graph...')
    # plotly.offline.plot(majorFig,
    #                     # show_link=False,
    #                     # # output_type='div',
    #                     # include_plotlyjs=False,
    #                     filename='charts//'+coin + '_' + str(seed) + '_'+interval+ '_' + datetime.utcnow().strftime("%d%m%y_%H:%M:%S") + '.html',
    #                     auto_open=False,
    #                     config={'displaylogo': False,
    #                             'modeBarButtonsToRemove': ['sendDataToCloud', 'select2d', 'zoomIn2d',
    #                                                        'zoomOut2d',
    #                                                        'resetScale2d', 'hoverCompareCartesian',
    #                                                        'lasso2d'],
    #                             'displayModeBar': True
    #                             })
    # endregion

    return finalValue


if __name__ == '__main__':

    markets = ['LTC', 'EOS', 'XLM', 'ZEC', 'BTT', 'ETH', 'QTUM']
    # markets = ['ZEC', 'BTT', 'ETH', 'QTUM']
    seeds = [37, 12, 7, 55]
    # seeds = [7]

    intervals = [Client.KLINE_INTERVAL_1MINUTE, Client.KLINE_INTERVAL_5MINUTE, Client.KLINE_INTERVAL_15MINUTE,
                 Client.KLINE_INTERVAL_30MINUTE]
    intervals = [Client.KLINE_INTERVAL_15MINUTE]
    global data

    bigAvg=[]
    for coin in markets:
        print('MARKET', coin)

        for interval in intervals:
            print('INTERVAL', interval)
            avg = 0.0
            data = pd.read_csv('030619_to_060619_analysis//' + coin + 'USDT_' + interval + '.csv')

            for seed in seeds:
                assets = 100
                btcAssets = 0
                newValue = lubinance(coin, interval=interval, seed=seed)

                print('newValue', newValue)

                avg += newValue

            avg = (avg - (100 * len(seeds))) / (len(seeds))
            bigAvg.append(avg)
            print('Average:', avg, '%')
            print('%%%%%%%%%%%%%%%%%%%%%%%%%')
            print()
        print('TTTTTTTTTTTTTTTTTTTTTTTTT')
        print()
    print(np.mean(bigAvg))


# 0.22527134963241174

# 0.2658649653583061