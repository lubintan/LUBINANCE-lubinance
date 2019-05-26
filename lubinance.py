from interactData import *
from analyzerFunctions import *




def lubinance(coin='BTC', buyMargin = 0.9975,sellingMargin=1.007,pollingInterval = 20):

    client = Client(apiK, sK)

    assets = getUSDTFromBasket(coin+'.txt')

    btcAssets = 0
    txFee = 0.002  # 0.22%

    # bolliBreak = False
    bolliDate = datetime(2019, 1, 1)
    bolliDelay = 35 * 60  # 35 mins
    lowThreshold = 0
    belowBolliPercent = 0.9995

    triggerPercent = 0.00001
    buyTrigger = 1e5
    lastBuyPrice = 1e5

    sellTriggerRatio = sellingMargin
    sellTriggerPercent = 0.00001
    sellTrigger = 0

    totalUSDTtxed = 0
    prevPrice = 0

    highThreshold = 1e5

    failSafePercent = 0.8 #lose at most 20%

    fileName = coin+'txLog_'+datetime.utcnow().strftime("%y%m%d_%H:%M:%S")+'.txt'
    pair = coin + 'USDT'

    openBuyId = None
    openSellId = None

    longPosition = False

    #check for outstanding orders
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


    #check how much you have
    btcAssets = get_asset_balance(client,coin)
    if btcAssets < 0.001:
        longPosition = False
        print('Currently not holding', coin,'. Starting with USDT.')
    else:
        longPosition = True
        print('Currently holding',btcAssets,coin)


    while True:
        try:
            time.sleep(pollingInterval)

            if longPosition == True:

                # wait for sell order to fill
                sellStatus = get_order_status(client, pair, openSellId)

                if sellStatus!='FILLED':
                    continue

                else:
                    start_time = time.time()
                    sellPrice, assets = get_order_price_cumQty(client, pair, openSellId)
                    btcAssets = get_asset_balance(client, coin)
                    openSellId = None
                    longPosition = False
                    elapsed = time.time() - start_time

                    line = str(currentDate) + ' SELL AT: ' + str(sellPrice) + ' Current Assets: ' + str(assets) + ' USDT'
                    print('***')
                    print(line)
                    print('***')

                    print('Time Taken:', elapsed, 's')
                    continue

            # long position == False

            start_time = time.time()
            dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

            currentPrice = get_price(client, pair)
            currentDate = datetime.utcnow()
            line = str(
                currentDate) + ' ' + coin + ' price: ' + str(currentPrice) + ' | buy trigger: ' + str(
                lowThreshold * buyMargin) + ' | Target Sell: ' + str(highThreshold)

            print(line)

            print('| openBuyId:', openBuyId, '| openSellId:',openSellId,'| long position:',longPosition)

            latestBolliValue = bollingerLow(pd.to_numeric(dataPoints.iloc[-6:-1].close))
            latestBar = dataPoints.iloc[-2]
            latestLow = float(latestBar.low)

            # bollinger band broken
            if (latestLow < (latestBolliValue * belowBolliPercent) and (latestLow != lowThreshold)):
                if assets < 1:
                    print(str(currentDate), ': no USDT to buy', coin, 'with')
                    continue



                if openBuyId != None:
                    status = get_order_status(client, pair, openBuyId)
                    if status != 'FILLED':
                        cancelled = cancel_order(client, pair, openBuyId)
                        time.sleep(0.3)
                        cancelStatus = get_order_status(client, pair, openBuyId)

                        if cancelStatus == 'CANCELED':
                            print('CANCELLED BUY', 'ID', cancelled)
                            openBuyId = None
                            longPosition = False
                        elif cancelStatus == 'FILLED':
                            # go on to buy settings

                            lastBuyPrice = buyPrice
                            btcAssets = get_asset_balance(client, coin)
                            assets = 0

                            highThreshold = sellTriggerRatio * lastBuyPrice

                            line = str(currentDate) + ' BUY AT: ' + str(buyPrice) + ' | current assets: ' + str(
                                btcAssets) + ' ' + coin + 'sell trigger now at: ' + str(highThreshold)

                            print('***')
                            print(line)
                            print('***')

                            # reset
                            bolliDate = datetime(2019, 1, 1)
                            buyTrigger = 1e5
                            lowThreshold = 0
                            openBuyId = None
                            longPosition = True

                            # now put in sell limit order

                            price, quantity = formattedPrcQty(coin, highThreshold, btcAssets)
                            openSellId = limit_sell(client, pair, quantity=quantity, price=price)

                            elapsed = time.time() - start_time
                            print('Time Taken:', elapsed, 's')

                            continue


                        else:
                            # skip and go on to next iteration
                            continue

                    elif status == 'FILLED':
                        # go on to buy settings

                        lastBuyPrice = buyPrice
                        btcAssets = get_asset_balance(client, coin)
                        assets = 0

                        highThreshold = sellTriggerRatio * lastBuyPrice

                        line = str(currentDate) + ' BUY AT: ' + str(buyPrice) + ' | current assets: ' + str(
                            btcAssets) + ' ' + coin + 'sell trigger now at: ' + str(highThreshold)

                        print('***')
                        print(line)
                        print('***')

                        # reset
                        bolliDate = datetime(2019, 1, 1)
                        buyTrigger = 1e5
                        lowThreshold = 0
                        openBuyId = None
                        longPosition = True

                        # now put in sell limit order

                        price, quantity = formattedPrcQty(coin, highThreshold, btcAssets)
                        openSellId = limit_sell(client, pair, quantity=quantity, price=price)

                        elapsed = time.time() - start_time
                        print('Time Taken:', elapsed, 's')

                        continue

                # after previous open buy is cancelled
                if openBuyId == None:
                    # put in buy limit order

                    order = get_open_orders(client,pair)

                    if len(order) == 0:

                        bolliDate = latestBar.date
                        lowThreshold = latestLow

                        buyPrice = lowThreshold * buyMargin
                        btcAssets = assets / buyPrice
                        price, quantity = formattedPrcQty(coin, buyPrice, btcAssets)
                        openBuyId = limit_buy(client, pair, quantity=quantity, price=price)

                        print('Put in Buy Order',openBuyId,'at',price)
                        time.sleep(62-pollingInterval)
                        continue

                    else:
                        print('openBuyId', openBuyId, ', but still got open orders')
                        for each in order:
                            print(each)

            # if waited too long
            bolliTimeSince = currentDate - bolliDate
            print('Bolli Time Since:', bolliTimeSince)

            if bolliTimeSince.seconds > bolliDelay:

                if openBuyId != None:
                    print('--- WAITED TOO LONG ---')

                    status = get_order_status(client, pair, openBuyId)
                    if status != 'FILLED':
                        cancelled = cancel_order(client, pair, openBuyId)
                        time.sleep(0.3)
                        cancelStatus = get_order_status(client, pair, openBuyId)

                        if cancelStatus == 'CANCELED':
                            print('CANCELLED BUY', 'ID:', cancelled)
                            openBuyId = None
                            longPosition = False
                        elif cancelStatus == 'FILLED':
                            # go on to buy settings

                            lastBuyPrice = buyPrice
                            btcAssets = get_asset_balance(client, coin)
                            assets = 0

                            highThreshold = sellTriggerRatio * lastBuyPrice

                            line = str(currentDate) + ' BUY AT: ' + str(buyPrice) + ' | current assets: ' + str(
                                btcAssets) + ' ' + coin + 'sell trigger now at: ' + str(highThreshold)

                            print('***')
                            print(line)
                            print('***')

                            # reset
                            bolliDate = datetime(2019, 1, 1)
                            buyTrigger = 1e5
                            lowThreshold = 0
                            openBuyId = None
                            longPosition = True

                            # now put in sell limit order

                            price, quantity = formattedPrcQty(coin, highThreshold, btcAssets)
                            openSellId = limit_sell(client, pair, quantity=quantity, price=price)

                            elapsed = time.time() - start_time
                            print('Time Taken:', elapsed, 's')

                            continue

                        else:
                            # skip and go on to next iteration
                            continue



###########################################################################################################

            # elif (currentPrice < (failSafePercent*lastBuyPrice)) and (lastBuyPrice!=1e5):
            #     print('Price FALLING TOO MUCH')
            #     if btcAssets == 0:
            #         print(str(currentDate), ': no',coin,'to sell')
            #         continue
            #
            #     # SELL section
            #
            #     sellTime = time.time()
            #     sellPrice = currentPrice
            #     btcAssets = get_asset_balance(client, coin)
            #     price, quantity = formattedPrcQty(coin, sellPrice, btcAssets)
            #     sellId = limit_sell(client, pair, quantity=quantity, price=price)
            #
            #     while True:
            #         time.sleep(2)
            #         openOrders = get_open_orders(client, pair)
            #         if len(openOrders) == 0:
            #             break
            #
            #         now = time.time()
            #         if (now - sellTime) > 30:  # if waited more than
            #             cancelled = cancel_order(client, pair, sellId)
            #             writeToFile(fileName, 'CANCELLED SELL:' + str(currentDate) + ' | price: ' + str(currentPrice))
            #             print('CANCELLED SELL', 'Price:', currentPrice)
            #             print(cancelled)
            #             continue
            #
            #
            #     assets = btcAssets * sellPrice
            #     assets = np.round(assets * (1 - txFee), 4)
            #     btcAssets = 0
            #     totalUSDTtxed += assets
            #
            #     line = str(currentDate) + ' SELL AT: ' + str(sellPrice) + ' Current Assets: ' + str(assets) + ' USDT' + ' | target sell price: ' + str(highThreshold) + ' | total USDT txed: ' + str(totalUSDTtxed)
            #
            #     print('***')
            #     print(line)
            #     print('***')
            #
            #     writeToFile(fileName, line)
            #
            #     # reset
            #     sellTrigger = 0
            #     highThreshold = 1e5
            #
            #     print('Total Txed:', totalUSDTtxed)
            #     print('USDT:', assets)
            #     print(coin, btcAssets)
            #
            #     elapsed = time.time() - start_time
            #     print('Time Taken:', elapsed, 's')
            #     continue

        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                OSError, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
                BinanceOrderMinPriceException,
                BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceRequestException) as e:

            try:
                errorHandler(e)
                time.sleep(10)
            except (KeyboardInterrupt):
                print('Saving files..')
                putUSDTToBasket(coin+'.txt',assets)
                print('Files saved.')
                exit('Shut down complete.')


        except (KeyboardInterrupt):
            try:
                print('Shutting Down, please wait and do not press anything..')

            finally:
                print('Saving files..')
                putUSDTToBasket(coin + '.txt', assets)
                print('Files saved.')
                exit('Shut down complete.')


if __name__ == '__main__':
    lubinance('ETH')

