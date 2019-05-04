from interactData import *
from analyzerFunctions import *




def lubinance(coin='BTC', sellingMargin=1.006, pollingInterval = 4):

    client = Client(apiK, sK)

    assets = getUSDTFromBasket(coin+'.txt')

    currentUSDT = get_asset_balance(client, 'USDT')
    currentCoin = get_asset_balance(client, coin)

    # if ((assets==0.0) and (currentCoin<2.0)) or (assets > currentUSDT):
    #     print('Error with current',coin,'basket!')
    #     print('basket value', assets, 'USDT')
    #     print('Binance Balance USDT:', currentUSDT)
    #     print('Binance Balance',coin+":",currentCoin)
    #     exit()

    btcAssets = 0
    txFee = 0.002  # 0.22%

    # bolliBreak = False
    bolliDate = datetime(2019, 1, 1)
    bolliDelay = 10 * 60  # 10 mins
    lowThreshold = 0
    belowBolliPercent = 0.9998

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

    while True:

        try:
            time.sleep(pollingInterval)

            start_time = time.time()
            pair = coin+'USDT'
            dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

            currentPrice = get_price(client,pair)

            if currentPrice == prevPrice: continue

            currentDate = datetime.utcnow()
            line = str(
                currentDate) + ' ' + coin+  ' price: '+ str(currentPrice) + ' | buy trigger: ' + str(buyTrigger) + ' | Target Sell: ' + str(highThreshold)

            print(line)
            # writeToFile(fileName,line)

            prevPrice = currentPrice

            get_asset_balance(client,'USDT')
            get_asset_balance(client,coin)

            latestBolliValue = bollingerLow(pd.to_numeric(dataPoints.iloc[-6:-1].close))
            latestBar = dataPoints.iloc[-2]
            latestLow = float(latestBar.low)
            # print('Latest Bar')
            # print(latestBar)
            # print('BolliValue:', latestBolliValue)
            # print('Bars in Calculation:')
            # print(dataPoints.iloc[-6:-1])


            # bollinger band broken
            if latestLow < (latestBolliValue * belowBolliPercent):
                # bolliBreak = True
                bolliDate = latestBar.date
                lowThreshold = latestLow
                # print('Bollinger Floor Broken, Low Threshold', lowThreshold)


            bolliTimeSince = currentDate - bolliDate
            print('Bolli Time Since:', bolliTimeSince)

            if bolliTimeSince.seconds > bolliDelay:
                bolliDate = datetime(2019, 1, 1)
                buyTrigger = 1e5
                lowThreshold = 0
                # print('bollinger RESET')

            # buy condition
            if (currentPrice > buyTrigger) and (currentPrice > lowThreshold):
                print('Price above buy trigger but also above low threshold.')
            if (bolliTimeSince.seconds < bolliDelay) and (currentPrice > buyTrigger) and (currentPrice <= lowThreshold) :
                # print('BUY ORDER TRIGGERED at trigger price:', buyTrigger)
                if assets == 0:
                    print(str(currentDate), ': no USDT to buy',coin, 'with')
                    continue

                # BUY section

                buyTime = time.time()
                buyPrice = currentPrice
                btcAssets = assets / buyPrice
                price, quantity = formattedPrcQty(coin, buyPrice, btcAssets)
                buyId = limit_buy(client,pair,quantity=quantity,price=price)

                while True:
                    time.sleep(2)
                    openOrders = get_open_orders(client,pair)
                    if len(openOrders) == 0:
                        break

                    now = time.time()
                    if (now-buyTime) > 10: # if waited more than
                        cancelled = cancel_order(client,pair,buyId)
                        btcAssets = 0
                        writeToFile(fileName,'CANCELLED BUY:'+str(currentDate)+' | price: '+str(currentPrice))
                        print('CANCELLED BUY','Price:',currentPrice)
                        print(cancelled)
                        continue




                lastBuyPrice = buyPrice
                btcAssets = get_asset_balance(client,coin)
                assets = 0
                totalUSDTtxed += btcAssets * buyPrice
                line = str(currentDate) + ' BUY AT: ' + str(buyPrice) + ' | current assets: ' + str(btcAssets) +' '+coin+' | buy trigger: '+str(buyTrigger) + ' | total USDT txed: ' + str(totalUSDTtxed)
                highThreshold = sellTriggerRatio * lastBuyPrice

                print('***')
                print(line)
                print('***')

                writeToFile(fileName,line)

                #reset
                bolliDate = datetime(2019, 1, 1)
                buyTrigger = 1e5
                lowThreshold = 0

                print('Total Txed:', totalUSDTtxed)
                print('USDT:', assets)
                print(coin, btcAssets)

                elapsed = time.time() - start_time
                print('Time Taken:', elapsed, 's')

                continue

            # enter Potential Buy Condition

            if (bolliTimeSince.seconds < bolliDelay) and (currentPrice < lowThreshold):
                buyTrigger = (1+triggerPercent) * currentPrice
                if buyTrigger > lowThreshold:
                    buyTrigger = lowThreshold
                # print('buy trigger is at', buyTrigger)

            ########################################################################

            # sell condition
            if (currentPrice < sellTrigger) and (currentPrice >= highThreshold):
                # print('SELL ORDER TRIGGERED')

                if btcAssets == 0:
                    print(str(currentDate), ': no',coin,'to sell')
                    continue


                # SELL section

                sellTime = time.time()
                sellPrice = currentPrice
                btcAssets = get_asset_balance(client,coin)
                price, quantity = formattedPrcQty(coin, sellPrice, btcAssets)
                sellId = limit_sell(client,pair,quantity=quantity,price=price)

                while True:
                    time.sleep(2)
                    openOrders = get_open_orders(client,pair)
                    if len(openOrders) == 0:
                        break

                    now = time.time()
                    if (now-sellTime) > 30: # if waited more than
                        cancelled = cancel_order(client,pair,sellId)
                        writeToFile(fileName,'CANCELLED SELL:'+str(currentDate)+' | price: '+str(currentPrice))
                        print('CANCELLED SELL','Price:',currentPrice)
                        print(cancelled)
                        continue



                assets = btcAssets * sellPrice
                assets = np.round(assets * (1 - txFee), 4)
                btcAssets = 0
                totalUSDTtxed += assets

                line = str(currentDate)+ ' SELL AT: '+str(sellPrice)+' Current Assets: '+str(assets)+' USDT'+' | target sell price: '+str(highThreshold) + ' | total USDT txed: ' + str(totalUSDTtxed)

                print('***')
                print(line)
                print('***')

                writeToFile(fileName,line)

                # reset
                sellTrigger = 0
                highThreshold = 1e5

                print('Total Txed:', totalUSDTtxed)
                print('USDT:', assets)
                print(coin, btcAssets)

                elapsed = time.time() - start_time
                print('Time Taken:', elapsed, 's')
                continue

            elif (currentPrice < (failSafePercent*lastBuyPrice)) and (lastBuyPrice!=1e5):
                print('Price FALLING TOO MUCH')
                if btcAssets == 0:
                    print(str(currentDate), ': no',coin,'to sell')
                    continue

                # SELL section

                sellTime = time.time()
                sellPrice = currentPrice
                btcAssets = get_asset_balance(client, coin)
                price, quantity = formattedPrcQty(coin, sellPrice, btcAssets)
                sellId = limit_sell(client, pair, quantity=quantity, price=price)

                while True:
                    time.sleep(2)
                    openOrders = get_open_orders(client, pair)
                    if len(openOrders) == 0:
                        break

                    now = time.time()
                    if (now - sellTime) > 30:  # if waited more than
                        cancelled = cancel_order(client, pair, sellId)
                        writeToFile(fileName, 'CANCELLED SELL:' + str(currentDate) + ' | price: ' + str(currentPrice))
                        print('CANCELLED SELL', 'Price:', currentPrice)
                        print(cancelled)
                        continue


                assets = btcAssets * sellPrice
                assets = np.round(assets * (1 - txFee), 4)
                btcAssets = 0
                totalUSDTtxed += assets

                line = str(currentDate) + ' SELL AT: ' + str(sellPrice) + ' Current Assets: ' + str(assets) + ' USDT' + ' | target sell price: ' + str(highThreshold) + ' | total USDT txed: ' + str(totalUSDTtxed)

                print('***')
                print(line)
                print('***')

                writeToFile(fileName, line)

                # reset
                sellTrigger = 0
                highThreshold = 1e5

                print('Total Txed:', totalUSDTtxed)
                print('USDT:', assets)
                print(coin, btcAssets)

                elapsed = time.time() - start_time
                print('Time Taken:', elapsed, 's')
                continue

            # Enter potential Sell Condition
            # highThreshold = sellTriggerRatio * lastBuyPrice

            # print('Target Price to Sell At:', highThreshold)

            if currentPrice > highThreshold:
                sellTrigger = (1-sellTriggerPercent) * currentPrice

                if sellTrigger < highThreshold:
                    sellTrigger = highThreshold
                # print('sell trigger is at:', sellTrigger)



            # print('--- no tx ---')
            # print('Total Txed:', totalUSDTtxed)
            # print('USDT:', assets)
            # print(coin, btcAssets)

            elapsed = time.time() - start_time
            print('Time Taken:', elapsed, 's')

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
    lubinance('ATOM')

