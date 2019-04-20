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


def fixedIntervalBar(startDate=None,
                     endDate=None,
                     intervalDays=1,
                     showStartDate=None,
                     highColor='orange'):
    dates = []

    maxNumOfDaysIn5Years = 365 * 365
    currentDate = startDate
    y = []
    counter = intervalDays
    # dates.append(currentDate)
    for i in range(maxNumOfDaysIn5Years):
        if currentDate > endDate: break
        if currentDate >= showStartDate:
            dates.append(currentDate)
            y.append(1)
            # if counter==intervalDays:
            #     y.append(1)
            # else:
            #     y.append(0)

        currentDate += timedelta(days=intervalDays)
        # currentDate += timedelta(days=1)
        # if counter==intervalDays:
        #     counter=0
        # else:
        #     counter+=1

    # length=len(dates)

    # project backwards if required

    backDates = []
    currentDate = startDate
    backY = []
    for i in range(maxNumOfDaysIn5Years):
        currentDate -= timedelta(days=intervalDays)
        if currentDate < showStartDate: break
        backDates.append(currentDate)
        backY.append(1)

    dates = backDates + dates
    y = backY + y

    thisBar = Bar(x=dates, y=y,
                  # width=[10]*length, #[barWidth] * length,
                  # xbins=dict(start=np.min(HH_bars), size=size, end=np.max(HH_bars)),
                  # hoverinfo='none',
                  # name='HH Projection ' + eachProj.strftime("%y-%m-%d"),
                  # dx=1,
                  dy=1,
                  # yaxis='y2',
                  # legendgroup='Proj of next highs',
                  showlegend=True,
                  opacity=1,
                  marker=dict(color=highColor),
                  hoverinfo='x',
                  # hoverlabel='',
                  # marker=dict(color='navy'),
                  )

    # print(showStartDate,endDate,intervalDays)
    # print(dates)
    # print(thisBar)
    # exit()

    return thisBar
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


def getActiveTrend(df):
    # inside bars (fully ignore for trend line calculation)
    # region: INSIDE BARS

    activeDate = []
    activeClose = []
    activeOpen = []
    activeHigh = []
    activeLow = []
    activeLowFirst = []
    activeBarIndex = []

    insideDate = []
    insideClose = []
    insideOpen = []
    insideHigh = []
    insideLow = []
    insideBarIndex = []

    for i, row in df.iterrows():

        if i == 0:
            activeDate.append(row.date)
            activeClose.append(row.close)
            activeOpen.append(row.open)
            activeHigh.append(row.high)
            activeLow.append(row.low)
            activeLowFirst.append(row.lowFirst)
            activeBarIndex.append(i)
            continue


        if (len(activeHigh)==0) and (len(activeLow)==0):
            continue

        if (activeHigh[-1] > row.high) & (activeLow[-1] < row.low):
            insideDate.append(row.date)
            insideClose.append(row.close)
            insideOpen.append(row.open)
            insideHigh.append(row.high)
            insideLow.append(row.low)
            insideBarIndex.append(i)
            continue

        activeDate.append(row.date)
        activeClose.append(row.close)
        activeOpen.append(row.open)
        activeHigh.append(row.high)
        activeLow.append(row.low)
        activeLowFirst.append(row.lowFirst)
        activeBarIndex.append(i)

    noInsideBars = {
        'date': activeDate,
        'close': activeClose,
        'open': activeOpen,
        'high': activeHigh,
        'low': activeLow,
        'lowFirst': activeLowFirst,
        'barIndex': activeBarIndex,
    }
    insideBarsOnly = {
        'date': insideDate,
        'close': insideClose,
        'open': insideOpen,
        'high': insideHigh,
        'low': insideLow,
        'barIndex': insideBarIndex,
    }
    dfIgnoreInsideBars = pd.DataFrame.from_dict(noInsideBars)
    # dfInsideBarsOnly = pd.DataFrame.from_dict(insideBarsOnly)

    trendLine1, trendLine2, trendLine3 = getTrendLine(dfIgnoreInsideBars)

    return trendLine1, trendLine2, trendLine3

def plotTrendlines(trendLine, name, color, width, dash=None):
    line = Scatter(name=name + 'Trend', x=trendLine.date, y=trendLine.point,
                   mode='lines+markers',
                   line=dict(color=color,
                             width=width,
                             dash=dash
                             ),
                   hoverinfo='none',
                   showlegend=True,
                   )



    return line


def checkPrevPoints(dfIgnoreInsideBars, index, row, DELAY):
    # takes out the chunk to be checked and reverses the order
    testDf = (dfIgnoreInsideBars[(index - DELAY):index]).iloc[::-1]

    # check for consecutive lower points
    runningLow = row.low
    trendLow = True
    for idx, entry in testDf.iterrows():
        if runningLow < entry.low:
            trendLow = True
            runningLow = entry.low
        else:
            trendLow = False
            break

    # check for consecutive higher points
    runningHigh = row.high
    trendHigh = True
    for idx, entry in testDf.iterrows():
        if runningHigh > entry.high:
            trendHigh = True
            runningHigh = entry.high
        else:
            trendHigh = False
            break

    # add points if necessary

    if trendLow:
        return [row.date, row.low, row.barIndex]
    elif trendHigh:
        return [row.date, row.high, row.barIndex]

        # otherwise do nothing

        return None


def processOutsideBars(row, trendPoints, DELAY, minorPoints):
    if len(minorPoints) >= 2:
        if minorPoints[-1][1] >= minorPoints[-2][1]:  # trending up
            if not row.lowFirst:  # high first
                if DELAY == 1:  # high then low
                    trendPoints.append([row.date, row.high, row.barIndex])
                    trendPoints.append([row.date, row.low, row.barIndex])
                else:  # 1 bar up
                    trendPoints.append([row.date, row.high, row.barIndex])
            else:  # low first
                if DELAY == 1:  # low then high
                    trendPoints.append([row.date, row.low, row.barIndex])
                    trendPoints.append([row.date, row.high, row.barIndex])
                else:  # 1 bar up
                    trendPoints.append([row.date, row.high, row.barIndex])

        elif minorPoints[-1][1] < minorPoints[-2][1]:  # trending down

            if not row.lowFirst:  # high first
                if DELAY == 1:  # high then low
                    trendPoints.append([row.date, row.high, row.barIndex])
                    trendPoints.append([row.date, row.low, row.barIndex])
                else:  # 1 bar up
                    trendPoints.append([row.date, row.high, row.barIndex])
            else:  # low first
                if DELAY == 1:  # low then high
                    trendPoints.append([row.date, row.low, row.barIndex])
                    trendPoints.append([row.date, row.high, row.barIndex])
                else:  # 1 bar down
                    trendPoints.append([row.date, row.low, row.barIndex])
    return trendPoints


def getTrendLine(dfIgnoreInsideBars):
    dfIgnoreInsideBars['outside'] = (dfIgnoreInsideBars.high > dfIgnoreInsideBars.shift(1).high) & (
            dfIgnoreInsideBars.low < dfIgnoreInsideBars.shift(1).low)

    minorPoints = []
    intermediatePoints = []
    majorPoints = []

    # dfIgnoreInsideBars = pd.DataFrame(df)

    for index, row in dfIgnoreInsideBars.iterrows():
        if index < 1: continue
        if row.outside:

            if index >= 2: intermediatePoints = processOutsideBars(row, intermediatePoints, DELAY=2,
                                                                   minorPoints=minorPoints)
            if index >= 3: majorPoints = processOutsideBars(row, majorPoints, DELAY=3, minorPoints=minorPoints)
            minorPoints = processOutsideBars(row, minorPoints, DELAY=1, minorPoints=minorPoints)
            continue

        # minor points
        result = checkPrevPoints(dfIgnoreInsideBars, index, row, DELAY=1)
        if result != None: minorPoints.append(result)

        # intermediate points
        if index >= 2:
            result = checkPrevPoints(dfIgnoreInsideBars, index, row, DELAY=2)
            if result != None: intermediatePoints.append(result)

        # major points
        if index >= 3:
            result = checkPrevPoints(dfIgnoreInsideBars, index, row, DELAY=3)
            if result != None: majorPoints.append(result)

    trendLine1 = pd.DataFrame(minorPoints, columns=['date', 'point', 'barIndex'])
    trendLine2 = pd.DataFrame(intermediatePoints, columns=['date', 'point', 'barIndex'])
    trendLine3 = pd.DataFrame(majorPoints, columns=['date', 'point', 'barIndex'])

    return trendLine1, trendLine2, trendLine3


def getTrendTopsAndBottoms(trendLine, df):
    tops = ((trendLine.point > trendLine.shift(1).point) & (trendLine.point > trendLine.shift(-1).point))
    bottoms = ((trendLine.point < trendLine.shift(1).point) & (trendLine.point < trendLine.shift(-1).point))

    trendLine['top'] = tops
    trendLine['bottom'] = bottoms

    reindexed = trendLine.reset_index(drop=True)

    dateIndexOnly = pd.DataFrame()
    dateIndexOnly['i'] = df.reset_index(drop=True).index
    dateIndexOnly['date'] = df.date
    reindexed = reindexed.merge(dateIndexOnly, on='date')

    topPoints = pd.DataFrame(reindexed[tops])
    # topPoints['i'] = topPoints.i
    bottomPoints = pd.DataFrame(reindexed[bottoms])
    # bottomPoints['i'] = bottomPoints.i
    topAndBottomPoints = pd.DataFrame(reindexed[tops | bottoms])
    # topAndBottomPoints['i'] = topAndBottomPoints.i

    # region: High to High
    HH_time = topPoints.date - topPoints.shift(1).date
    HH_price = topPoints.point - topPoints.shift(1).point
    HH_bars = topPoints.i - topPoints.shift(1).i

    HH_time = HH_time.dropna()
    HH_price = HH_price.dropna()

    HH_bars = HH_bars.dropna()

    # fig = ff.create_distplot([HH_bars], group_labels=['test1'],
    # endregion

    # region: Low to Low
    LL_time = bottomPoints.date - bottomPoints.shift(1).date
    LL_price = bottomPoints.point - bottomPoints.shift(1).point
    LL_bars = bottomPoints.i - bottomPoints.shift(1).i

    LL_time = LL_time.dropna()
    LL_price = LL_price.dropna()
    LL_bars = LL_bars.dropna()

    LL_barsMean = np.mean(LL_bars)
    # LL_barsMode = sp.stats.mode(LL_bars).mode[0]

    LL_barsTrace = Histogram(x=LL_bars, xbins=dict(start=np.min(LL_bars), size=1, end=np.max(LL_bars)))
    LL_barsFig = Figure(data=[LL_barsTrace])
    # endregion

    # region: High to Low and Low to High
    mixed_time = topAndBottomPoints.date - topAndBottomPoints.shift(1).date
    mixed_price = topAndBottomPoints.point - topAndBottomPoints.shift(1).point
    mixed_bars = topAndBottomPoints.i - topAndBottomPoints.shift(1).i

    mixed_time = mixed_time.dropna().reset_index(drop=True)
    mixed_price = mixed_price.dropna().reset_index(drop=True)
    mixed_bars = mixed_bars.dropna().reset_index(drop=True)

    topAndBottomPoints.reset_index(drop=True, inplace=True)

    if topAndBottomPoints.iloc[0].point < topAndBottomPoints.iloc[1].point:  # bottom first
        HL_time = mixed_time[mixed_time.index % 2 == 0]  # even
        LH_time = mixed_time[mixed_time.index % 2 == 1]  # odd

        HL_price = mixed_price[mixed_price.index % 2 == 0]
        LH_price = mixed_price[mixed_price.index % 2 == 1]

        HL_bars = mixed_bars[mixed_bars.index % 2 == 0]
        LH_bars = mixed_bars[mixed_bars.index % 2 == 1]

    else:
        HL_time = mixed_time[mixed_time.index % 2 == 1]
        LH_time = mixed_time[mixed_time.index % 2 == 0]

        HL_price = mixed_price[mixed_price.index % 2 == 1]
        LH_price = mixed_price[mixed_price.index % 2 == 0]

        HL_bars = mixed_bars[mixed_bars.index % 2 == 1]
        LH_bars = mixed_bars[mixed_bars.index % 2 == 0]

    # endregion

    topText = []
    bottomText = []
    topAndBottomPoints['xDiff'] = topAndBottomPoints.i - topAndBottomPoints.shift(1).i
    topAndBottomPoints['yDiff'] = topAndBottomPoints.point - topAndBottomPoints.shift(1).point

    topAndBottomPoints.fillna(value=0,inplace=True)



    for index, row in topAndBottomPoints.iterrows():
        if row.top:
            text = str(row.point) + '<br>'+ str(int(row.xDiff)) + '<br>' + '%.4f'%(row.yDiff)
            topText.append(text)
            # bottomText.append('')
        elif row.bottom:
            # topText.append('')
            text = str(row.point) + '<br>' + str(int(row.xDiff)) + '<br>' + '%.4f' % (row.yDiff)
            bottomText.append(text)
        # else:
        #     topText.append('')
        #     bottomText.append('')

    # print(trendLine)
    # print(len(trendLine[tops]))
    # print(len(topText.))
    # print(topText)
    # exit()


    return dict(tops=trendLine[tops],
                bottoms=trendLine[bottoms],
                topsAndBottoms=trendLine[tops | bottoms],
                topText=topText,
                bottomText=bottomText,
                HH_bars=HH_bars,
                LL_bars=LL_bars,
                HL_bars=HL_bars,
                LH_bars=LH_bars,
                )