from math import pi
from datetime import datetime
from datetime import timedelta

import pandas as pd
import numpy as np
import plotly
from plotly.graph_objs import Layout, Scatter, Line, Ohlc, Figure, Histogram, Bar, Table
import plotly.figure_factory as ff
import scipy as sp
import time
from sklearn.cluster import AgglomerativeClustering

# TODO:
# plotly
# table and chart subplot
# figure factory subplot
# gantt chart for intersecting projections (basic)
# mixed subplot
# tables, histograms

# TODO:
# Window 1999-2001
# Check for toppest top and bottomest bottom
# Take date - Get year, month, week, day for that top/bottom point.
# If top & bottom:
# Look at next year. If top taken out, choose bottomest bottom date. And vice versa.
# If cannot resolve, go to following year and see if top or bottom taken out.
#
# TODO:
# Price Retracements
# All on the right hand side.
# See email for retracement levels.
# For now, for each full trend (up or down).
# "mini" projections only for current, where don't know whether trend has ended or not.
# Differnet levels for up trend or down trend.
#
#
# TODO: UPDATE BY EACH DAY/BAR!
# DONE: Current trend (always up or down.)
# DONE: See if broke previous top or bottom.
# DONE: If sideways, (trend up/down will just keep flipping.)
# DONE: If doesn't break, keep the previous trend.
#
# TODO:
# Fig 12.2, 12.3 - show difference in price, time at max/min points.
# (Non-trend indicator. Raw data)

#
# TODO:
# Tops and Bottoms Projection
# Find latest trend (up or down), can be current trend also.
# collate H-H, H-L, L-L, L-H data. (for both uptrend and downtrend)
# Project for each H-H, H-L, L-L, L-H using previous set of numbers from whole data set.
# For each H-H, H-L, L-L, L-H, show historgram of dates vs 1x of each duration from previous trend. Do for both tops and bottoms.
# if current trend has no eg. H-L data yet, use previous trend's data.
# replace previous set of data, once there is 1 value from current trend.
# IMPT: For H-L and L-L, only project ONCE for each set of numbers.
# Combine H-L and L-L charts (to see which dates have hits).
# Combine L-H and H-H charts (to see which dates have hits).
# 2 things to look for: 1. highest frequecnies of intervals from the past. 2. projections - where the dates line up.
# to project Lows, use L-L, and H-L (different starting points)
# to project Highs, use H-H, and L-H (different starting points)
# See if can use gantt chart to show which projections come from where.

# TODO: Lost Motion
# TODO: Signal Tops/Bottoms

# TODO:
# - DONE: split 3 trendlines
# - DONE: outside bar include closer to open/close thing for highs and lows
# - DONE: HH, HL, LH, LL - histogram?

# TODO:
#     - write program to be efficient: only make changes to new data collected (don’t recompute everything.)

# - DONE: see swing high and low numbers. High green circle, low red circle.

# TITLE = 'TrendLine Delay = ' + str(DELAY)
TITLE = 'minor-grey, intermediate-blue, major-black'


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


def plotter(figure, filename, htmlList):
    plotly.offline.plot(figure_or_data=figure,
                        show_link=False,
                        output_type='file',
                        include_plotlyjs=False,
                        filename=filename,
                        auto_open=True,
                        config={'displaylogo': False,
                                'modeBarButtonsToRemove': [
                                    # 'zoom2d',
                                    #                        'sendDataToCloud',
                                    # 'select2d',
                                    # 'zoomIn2d',
                                    # 'zoomOut2d',
                                    #                        'resetScale2d', 'hoverCompareCartesian', 'lasso2d'
                                ]})
    line = '<script src="plotly-latest.min.js"></script>'
    with open(filename, 'r+') as htmlFile:
        contents = htmlFile.read()
        htmlFile.seek(0, 0)
        htmlFile.write(line.rstrip('\r\n') + '\n' + contents)

        for eachHtml in htmlList:
            htmlFile.write('\n' + eachHtml)

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