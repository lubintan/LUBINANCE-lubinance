from math import pi
from datetime import datetime
from datetime import timedelta

import pandas as pd
import numpy as np
import time, sys
import logging

TITLE = 'minor-grey, intermediate-blue, major-black'

def printer(inputDict, file):
    
    pd = {}
    pd['Date'] = ''
    pd['Current Price'] = ''
    pd['assets'] = ''
    pd['btcAssets'] = ''
    pd['Bolli Broken'] = ''
    pd['Wait Buy Break'] = ''
    pd['Buy Order Cancelled'] = ''
    pd['Buy Order'] = ''
    pd['Stop'] = ''
    pd['Limit'] = ''
    pd['Buy Executed'] = ''
    pd['Buy Price'] = ''
    pd['Target'] = ''
    pd['Margin'] = ''
    pd['Drop Threshold'] = ''
    pd['Sell Order Cancelled'] = ''
    pd['Sell Order'] = ''
    pd['Sell Stop'] = ''
    pd['Sell Limit'] = ''
    pd['Sell Executed'] = ''
    pd['Sell Price'] = ''
    pd['Mini Sell Order Cancelled'] = ''
    pd['Mini Sell Order'] = ''
    pd['Mini Sell Stop'] = ''
    pd['Mini Sell Limit'] = ''
    pd['Mini Sell Executed'] = ''
    pd['Mini Sell Price'] = ''
    pd['Open Phase Entered'] = ''
    pd['Open Phase Exited'] = ''
    pd['Close Phase Entered'] = ''
    pd['Close Phase Exited'] = ''
    
    headerList = ['Date',
                 'Current Price',
                 'assets',
                 'btcAssets',
                 'Bolli Broken',
                 'Wait Buy Break',
                 'Buy Order Cancelled',
                 'Buy Order',
                 'Stop',
                 'Limit',
                 'Buy Executed',
                 'Buy Price',
                 'Target',
                 'Margin',
                 'Drop Threshold',
                 'Sell Order Cancelled',
                 'Sell Order',
                 'Sell Stop',
                 'Sell Limit',
                 'Sell Executed',
                 'Sell Price',
                 'Mini Sell Order Cancelled',
                 'Mini Sell Order',
                 'Mini Sell Stop',
                 'Mini Sell Limit',
                 'Mini Sell Executed',
                 'Mini Sell Price',
                 'Open Phase Entered',
                 'Open Phase Exited',
                 'Close Phase Entered',
                 'Close Phase Exited']

    for eachKey in inputDict.keys():
        pd[eachKey] = str(inputDict[eachKey])

    printingList = ''

    for eachKey in headerList:
        printingList = printingList + pd[eachKey] + ','

    print(printingList, file=file)


def uptrendFinder(uptrendData,file):
    midpoints = []
    for i, r in uptrendData.iterrows():
        mid = ((r.high - r.low) / 2) + r.low
        midpoints.append(mid)

    # print('Finding Uptrend..',midpoints,file=file)

    for i in range(len(midpoints) - 1):
        if midpoints[i] >= midpoints[i + 1]:
            return False

    return True

def downtrendFinder(downtrendData,file):
    midpoints = []
    for i, r in downtrendData.iterrows():
        mid = ((r.high - r.low) / 2) + r.low
        midpoints.append(mid)

    # print('Finding Uptrend..',midpoints,file=file)

    for i in range(len(midpoints) - 1):
        if midpoints[i] <= midpoints[i + 1]:
            return False

    return True

def gainLossCounter(uptrendData):
    gainCounter = 0
    lossCounter = 0
    length = len(uptrendData)
    for i, r in uptrendData.iterrows():
        if r.open < r.close: gainCounter += 1
        elif r.close < r.open: lossCounter += 1

    total = float(gainCounter + lossCounter)
    if total == 0:
        gains = 1
        losses = gains
    else:
        losses = int(length * lossCounter/total)
        gains = length-losses

    return gains, losses


def writeToFile(filename,line='\n'):
    filename = 'logs//'+filename
    with open(filename, 'a+') as f:
        f.writelines(line)
        f.writelines('\n')

def getUSDTFromBasket(filename):
    filename = 'baskets//' + filename
    f = open(filename, "r")
    amount = f.readline()
    f.close()
    return float(amount)

def putUSDTToBasket(filename, amount):
    filename = 'baskets//' + filename
    f = open(filename, "w+")
    precision = 5
    amount = "{:0.0{}f}".format(amount, precision)
    f.writelines(amount)
    f.close()


def bollingerLow(prevData, numOfStd=2):
    mean = np.mean(prevData)
    stdDev = np.std(prevData)

    return mean - (numOfStd * stdDev)


# def plotter(figure, filename, htmlList):
#     plotly.offline.plot(figure_or_data=figure,
#                         show_link=False,
#                         output_type='file',
#                         include_plotlyjs=False,
#                         filename=filename,
#                         auto_open=True,
#                         config={'displaylogo': False,
#                                 'modeBarButtonsToRemove': [
#                                     # 'zoom2d',
#                                     #                        'sendDataToCloud',
#                                     # 'select2d',
#                                     # 'zoomIn2d',
#                                     # 'zoomOut2d',
#                                     #                        'resetScale2d', 'hoverCompareCartesian', 'lasso2d'
#                                 ]})
#     line = '<script src="plotly-latest.min.js"></script>'
#     with open(filename, 'r+') as htmlFile:
#         contents = htmlFile.read()
#         htmlFile.seek(0, 0)
#         htmlFile.write(line.rstrip('\r\n') + '\n' + contents)
#
#         for eachHtml in htmlList:
#             htmlFile.write('\n' + eachHtml)

def lubinanceForAnalysis(coin='BTC', sellingMargin=1.006, pollingInterval = 4):
    # from interactData import *
    # must paste the above line at the top of file
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

    failSafePercent = 0.8 #lose at most 20%


    while True:

        try:
            assets+=1.03
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