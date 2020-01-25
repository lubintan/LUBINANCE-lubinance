from interactData import *
from analyzerFunctions import *
import random



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

txFee = 0.001

counter = 7
data = None
btcAssets = 0

def closedPhase(client, coin, sellPrice=None, margin=None, assets=0):
    global file
    global counter, data, btcAssets

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
        buyQty = assets / buyPrice
        price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
        # buyOrderId = limit_buy(client, pair, quantity=quantity, price=price)
        buyOrderId = 1

        print('Waiting for Buy Order to Fill, price:',buyPrice,file=file)

    else:
        buyOrderId = None

    miniCounter = 0

    while True:
        try:

            miniCounter+=1
            miniCounter = miniCounter % (60/pollingInterval)
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
                print(coin, 'TOTAL VALUE', assets + (btcAssets * finalClose))

                finalValue = assets + (btcAssets * finalClose)
                return 'next', finalValue

            current = dataPoints.iloc[-1]
            currentPrice = random.uniform(current.low, current.high)

            # if (buyOrderId!= None) and (get_order_status(client,pair,buyOrderId) == Client.ORDER_STATUS_FILLED):
            if (buyOrderId!= None) and (currentPrice < buyPrice):
                margin = margin + (buyPrice*feePercent)

                print('Regain Buy Filled at price:', buyPrice,file=file)

                break

            # if fulfilled:
            #   break. margin = margin + (buyPrice*feePercent).
            #   Go to open phase.

            # dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')


            print('----- D-A-T-E ----', dataPoints.iloc[-1].date,file=file)

            # maClose = np.mean(dataPoints.iloc[-6:-1].close)
            maHigh = np.mean(dataPoints.iloc[-6:-1].high)


            print('waitForBuyBreak:', waitForBuyBreak,file=file)

            if waitForBuyBreak:

                hourData = pd.read_csv('290519 _to_310519_analysis_lubinance2//'+pair+'_1h.csv')
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
                        whichHour = i-1
                        break

                hourPoint = hourData.iloc[whichHour]
                buyBarrier = (hourPoint.high - hourPoint.low) * buyBarrierFactor + hourPoint.low

                buyBreakThresh = maHigh * buyBreakPercent
                print('buyBreakThresh', buyBreakThresh, 'buyBarrier', buyBarrier,file=file)

                if (currentPrice > buyBreakThresh) and (currentPrice < buyBarrier):
                    # put in buy limit order for currentPrice * buyBreakLimit
                    buyPrice = maHigh * (buyBreakPercent + 0.0007)
                    buyQty = assets / buyPrice
                    price, quantity = formattedPrcQty(coin, price=buyPrice, quantity=buyQty)
                    # openBuyId = limit_buy(client, pair, quantity=quantity, price=price)

                    assets = 0
                    btcAssets = buyQty * (1-txFee)

                    print('Regular Buy Filled at price:', buyPrice,file=file)

                    waitForBuyBreak = False



                    print('BUY AT:', buyPrice, 'buy qty:', buyQty, 'after tx fee', btcAssets, file=file)

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

    result, assets = openPhase(client,coin,buyPrice,margin,assets)

    print('Returned to Closed Phase ID', phaseId,file=file)
    print('',file=file)
    return result, assets



def openPhase(client, coin, buyPrice=None, margin=None,assets=0):
    global file
    global counter, data, btcAssets

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
    limitPrice, sellQty = formattedPrcQty(coin, sellPrice, btcAssets)
    limitPrice, sellQty = formattedPrcQty(coin, sellDropStop, btcAssets)
    # sellOrderId = limit_sell(client,pair,sellQty,limitPrice) # sell limit

    print('Drop Sell Order In At Price:', limitPrice,'Trigger:',sellDropStop,file=file)

    openSellId = None # sell stop limit

    miniCounter = 0
    while True:
        miniCounter += 1
        miniCounter = miniCounter % (60 / pollingInterval)
        if miniCounter == 0:
            counter += 1


        dataPoints = data.iloc[(counter - 7):counter]
        if len(dataPoints) < 7:
            global finalClose

            print('-----END----',file=file)
            print('USDT',assets,file=file )
            print('Coin', btcAssets,file=file)
            print('Final Close', finalClose,file=file)
            print('TOTAL VALUE', assets + (btcAssets*finalClose), file=file)
            print(coin,'TOTAL VALUE', assets + (btcAssets*finalClose))

            finalValue = assets + (btcAssets * finalClose)
            return 'next', finalValue

        current = dataPoints.iloc[-1]
        currentPrice = random.uniform(current.low, current.high)

        print('----- D-A-T-E ----', dataPoints.iloc[-1].date,file=file)


        if (currentPrice < sellDropStop):
            loss = (sellDropStop * feePercent) + (buyPrice - sellDropStop)
            margin = margin + loss
            print('Drop SELL filled at price:', sellPrice, 'new margin:', margin,file=file)

            break


        if (currentPrice * gap) > target:
            # #sellFinish
            uptrendData = dataPoints.iloc[-4:-1]
            uptrendFound = uptrendFinder(uptrendData,file)

            print('uptrend found?', uptrendFound,file=file)
            # check that last 4 all above each other
            if uptrendFound:
                if openSellId==None:

                    # set stop and limit
                    sellStop = currentPrice * sellStopPercent
                    sellLimit = currentPrice * sellLimitPercent
                    stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
                    limitPrice, sellQty = formattedPrcQty(coin, sellLimit, btcAssets)

                    try:
                        # if get_order_status(client,pair,sellOrderId) != Client.ORDER_STATUS_FILLED:
                        #     cancel_order(client,pair,sellOrderId)
                        #     print('Drop SELL CANCELLED',file=file)
                        # else:
                        #     loss = (sellPrice * feePercent) + (buyPrice - sellPrice)
                        #     margin = margin + loss
                        #     print('Last Minute Drop SELL filled at price:', sellPrice, 'new margin:', margin,file=file)
                        #     break

                        # openSellId = stop_limit_sell(client, pair, quantity=sellQty, stopprice=stopPrice,
                        #                              limitprice=limitPrice)
                        openSellId = 1
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
                    # status = get_order_status(client, pair, openSellId)
                    if ((currentPrice * gap) > target):
                        # cancel_order(client, pair, openSellId)
                        print('Drop SELL CANCELLED',file=file)
                        # set stop and limit
                        sellStop = currentPrice * sellStopPercent
                        sellLimit = currentPrice * sellLimitPercent
                        stopPrice, sellQty = formattedPrcQty(coin, sellStop, btcAssets)
                        limitPrice, sellQty = formattedPrcQty(coin, sellLimit, btcAssets)
                        try:
                            openSellId += 1

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

                    elif currentPrice < sellStop:

                        sellPrice = sellLimit


                        totalUSDT = sellPrice * btcAssets

                        assets = (1 - txFee) * totalUSDT
                        btcAssets = 0

                        print('SELL order Filled', openSellId, 'at price', sellPrice, 'Total USDT:', assets,file=file)
                        print('Closing Open Phase Id',phaseId,file=file)
                        return True,assets




    result, assets = closedPhase(client,coin,sellPrice,margin,assets)
    print('Returned to Open Phase Id', phaseId,file=file)

    return result, assets




def lubinance(coin, assets=100, seed=37):

    random.seed(seed)
    pair = coin + 'USDT'
    global file
    global counter, data, finalClose, btcAssets

    counter = 7
    data = None
    btcAssets = 0

    print('Beginning Sim,',coin,'assets',assets,'seed',seed)
    file = open("logs//"+pair+datetime.utcnow().strftime("%d%m%y_%H:%M:%S") +".txt", "a")
    # client = Client(apiK, sK)
    client = None


    data = pd.read_csv('290519 _to_310519_analysis_lubinance2//' + pair + '_1m.csv')
    data.columns = ['date','open','high','low','close','vol']


    data['date'] = [pd.to_datetime(x) for x in data['date']]
    data['low'] = [pd.to_numeric(x) for x in data['low']]
    data['high'] = [pd.to_numeric(x) for x in data['high']]
    data['open'] = [pd.to_numeric(x) for x in data['open']]
    data['close'] = [pd.to_numeric(x) for x in data['close']]
    

    length = len(data) - counter

    print('Running sim on',pair,'data, 29 May 2019 to 31 May 2019 UTC', file=file)

    finalClose = data.iloc[-1].close


    while counter < length:
        
        case, assets = closedPhase(client,coin,sellPrice=None,margin=None,assets=assets)

        print(case, assets)

        if case=='next':
            return float(assets)
        print('Case Closed?', case,file=file)

        # Buffer Time
        print('============Rest 1 hour=========',file=file)
        print('================================',file=file)
        # time.sleep(postSellRest)
        counter += 60


if __name__ == '__main__':


    markets = ['LTC', 'EOS', 'XLM', 'ZEC', 'BTT', 'ETH', 'QTUM']
    seeds = [37,12,7,55]

    for pair in markets:
        avg = 0.0
        for seed in seeds:

            newValue = lubinance(pair,assets=100,seed=seed)

            print('newValue',newValue,'avg',avg)

            avg+= newValue
        avg = (avg-400) / 4.0
        print('Average:', avg, '%')
        print()


