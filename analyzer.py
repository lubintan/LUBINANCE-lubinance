from analyzerFunctions import *
from testInfo import *


def main(dataFile,begin,end):

    print()

    print('Processing New Data Set:', dataFile)


    df = pd.read_csv(dataFile)

    # Convert Date Format
    df.columns = ['date', 'open', 'high', 'low', 'close','vol']


    df['date'] = pd.to_datetime(df['date'])

    BEGIN = begin
    END = end

    df = df[(df.date>=BEGIN) & (df.date<=END)].reset_index(drop=True)

    print("Total num of points:", len(df))
    print("from:", df.iloc[0].date, 'to:', df.iloc[-1].date)



    # df = df[pd.to_numeric(df['high'], errors='coerce').notnull()]
    df['close'] = pd.to_numeric(df['close'])
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['vol'] = pd.to_numeric(df['vol'])
    df = df.reset_index(drop=True)

    # only retain data for last 5 years
    # df = df[df.date > (df.iloc[-1].date-timedelta(days=(365.25*2)))]
    # df = df.reset_index(drop=True)

    # cutoff = len(df) - 0

    # dfTail = df[cutoff:]
    # df = df[:cutoff]

    # todaysDate = df.iloc[-1].date

    # endpoint = todaysDate + timedelta(weeks=0)
    #
    # showDate = todaysDate - timedelta(weeks=0)
    #
    # showXaxisRange = [showDate,
    #                   # df.iloc[-154].date,
    #                   endpoint]





    # region: add lowFirst column if no timing data
    if 'lowFirst' not in df.columns: df['lowFirst'] = df.open < df.close
    # endregion
    df = pd.DataFrame(df.iloc[0:]).reset_index(drop=True)

    trendLine1, trendLine2, trendLine3 = getActiveTrend(df)

    #### TRENDLINE PROCESSING  END #####

    # topAndBottomPoints, HH_bars, LL_bars, HL_bars, LH_bars
    # minorStuff = getTrendTopsAndBottoms(trendLine1, df)
    # intermediateStuff = getTrendTopsAndBottoms(trendLine2, df)
    # majorStuff = getTrendTopsAndBottoms(trendLine3, df)

    # region:all bars
    allBars = Ohlc(name='All Bars', x=df.date, open=df.open,
                   close=df.close, high=df.high, low=df.low,
                   opacity=0.8,
                   line=dict(width=2.5),
                   # hoverinfo='none',
                   hoverlabel=dict(bgcolor='pink'),

                   # showlegend=False,
                   # increasing=dict(line=dict(color= '#17BECF')),
                   # decreasing=dict(line=dict(color= '#17BECF')),
                   # increasing=dict(line=dict(color='black')),
                   # decreasing=dict(line=dict(color='black')),
                   )
    # endregion



    # region:trendlines
    # plot minor trendline points and lines
    minor= plotTrendlines(trendLine1, name='Minor', color='brown', width=3)

    # # plot intermediate trendline points and lines
    # intermediate, intermediateTops, intermediateBottoms = plotTrendlines(trendLine2, intermediateStuff,
    #                                                                      name='Intermediate', color='orange', width=3)
    #
    # major, majorTops, majorBottoms = plotTrendlines(trendLine3, majorStuff, name='Major', color='navy', width=4)

    # region: major data to plot
    majorData = [
        allBars,
        # tailBars,
        # major,
        # intermediate,
        minor,
        # majorTops, majorBottoms,
        # intermediateTops, intermediateBottoms,
        # minorTops, minorBottoms

    ]

    # majorFig = Figure(data=majorData,
    #                   layout=Layout(xaxis=dict(
    #         rangeslider=dict(
    #             visible=False
    #         ),)))
    # plotly.offline.plot(majorFig)




    # dataPoints = []
    startDate = datetime(year=2015,month=1,day=1,hour=0,minute=0)

    startingUSD = float(1e2)
    assets = startingUSD
    btcAssets = 0
    txFee = 0.002  # 0.22%

    totalUSDTtxed = 0

    for i,r in df.iterrows():
        # print()
        # print(i,'----------------------------')

        dataPoints = pd.DataFrame(df[(df.date >= startDate) & (df.index<=i)]).reset_index(drop=True)

        # if len(dataPoints) < 7:
        #     continue

        # print(dataPoints)

        min,inter,mag = getActiveTrend(dataPoints)

        if len(min) < 4:
            continue

        min = min[-4:].reset_index(drop=True)

        # print(min)


        #sell condition
        if (min.iloc[1].point < min.iloc[2].point) and (min.iloc[3].point<min.iloc[2].point):
            # print()
            if btcAssets == 0:
                # print(str(min.iloc[-1].date),': no BTC to sell')
                continue


            sellPrice = df[df.date==min.iloc[-1].date].close.values[0]
            assets = btcAssets * sellPrice
            btcAssets = 0
            assets = np.round(assets * (1 - txFee), 3)

            startDate = min.iloc[0].date

            totalUSDTtxed += assets

            # print(str(min.iloc[-1].date), 'sell at:', sellPrice, 'assets:', assets, 'USD')
            # print('startDate', startDate)



        elif (min.iloc[1].point > min.iloc[2].point) and (min.iloc[3].point > min.iloc[2].point):
            # print()
            if assets == 0:
                # print(min.iloc[-1].date, ': no USDT to buy BTC with')
                continue



            buyPrice = df[df.date==min.iloc[-1].date].close.values[0]

            btcAssets = assets / buyPrice
            assets = 0
            btcAssets = np.round(btcAssets * (1 - txFee), 3)

            startDate = min.iloc[0].date

            totalUSDTtxed += btcAssets * buyPrice

            # print(str(min.iloc[-1].date), 'buy at:', buyPrice, 'assets:', btcAssets, 'BTC')
            # print('startDate', startDate)

    print('end assetsUSD:', assets)
    print('end assetsBTC:', btcAssets, '=', btcAssets * df.iloc[-1].close, 'USD')

    days = (df.iloc[-1].date - df.iloc[0].date).days

    # (1.n)^days = 1.totalN
    # days * log(1.n) = log(1.totalN)
    # log(1.n) = log(1.totalN)/days
    # 1.n = 10^(log(1.totalN)/days)

    totalPercentage = (assets + btcAssets * df.iloc[-1].close) / startingUSD
    dailyRate = 10 ** (np.log10(totalPercentage) / days)

    print('total %:', totalPercentage, 'daily %:', dailyRate, 'days:', days)

    print('projected monthly rate:', 100 * ((dailyRate ** 30) - 1), '%')
    print('projected annual rate:', 100 * ((dailyRate ** 365) - 1), '%')








    #

    startingUSD = float(1e2)
    assets = startingUSD
    btcAssets = 0
    txFee = 0.002  # 0.22%

    minorStuff = getTrendTopsAndBottoms(trendLine1, df)


    trend = trendLine1[:]  # minor,int, major

    print('start assetsUSDT: ', assets)
    print('start assetsBTC: ', btcAssets)

    for i, r in trend.iterrows():
        # print(i,'---------------')
        if i == len(trend) - 2: break
        if trend.iloc[i + 1].date == r.date:
            iii = 2
        else:
            iii = 1

        if r.bottom:
            if assets == 0: continue

            buyPrice = df.iloc[trend.iloc[i + iii].barIndex].close
            btcAssets = assets / buyPrice
            assets = 0
            btcAssets = np.round(btcAssets * (1 - txFee), 3)
            # print(str(trend.iloc[i + iii].date)[:10], 'buy at:', buyPrice, 'assets:', btcAssets, 'BTC')

        elif r.top:
            if btcAssets == 0: continue


            sellPrice = df.iloc[trend.iloc[i + iii].barIndex].close
            assets = btcAssets * sellPrice
            btcAssets = 0
            assets = np.round(assets * (1 - txFee), 3)
            # print(str(trend.iloc[i + iii].date)[:10], 'sell at:', sellPrice, 'assets:', assets, 'USD')

    print('end assetsUSD:', assets)
    print('end assetsBTC:', btcAssets, '=', btcAssets * df.iloc[-1].close, 'USD')

    days = (df.iloc[-1].date - df.iloc[0].date).days

    # (1.n)^days = 1.totalN
    # days * log(1.n) = log(1.totalN)
    # log(1.n) = log(1.totalN)/days
    # 1.n = 10^(log(1.totalN)/days)

    totalPercentage = (assets + btcAssets * df.iloc[-1].close) / startingUSD
    dailyRate = 10 ** (np.log10(totalPercentage) / days)

    print('total %:', totalPercentage, 'daily %:', dailyRate, 'days:', days)

    print('projected monthly rate:', 100 * ((dailyRate ** 30) - 1), '%')
    print('projected annual rate:', 100 * ((dailyRate ** 365) - 1), '%')





    return


def timeCounterWrapper(dataFile, begin, end):
    startTime = time.time()

    main(dataFile, begin, end)

    endTime = time.time()
    elapsed = endTime - startTime
    print("Operation took a total of %.2f seconds." % (elapsed))
    print()


if __name__ == '__main__':

    timeCounterWrapper(BTCUSDT['datasets'][1], datetime(2019,1,1),datetime(2019,1,5))



