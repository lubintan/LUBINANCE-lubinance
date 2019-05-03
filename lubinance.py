from interactData import *
from analyzerFunctions import *




def lubinance(coin='BTC', sellingMargin=1.006, pollingInterval = 4):
    client = Client(apiK, sK)

    startingUSD = float(1e3)
    assets = startingUSD
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

    failSafePercent = 0.8 #lose at most 20%


    while True:
        time.sleep(pollingInterval)

        start_time = time.time()
        pair = coin+'USDT'
        dataPoints = getPricePanda(client, pair, client.KLINE_INTERVAL_1MINUTE, '7 minutes ago UTC')

        currentPrice = get_price(client,pair)

        if currentPrice == prevPrice: continue

        currentDate = datetime.utcnow()
        print('--------- date:',currentDate,'| price:', currentPrice, '| low thresh:', lowThreshold)

        prevPrice = currentPrice

        get_asset_balance(client,'USDT')
        get_asset_balance(client,coin)

        latestBolliValue = bollingerLow(pd.to_numeric(dataPoints.iloc[-6:-1].close))
        latestBar = dataPoints.iloc[-2]
        latestLow = float(latestBar.low)
        print('Latest Bar')
        print(latestBar)
        print('BolliValue:', latestBolliValue)
        # print('Bars in Calculation:')
        # print(dataPoints.iloc[-6:-1])


        # bollinger band broken
        if latestLow < (latestBolliValue * belowBolliPercent):
            # bolliBreak = True
            bolliDate = latestBar.date
            lowThreshold = latestLow
            print('Bollinger Floor Broken, Low Threshold', lowThreshold)


        bolliTimeSince = currentDate - bolliDate
        print('Bolli Time Since:', bolliTimeSince)

        if bolliTimeSince.seconds > bolliDelay:
            bolliDate = datetime(2019, 1, 1)
            buyTrigger = 1e5
            lowThreshold = 0
            print('bollinger RESET')

        # buy condition
        if (currentPrice > buyTrigger) and (currentPrice > lowThreshold):
            print('Price above buy trigger but also above low threshold.')
        if (bolliTimeSince.seconds < bolliDelay) and (currentPrice > buyTrigger) and (currentPrice <= lowThreshold) :
            print('BUY ORDER TRIGGERED at trigger price:', buyTrigger)
            if assets == 0:
                print(str(currentDate), ': no USDT to buy',coin, 'with')
                continue

            lastBuyPrice = currentPrice

            buyPrice = currentPrice
            btcAssets = assets / buyPrice
            btcAssets = np.round(btcAssets * (1 - txFee), 7)
            assets = 0
            totalUSDTtxed += btcAssets * buyPrice

            print('***')
            print(str(currentDate), 'BUY AT:', buyPrice, 'current assets:', btcAssets, coin)
            print('***')

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
            print('buy trigger is at', buyTrigger)

        ########################################################################

        # sell condition
        if (currentPrice < sellTrigger) and (currentPrice >= highThreshold):
            print('SELL ORDER TRIGGERED')

            if btcAssets == 0:
                print(str(currentDate), ': no',coin,'to sell')
                continue

            sellPrice = currentPrice
            assets = btcAssets * sellPrice
            assets = np.round(assets * (1 - txFee), 7)
            btcAssets = 0
            totalUSDTtxed += assets

            print('***')
            print(str(currentDate), 'SELL AT:', sellPrice, 'current assets:', assets, 'USDT')
            print('***')

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

            sellPrice = currentPrice
            assets = btcAssets * sellPrice
            assets = np.round(assets * (1 - txFee), 7)
            btcAssets = 0
            totalUSDTtxed += assets

            print('***')
            print(str(currentDate), 'SELL AT:', sellPrice, 'current assets:', assets, 'USDT')
            print('***')

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
        highThreshold = sellTriggerRatio * lastBuyPrice

        print('Target Price to Sell At:', highThreshold)

        if currentPrice > highThreshold:
            sellTrigger = (1-sellTriggerPercent) * currentPrice
            if sellTrigger < highThreshold:
                sellTrigger = highThreshold
            print('sell trigger is at:', sellTrigger)



        print('--- no tx ---')
        print('Total Txed:', totalUSDTtxed)
        print('USDT:', assets)
        print(coin, btcAssets)

        elapsed = time.time() - start_time
        print('Time Taken:', elapsed, 's')




if __name__ == '__main__':
    lubinance('ATOM')

