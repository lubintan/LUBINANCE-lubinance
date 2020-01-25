from analyzerFunctions import *
from testInfo import *
import csv,sys



def mainPriceGateZZGate(dataFile,begin,end,fileName='test'):
    
    with open(
            "{}.csv".format(
                fileName             
            ),
            mode='w+'  # set file write mode
    ) as f:
        writer = csv.writer(f)
        writer.writerow([dataFile])

    
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
        writer.writerow(["Total num of points:", len(df)])
        writer.writerow(["from:", df.iloc[0].date, 'to:', df.iloc[-1].date])



        # df = df[pd.to_numeric(df['high'], errors='coerce').notnull()]
        df['close'] = pd.to_numeric(df['close'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['vol'] = pd.to_numeric(df['vol'])
        df = df.reset_index(drop=True)

           #
        # region: add lowFirst column if no timing data
        if 'lowFirst' not in df.columns: df['lowFirst'] = df.open < df.close
        df = pd.DataFrame(df.iloc[:]).reset_index(drop=True)
        # endregion
        trendLine1 = getActiveTrend(df)

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



        # region:trendlines plotting
        # plot minor trendline points and lines
        minor= plotTrendlines(trendLine1, name='Minor', color='brown', width=3)

        majorData = [
            allBars,
            minor,
            ]

        majorFig = Figure(data=majorData,
                          layout=Layout(title=dataFile,xaxis=dict(
                rangeslider=dict(
                    visible=False
                ),)))
        plotly.offline.plot(majorFig,filename=fileName,auto_open=False)
        #endregion



        #region: analysis

        # dataPoints = []
        startDate = datetime(year=2015,month=1,day=1,hour=0,minute=0)

        startingUSD = float(1e2)
        assets = startingUSD
        btcAssets = 0
        txFee = 0.002  # 0.22%

        totalUSDTtxed = 0

        lastSellDate = None
        lastBuyDate = None
        lastBuyPrice = None
        lastSellPrice = None
        bufferPercent = 0.003
        lengthDf = len(df)
        window = 10


        writer.writerow(['date',
                         'start date',
                         'not enough points',
                         'ignoring lastBuyDate',
                         'ignoring lastSellDate',
                         'last buy price',
                         'last sell price',
                         'sell price lower than last buy price',
                         'current BTC',
                         'sell Price',
                         'new USDT',
                         'buy price higher than last sell price',
                         'current USDT',
                         'buy Price',
                         'new BTC',
                         ])


        for i,r in df.iterrows():

            if i < window: continue

            dataPoints = pd.DataFrame(df[(df.index>(i-window)) & (df.index<=i)]).reset_index(drop=True)
            currentDate = dataPoints.iloc[-1].date

            print('-------------------------')
            print('date',currentDate, 'start date:', startDate)

            min = getActiveTrend(dataPoints)


            counter = 1
            while len(min) < 4:
                print("not enough points",'counter:',counter)
                writer.writerow([currentDate,counter, 'TRUE','','',lastBuyPrice,lastSellPrice])
                dataPoints = pd.DataFrame(df[(df.index > (i - (counter*window))) & (df.index <= i)]).reset_index(drop=True)
                min = getActiveTrend(dataPoints)


                counter+=1

                continue

            if min.iloc[-1].date!=dataPoints.iloc[-1].date: #"inside bar, skip"
                continue

            min = min.reset_index(drop=True)
            print(min)


            if (min.iloc[-2].date == lastBuyDate):
                print('ignoring:',lastBuyDate)
                writer.writerow([currentDate,startDate,'',lastBuyDate,'',lastBuyPrice,lastSellPrice])
                continue

            if (min.iloc[-2].date == lastSellDate):
                print('ignoring:', lastSellDate)
                writer.writerow([currentDate,startDate,'','',lastSellDate,lastBuyPrice,lastSellPrice])
                continue

            #sell condition
            if (min.iloc[-3].point < min.iloc[-2].point) and (min.iloc[-1].point<min.iloc[-2].point):
                # startDate = min.iloc[0].date
                # print()
                if btcAssets == 0:
                    print(str(min.iloc[-1].date),': no BTC to sell')
                    writer.writerow([currentDate,startDate,'','','',lastBuyPrice,lastSellPrice,'','000'])
                    continue


                sellPrice = df[df.date==min.iloc[-1].date].close.values[0]

                if (lastBuyPrice!=None) and (sellPrice <= ((1+bufferPercent)*lastBuyPrice)):
                    print("sell price lower than last buy price")
                    writer.writerow([currentDate,startDate,'','','',lastBuyPrice,lastSellPrice,sellPrice])
                    continue

                assets = btcAssets * sellPrice

                assets = np.round(assets * (1 - txFee), 3)

                writer.writerow([currentDate,startDate, '', '', '', lastBuyPrice, lastSellPrice, '', btcAssets,sellPrice,assets])
                btcAssets = 0



                totalUSDTtxed += assets

                lastSellDate = min.iloc[-1].date
                lastSellPrice = sellPrice

                print(str(min.iloc[-1].date), 'sell at:', sellPrice, 'assets:', assets, 'USD')

                # print('startDate', startDate)



            elif (min.iloc[-3].point > min.iloc[-2].point) and (min.iloc[-1].point > min.iloc[-2].point):
                # startDate = min.iloc[0].date
                # print()
                if assets == 0:
                    print(min.iloc[-1].date, ': no USDT to buy BTC with')
                    writer.writerow([currentDate, startDate,'', '', '', lastBuyPrice, lastSellPrice,'','','','','','000'])
                    continue



                buyPrice = df[df.date==min.iloc[-1].date].close.values[0]

                if (lastSellPrice!=None) and (buyPrice >= ((1-bufferPercent)*lastSellPrice)):
                    print("buy price greater than last sell price")
                    writer.writerow([currentDate,startDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '','', buyPrice,])
                    continue

                btcAssets = assets / buyPrice
                btcAssets = np.round(btcAssets * (1 - txFee), 3)

                writer.writerow([currentDate,startDate, '', '', '', lastBuyPrice, lastSellPrice, '', '','','','', assets,buyPrice,btcAssets])


                assets = 0


                totalUSDTtxed += btcAssets * buyPrice

                lastBuyDate = min.iloc[-1].date
                lastBuyPrice = buyPrice

                print(str(min.iloc[-1].date), 'buy at:', buyPrice, 'assets:', btcAssets, 'BTC')
                # print('startDate', startDate)
            else:
                writer.writerow([currentDate, startDate,])

        print('end assetsUSD:', assets)
        print('end assetsBTC:', btcAssets, '=', btcAssets * df.iloc[-1].close, 'USDT')
        print('volume:', totalUSDTtxed, 'USDT')

        writer.writerow([''])
        writer.writerow(['END'])
        writer.writerow(['Total Holdings','Vol USDT TXed','proj mthly vol (times of starting capital)','days','daily%','proj mthly %', 'proj yrly %'])


        totalHoldings = assets + (btcAssets * df.iloc[-1].close)

        days = (df.iloc[-1].date - df.iloc[0].date).days

        print('projected monthly volume:', 30.0* totalUSDTtxed/days/startingUSD, 'times of starting capital')


        # (1.n)^days = 1.totalN
        # days * log(1.n) = log(1.totalN)
        # log(1.n) = log(1.totalN)/days
        # 1.n = 10^(log(1.totalN)/days)

        totalPercentage = (totalHoldings) / startingUSD
        dailyRate = 10 ** (np.log10(totalPercentage) / days)

        print('total %:', totalPercentage, 'daily %:', dailyRate, 'days:', days)

        monthlyRate = 100 * ((dailyRate ** 30) - 1)
        annualRate = 100 * ((dailyRate ** 365) - 1)

        print('projected monthly rate:',monthlyRate , '%')
        print('projected annual rate:', annualRate , '%')

        writer.writerow([totalHoldings,totalUSDTtxed,30.0* totalUSDTtxed/days/startingUSD,days,dailyRate,monthlyRate,annualRate])


    return annualRate, monthlyRate, days, totalHoldings


def mainZZGateOnly(dataFile, begin, end, fileName='test'):
    with open(
            "{}.csv".format(
                fileName
            ),
            mode='w+'  # set file write mode
    ) as f:
        writer = csv.writer(f)
        writer.writerow([dataFile])

        print('Processing New Data Set:', dataFile)

        df = pd.read_csv(dataFile)

        # Convert Date Format
        df.columns = ['date', 'open', 'high', 'low', 'close', 'vol']

        df['date'] = pd.to_datetime(df['date'])

        BEGIN = begin
        END = end

        df = df[(df.date >= BEGIN) & (df.date <= END)].reset_index(drop=True)

        print("Total num of points:", len(df))
        print("from:", df.iloc[0].date, 'to:', df.iloc[-1].date)
        writer.writerow(["Total num of points:", len(df)])
        writer.writerow(["from:", df.iloc[0].date, 'to:', df.iloc[-1].date])

        # df = df[pd.to_numeric(df['high'], errors='coerce').notnull()]
        df['close'] = pd.to_numeric(df['close'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['vol'] = pd.to_numeric(df['vol'])
        df = df.reset_index(drop=True)

        #
        # region: add lowFirst column if no timing data
        if 'lowFirst' not in df.columns: df['lowFirst'] = df.open < df.close
        df = pd.DataFrame(df.iloc[:]).reset_index(drop=True)
        # endregion
        trendLine1, trendLine2, trendLine3 = getActiveTrend(df)

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

        # region:trendlines plotting
        # plot minor trendline points and lines
        minor = plotTrendlines(trendLine1, name='Minor', color='brown', width=3)

        # # plot intermediate trendline points and lines
        # intermediate, intermediateTops, intermediateBottoms = plotTrendlines(trendLine2, intermediateStuff,
        #                                                                      name='Intermediate', color='orange', width=3)
        #
        # major, majorTops, majorBottoms = plotTrendlines(trendLine3, majorStuff, name='Major', color='navy', width=4)

        # # region: major data to plot
        majorData = [
            allBars,
            minor,
        ]

        majorFig = Figure(data=majorData,
                          layout=Layout(title=dataFile, xaxis=dict(
                              rangeslider=dict(
                                  visible=False
                              ), )))
        plotly.offline.plot(majorFig, filename=fileName, auto_open=False)
        # endregion

        # region: analysis

        # dataPoints = []
        startDate = datetime(year=2015, month=1, day=1, hour=0, minute=0)

        startingUSD = float(1e2)
        assets = startingUSD
        btcAssets = 0
        txFee = 0.002  # 0.22%

        totalUSDTtxed = 0

        lastSellDate = None
        lastBuyDate = None
        lastBuyPrice = ''
        lastSellPrice = ''
        bufferPercent = 0.003
        lengthDf = len(df)

        writer.writerow(['date',
                         'not enough points',
                         'ignoring lastBuyDate',
                         'ignoring lastSellDate',
                         'last buy price',
                         'last sell price',
                         'sell price lower than last buy price'
                         'current BTC',
                         'sell Price',
                         'new USDT',
                         'buy price higher than last sell price',
                         'current USDT',
                         'buy Price',
                         'new BTC',
                         ])

        for i, r in df.iterrows():


            dataPoints = pd.DataFrame(df[(df.date >= startDate) & (df.index <= i)]).reset_index(drop=True)
            currentDate = dataPoints.iloc[-1].date

            print('date', currentDate, ', lastBuyPrice', lastBuyPrice, ', lastSellPrice', lastSellPrice)

            min, inter, mag = getActiveTrend(dataPoints)

            if len(min) < 4:
                print("not enough points")
                writer.writerow([currentDate, 'TRUE', '', '', lastBuyPrice, lastSellPrice])
                continue

            min = min[-4:].reset_index(drop=True)

            if (min.iloc[-2].date == lastBuyDate):
                print('ignoring:', lastBuyDate)
                writer.writerow([currentDate, '', lastBuyDate, '', lastBuyPrice, lastSellPrice])
                continue

            if (min.iloc[-2].date == lastSellDate):
                print('ignoring:', lastSellDate)
                writer.writerow([currentDate, '', '', lastSellDate, lastBuyPrice, lastSellPrice])
                continue

            # sell condition
            if (min.iloc[1].point < min.iloc[2].point) and (min.iloc[3].point < min.iloc[2].point):
                startDate = min.iloc[0].date
                # print()
                if btcAssets == 0:
                    print(str(min.iloc[-1].date), ': no BTC to sell')
                    writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '000'])
                    continue

                sellPrice = df[df.date == min.iloc[-1].date].close.values[0]

                # if (lastBuyPrice != None) and (sellPrice <= ((1 + bufferPercent) * lastBuyPrice)):
                #     print("sell price lower than last buy price")
                #     writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, sellPrice])
                #     continue

                assets = btcAssets * sellPrice

                assets = np.round(assets * (1 - txFee), 3)

                writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', btcAssets, sellPrice, assets])
                btcAssets = 0

                totalUSDTtxed += assets

                lastSellDate = min.iloc[-1].date
                # lastSellPrice = sellPrice

                print(str(min.iloc[-1].date), 'sell at:', sellPrice, 'assets:', assets, 'USD')

                # print('startDate', startDate)




            elif (min.iloc[1].point > min.iloc[2].point) and (min.iloc[3].point > min.iloc[2].point):
                startDate = min.iloc[0].date
                # print()
                if assets == 0:
                    print(min.iloc[-1].date, ': no USDT to buy BTC with')
                    writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '', '', '', '000'])
                    continue

                buyPrice = df[df.date == min.iloc[-1].date].close.values[0]

                # if (lastSellPrice != None) and (buyPrice >= ((1 - bufferPercent) * lastSellPrice)):
                #     print("buy price greater than last sell price")
                #     writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '', '', buyPrice, ])
                #     continue

                btcAssets = assets / buyPrice
                btcAssets = np.round(btcAssets * (1 - txFee), 3)

                writer.writerow(
                    [currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '', '', '', assets, buyPrice, btcAssets])

                assets = 0

                totalUSDTtxed += btcAssets * buyPrice

                lastBuyDate = min.iloc[-1].date
                # lastBuyPrice = buyPrice

                print(str(min.iloc[-1].date), 'buy at:', buyPrice, 'assets:', btcAssets, 'BTC')
                # print('startDate', startDate)

        print('end assetsUSD:', assets)
        print('end assetsBTC:', btcAssets, '=', btcAssets * df.iloc[-1].close, 'USDT')
        print('volume:', totalUSDTtxed, 'USDT')

        writer.writerow([''])
        writer.writerow(['END'])
        writer.writerow(['Total Holdings', 'Vol USDT TXed', 'proj mthly vol (times of starting capital)', 'days', 'daily%',
                         'proj mthly %', 'proj yrly %'])

        totalHoldings = assets + (btcAssets * df.iloc[-1].close)

        days = (df.iloc[-1].date - df.iloc[0].date).days

        print('projected monthly volume:', 30.0 * totalUSDTtxed / days / startingUSD, 'times of starting capital')

        # (1.n)^days = 1.totalN
        # days * log(1.n) = log(1.totalN)
        # log(1.n) = log(1.totalN)/days
        # 1.n = 10^(log(1.totalN)/days)

        totalPercentage = (totalHoldings) / startingUSD
        dailyRate = 10 ** (np.log10(totalPercentage) / days)

        print('total %:', totalPercentage, 'daily %:', dailyRate, 'days:', days)

        monthlyRate = 100 * ((dailyRate ** 30) - 1)
        annualRate = 100 * ((dailyRate ** 365) - 1)

        print('projected monthly rate:', monthlyRate, '%')
        print('projected annual rate:', annualRate, '%')

        writer.writerow(
            [totalHoldings, totalUSDTtxed, 30.0 * totalUSDTtxed / days / startingUSD, days, dailyRate, monthlyRate,
             annualRate])

    return annualRate, monthlyRate, days, totalHoldings



def mainNoGates(dataFile, begin, end, fileName='test'):
    with open(
            "{}.csv".format(
                fileName
            ),
            mode='w+'  # set file write mode
    ) as f:
        writer = csv.writer(f)
        writer.writerow([dataFile])

        print('Processing New Data Set:', dataFile)

        df = pd.read_csv(dataFile)

        # Convert Date Format
        df.columns = ['date', 'open', 'high', 'low', 'close', 'vol']

        df['date'] = pd.to_datetime(df['date'])

        BEGIN = begin
        END = end

        df = df[(df.date >= BEGIN) & (df.date <= END)].reset_index(drop=True)

        print("Total num of points:", len(df))
        print("from:", df.iloc[0].date, 'to:', df.iloc[-1].date)
        writer.writerow(["Total num of points:", len(df)])
        writer.writerow(["from:", df.iloc[0].date, 'to:', df.iloc[-1].date])

        # df = df[pd.to_numeric(df['high'], errors='coerce').notnull()]
        df['close'] = pd.to_numeric(df['close'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['vol'] = pd.to_numeric(df['vol'])
        df = df.reset_index(drop=True)

        #
        # region: add lowFirst column if no timing data
        if 'lowFirst' not in df.columns: df['lowFirst'] = df.open < df.close
        df = pd.DataFrame(df.iloc[:]).reset_index(drop=True)
        # endregion


        trendLine1= getActiveTrend(df)


        #
        #region:all bars
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
        # # endregion
        #
        #region:trendlines plotting
        # # plot minor trendline points and lines
        # minor = plotTrendlines(trendLine1, name='Minor', color='brown', width=3)

        #region: Bollinger Low Band
        windowSize = 5
        bolliwoodBand = []
        medianBand = []
        for i,r in df.iterrows():
            if i < 5:
                bolliwoodBand.append(0.0)
                medianBand.append(0.0)
                continue

            windowedData = df.iloc[i-4:i+1].close
            print(windowedData)

            exit()

            lowPoint = bollingerLow(windowedData)
            bolliwoodBand.append(lowPoint)
            # medianBand.append(meanPoint)


        bollingerBand = Scatter(name='bollinger',x=df.iloc[5:].date,y=pd.Series(bolliwoodBand[5:]),mode='lines',
                   line=dict(color='navy',
                             width=4,
                             ),)
        # medianBand = Scatter(name='median', x=df.iloc[5:].date, y=pd.Series(medianBand[5:]), mode='lines',
        #                         line=dict(color='orange',
        #                                   width=4,
        #                                   ), )
        #endregion

        # # region: major data to plot
        majorData = [
            allBars,
            # minor,
            bollingerBand,
            # medianBand
        ]

        majorFig = Figure(data=majorData,
                          layout=Layout(title=dataFile, xaxis=dict(
                              rangeslider=dict(
                                  visible=False
                              ), )))
        plotly.offline.plot(majorFig, auto_open=True)
        #endregion

        exit()

        # region: analysis

        # dataPoints = []
        startDate = datetime(year=2015, month=1, day=1, hour=0, minute=0)

        startingUSD = float(1e2)
        assets = startingUSD
        btcAssets = 0
        txFee = 0.002  # 0.22%

        totalUSDTtxed = 0

        lastSellDate = ''
        lastBuyDate = ''
        lastBuyPrice = None
        lastSellPrice = None
        bufferPercent = 0.003
        lengthDf = len(df)
        window = 30

        writer.writerow(['date',
                         'not enough points',
                         'ignoring lastBuyDate',
                         'ignoring lastSellDate',
                         'last buy price',
                         'last sell price',
                         'sell price lower than last buy price'
                         'current BTC',
                         'sell Price',
                         'new USDT',
                         'buy price higher than last sell price',
                         'current USDT',
                         'buy Price',
                         'new BTC',
                         ])


        for i, r in df.iterrows():

            if i < window: continue

            dataPoints = pd.DataFrame(df[(df.index > (i - window)) & (df.index <= i)]).reset_index(drop=True)
            currentDate = dataPoints.iloc[-1].date

            print('-------------------------')
            print('date', currentDate, )

            min = getActiveTrend(dataPoints)

            writer.writerow([currentDate, 'TRUE', '', '', lastBuyPrice, lastSellPrice])

            counter = 1
            while len(min) < 4:
                print("not enough points", 'counter:', counter)

                dataPoints = pd.DataFrame(df[(df.index > (i - (counter * window))) & (df.index <= i)]).reset_index(
                    drop=True)
                min = getActiveTrend(dataPoints)
                counter += 1

                if counter >= 10: exit('infinity stones loop')

                continue

            # if (lastBuyPrice != None):
            #     if dataPoints.iloc[-1].low < (lastBuyPrice * 0.96):
            #         sellPrice = dataPoints.iloc[-1].low
            #         assets = btcAssets * sellPrice
            #
            #         assets = np.round(assets * (1 - txFee), 3)
            #         writer.writerow(
            #             [currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', btcAssets, sellPrice, assets])
            #         btcAssets = 0
            #
            #         totalUSDTtxed += assets
            #
            #         # lastSellDate = min.iloc[-1].date
            #         lastSellPrice = sellPrice
            #         lastBuyPrice = None
            #
            #         print(' STOP LOSS SELL-----------------',str(min.iloc[-1].date), 'sell at:', sellPrice, 'assets:', assets, 'USD')
            #
            #         continue


            if min.iloc[-1].date != dataPoints.iloc[-1].date:  # "inside bar, skip"
                continue

            min = min.reset_index(drop=True)
            # print(min)
            # if (min.iloc[-2].date == lastBuyDate):
            #     print('ignoring:', lastBuyDate)
            #     writer.writerow([currentDate, '', lastBuyDate, '', lastBuyPrice, lastSellPrice])
            #     continue
            #
            # if (min.iloc[-2].date == lastSellDate):
            #     print('ignoring:', lastSellDate)
            #     writer.writerow([currentDate, '', '', lastSellDate, lastBuyPrice, lastSellPrice])
            #     continue

            # sell condition
            if (min.iloc[-3].point < min.iloc[-2].point) and (min.iloc[-1].point < min.iloc[-2].point):
                # startDate = min.iloc[0].date
                # print()
                if btcAssets == 0:
                    print(str(min.iloc[-1].date), ': no BTC to sell')
                    writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '000'])
                    continue

                sellPrice = df[df.date == min.iloc[-1].date].close.values[0]

                # if (lastBuyPrice != None) and (sellPrice <= ((1 + bufferPercent) * lastBuyPrice)):
                #     print("sell price lower than last buy price")
                #     writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, sellPrice])
                #     continue

                assets = btcAssets * sellPrice

                assets = np.round(assets * (1 - txFee), 3)

                writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', btcAssets, sellPrice, assets])
                btcAssets = 0

                totalUSDTtxed += assets

                # lastSellDate = min.iloc[-1].date
                lastSellPrice = sellPrice
                lastBuyPrice = None

                print(str(min.iloc[-1].date), 'sell at:', sellPrice, 'assets:', assets, 'USD')

                # print('startDate', startDate)




            elif (min.iloc[-3].point > min.iloc[-2].point) and (min.iloc[-1].point > min.iloc[-2].point):
                # startDate = min.iloc[0].date
                # print()
                if assets == 0:
                    print(min.iloc[-1].date, ': no USDT to buy BTC with')
                    writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '', '', '', '000'])
                    continue

                buyPrice = df[df.date == min.iloc[-1].date].close.values[0]

                # if (lastSellPrice != None) and (buyPrice >= ((1 - bufferPercent) * lastSellPrice)):
                #     print("buy price greater than last sell price")
                #     writer.writerow([currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '', '', buyPrice, ])
                #     continue

                btcAssets = assets / buyPrice
                btcAssets = np.round(btcAssets * (1 - txFee), 3)

                writer.writerow(
                    [currentDate, '', '', '', lastBuyPrice, lastSellPrice, '', '', '', '', '', assets, buyPrice, btcAssets])

                assets = 0

                totalUSDTtxed += btcAssets * buyPrice

                # lastBuyDate = min.iloc[-1].date
                lastBuyPrice = buyPrice
                lastSellPrice=None

                print(str(min.iloc[-1].date), 'buy at:', buyPrice, 'assets:', btcAssets, 'BTC')
                # print('startDate', startDate)

        print('end assetsUSD:', assets)
        print('end assetsBTC:', btcAssets, '=', btcAssets * df.iloc[-1].close, 'USDT')
        print('volume:', totalUSDTtxed, 'USDT')

        writer.writerow([''])
        writer.writerow(['END'])
        writer.writerow(['Total Holdings', 'Vol USDT TXed', 'proj mthly vol (times of starting capital)', 'days', 'daily%',
                         'proj mthly %', 'proj yrly %'])

        totalHoldings = assets + (btcAssets * df.iloc[-1].close)

        days = (df.iloc[-1].date - df.iloc[0].date).days

        print('projected monthly volume:', 30.0 * totalUSDTtxed / days / startingUSD, 'times of starting capital')

        # (1.n)^days = 1.totalN
        # days * log(1.n) = log(1.totalN)
        # log(1.n) = log(1.totalN)/days
        # 1.n = 10^(log(1.totalN)/days)

        totalPercentage = (totalHoldings) / startingUSD
        dailyRate = 10 ** (np.log10(totalPercentage) / days)

        print('total %:', totalPercentage, 'daily %:', dailyRate, 'days:', days)

        monthlyRate = 100 * ((dailyRate ** 30) - 1)
        annualRate = 100 * ((dailyRate ** 365) - 1)

        print('projected monthly rate:', monthlyRate, '%')
        print('projected annual rate:', annualRate, '%')

        writer.writerow(
            [totalHoldings, totalUSDTtxed, 30.0 * totalUSDTtxed / days / startingUSD, days, dailyRate, monthlyRate,
             annualRate])

    return annualRate, monthlyRate, days, totalHoldings




def timeCounterWrapper(dataFile, begin, end):
    startTime = time.time()

    annualRate, monthlyRate, numOfDays,finalBalance = mainNoGates(dataFile, begin, end)

    endTime = time.time()
    elapsed = endTime - startTime
    print("Operation took a total of %.2f seconds." % (elapsed))
    print()

    return annualRate, monthlyRate, numOfDays, finalBalance

    time.sleep(2)


if __name__ == '__main__':

    OVERALL_START = time.time()

    #region: SIMULATION
    # numTrends = 4.0
    #
    # with open(
    #         "{}_{}.csv".format(
    #             'lubinanaceSimData100USDT',
    #             time.time()
    #         ),
    #         mode='w+'  # set file write mode
    # ) as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['Crypto Pair', 'Interval', 'Trend','Annual Rate', 'Monthly Rate', 'Final Balance','Sample Days', 'Sample Start', 'Sample End'])
    #
    #     for eachData in allData:
    #
    #         dataFile = eachData['datasets'][0]
    #         eachData['1mResults']={}
    #         totalAnnualRate = 0
    #         totalMonthlyRate = 0
    #         totalNumDays = 0
    #         totalBalance = 0
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['uptrendDates'][0],
    #                                                                               eachData['uptrendDates'][1])
    #         writer.writerow([eachData['name'], '1m', 'up', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['uptrendDates'][0], eachData['uptrendDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['1mResults']['uptrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
    #         #                                               finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['downtrendDates'][0],
    #                                                                               eachData['downtrendDates'][1])
    #         writer.writerow([eachData['name'], '1m', 'down', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['downtrendDates'][0], eachData['downtrendDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['1mResults']['downtrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
    #         #                                                 finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['sidewaysDates'][0],
    #                                                                               eachData['sidewaysDates'][1])
    #         writer.writerow([eachData['name'], '1m', 'sideways', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['sidewaysDates'][0], eachData['sidewaysDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['1mResults']['sidewaysResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
    #         #                                                finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['randomDates'][0],
    #                                                                               eachData['randomDates'][1])
    #         writer.writerow([eachData['name'], '1m', 'random', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['randomDates'][0], eachData['randomDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['1mResults']['randomResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
    #         #                                              finalBalance=finalBalance)
    #
    #
    #
    #         writer.writerow([eachData['name'], '1m', 'Average', totalAnnualRate/numTrends, totalMonthlyRate/numTrends, totalBalance/numTrends, totalNumDays/numTrends,
    #                          0, 0])
    #
    # ##########################################################
    #         dataFile = eachData['datasets'][1]
    #         eachData['5mResults'] = {}
    #         totalAnnualRate = 0
    #         totalMonthlyRate = 0
    #         totalNumDays = 0
    #         totalBalance = 0
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['uptrendDates'][0],
    #                                                                               eachData['uptrendDates'][1])
    #         writer.writerow([eachData['name'], '5m', 'up', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['uptrendDates'][0], eachData['uptrendDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['5mResults']['uptrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                               numOfDays=numOfDays,
    #         #                                               finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['downtrendDates'][0],
    #                                                                               eachData['downtrendDates'][1])
    #         writer.writerow([eachData['name'], '5m', 'down', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['downtrendDates'][0], eachData['downtrendDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['5mResults']['downtrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                                 numOfDays=numOfDays,
    #         #                                                 finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['sidewaysDates'][0],
    #                                                                               eachData['sidewaysDates'][1])
    #         writer.writerow([eachData['name'], '5m', 'sideways', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['sidewaysDates'][0], eachData['sidewaysDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['5mResults']['sidewaysResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                                numOfDays=numOfDays,
    #         #                                                finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['randomDates'][0],
    #                                                                               eachData['randomDates'][1])
    #         writer.writerow([eachData['name'], '5m', 'random', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['randomDates'][0], eachData['randomDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['5mResults']['randomResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                              numOfDays=numOfDays,
    #         #                                              finalBalance=finalBalance)
    #
    #         writer.writerow(
    #             [eachData['name'], '5m', 'Average', totalAnnualRate / numTrends, totalMonthlyRate / numTrends,
    #              totalBalance / numTrends, totalNumDays / numTrends,
    #              0, 0])
    #
    #         ################################################################################################
    #         dataFile = eachData['datasets'][2]
    #         eachData['15mResults'] = {}
    #         totalAnnualRate = 0
    #         totalMonthlyRate = 0
    #         totalNumDays = 0
    #         totalBalance = 0
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['uptrendDates'][0],
    #                                                                               eachData['uptrendDates'][1])
    #         writer.writerow([eachData['name'], '15m', 'up', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['uptrendDates'][0], eachData['uptrendDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['15mResults']['uptrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                               numOfDays=numOfDays,
    #         #                                               finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['downtrendDates'][0],
    #                                                                               eachData['downtrendDates'][1])
    #         writer.writerow([eachData['name'], '15m', 'down', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['downtrendDates'][0], eachData['downtrendDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['15mResults']['downtrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                                 numOfDays=numOfDays,
    #         #                                                 finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['sidewaysDates'][0],
    #                                                                               eachData['sidewaysDates'][1])
    #         writer.writerow([eachData['name'], '15m', 'sideways', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['sidewaysDates'][0], eachData['sidewaysDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['15mResults']['sidewaysResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                                numOfDays=numOfDays,
    #         #                                                finalBalance=finalBalance)
    #
    #         annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['randomDates'][0],
    #                                                                               eachData['randomDates'][1])
    #         writer.writerow([eachData['name'], '15m', 'random', annualRate, monthlyRate, finalBalance, numOfDays,
    #                          eachData['randomDates'][0], eachData['randomDates'][1]])
    #         totalAnnualRate += annualRate
    #         totalMonthlyRate += monthlyRate
    #         totalBalance += finalBalance
    #         totalNumDays += numOfDays
    #         # eachData['15mResults']['randomResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
    #         #                                              numOfDays=numOfDays,
    #         #                                              finalBalance=finalBalance)
    #
    #         writer.writerow(
    #             [eachData['name'], '15m', 'Average', totalAnnualRate / numTrends, totalMonthlyRate / numTrends,
    #              totalBalance / numTrends, totalNumDays / numTrends,
    #              0, 0])
    #endregion


    # timeCounterWrapper(dataFile=BTCUSDT['datasets'][2],begin=datetime(2019,1,1),end=datetime(2019,3,15))



    # timeCounterWrapper(BTCUSDT['datasets'][2], BTCUSDT['uptrendDates'][0],BTCUSDT['uptrendDates'][1])
    # timeCounterWrapper(BTCUSDT['datasets'][1], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1])
    # timeCounterWrapper(BTCUSDT['datasets'][2], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1])
    # timeCounterWrapper(BTCUSDT['datasets'][2], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1])

    resultFile='results//'


    # mainNoGates(BTCUSDT['datasets'][0], BTCUSDT['uptrendDates'][0],BTCUSDT['uptrendDates'][1],resultFile+'No Gates 1m uptrend - 8')
    # mainNoGates(BTCUSDT['datasets'][0], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],resultFile+'No Gates 1m downtrend - 8')
    # mainNoGates(BTCUSDT['datasets'][0], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],resultFile+'No Gates 1m sideways - 8')
    # mainNoGates(BTCUSDT['datasets'][0], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1],resultFile+'No Gates 1m random - 8')

    # mainNoGates(BTCUSDT['datasets'][1], BTCUSDT['uptrendDates'][0],BTCUSDT['uptrendDates'][1],resultFile+'No Gates 5m uptrend - 7')
    # mainNoGates(BTCUSDT['datasets'][1], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],resultFile+'No Gates 5m downtrend - 7')
    # mainNoGates(BTCUSDT['datasets'][1], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],resultFile+'No Gates 5m sideways - 7')
    # mainNoGates(BTCUSDT['datasets'][1], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1],resultFile+'No Gates 5m random - 7')
    #
    # mainNoGates(BTCUSDT['datasets'][2], BTCUSDT['uptrendDates'][0],BTCUSDT['uptrendDates'][1],resultFile+'No Gates 15m uptrend - 8')
    # mainNoGates(BTCUSDT['datasets'][2], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],resultFile+'No Gates 15m downtrend - 8')
    mainNoGates(BTCUSDT['datasets'][2], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],resultFile+'No Gates 15m sideways - 8')
    # mainNoGates(BTCUSDT['datasets'][2], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1],resultFile+'No Gates 15m random - 8')
    #
    # ##########################################################################################
    # mainZZGateOnly(BTCUSDT['datasets'][0], BTCUSDT['uptrendDates'][0], BTCUSDT['uptrendDates'][1], resultFile+'ZZ Gates 1m uptrend')
    # mainZZGateOnly(BTCUSDT['datasets'][0], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],
    #             resultFile+'ZZ Gates 1m downtrend')
    # mainZZGateOnly(BTCUSDT['datasets'][0], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],
    #             resultFile+'ZZ Gates 1m sideways')
    # mainZZGateOnly(BTCUSDT['datasets'][0], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1], resultFile+'ZZ Gates 1m random')
    #
    # mainZZGateOnly(BTCUSDT['datasets'][1], BTCUSDT['uptrendDates'][0], BTCUSDT['uptrendDates'][1], resultFile+'ZZ Gates 5m uptrend')
    # mainZZGateOnly(BTCUSDT['datasets'][1], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],
    #             resultFile+'ZZ Gates 5m downtrend')
    # mainZZGateOnly(BTCUSDT['datasets'][1], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],
    #             resultFile+'ZZ Gates 5m sideways')
    # mainZZGateOnly(BTCUSDT['datasets'][1], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1], resultFile+'ZZ Gates 5m random')
    #
    # mainZZGateOnly(BTCUSDT['datasets'][2], BTCUSDT['uptrendDates'][0], BTCUSDT['uptrendDates'][1], resultFile+'ZZ Gates 15m uptrend')
    # mainZZGateOnly(BTCUSDT['datasets'][2], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],
    #             resultFile+'ZZ Gates 15m downtrend')
    # mainZZGateOnly(BTCUSDT['datasets'][2], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],
    #             resultFile+'ZZ Gates 15m sideways')
    # mainZZGateOnly(BTCUSDT['datasets'][2], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1], resultFile+'ZZ Gates 15m random')
    #
    # #############################################################################################
    #
    # mainPriceGateZZGate(BTCUSDT['datasets'][0], BTCUSDT['uptrendDates'][0], BTCUSDT['uptrendDates'][1], resultFile+'ZZandP Gates 1m uptrend')
    # mainPriceGateZZGate(BTCUSDT['datasets'][0], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],
    #                     resultFile + 'ZZandP Gates 1m downtrend')
    # mainPriceGateZZGate(BTCUSDT['datasets'][0], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],
    #                     resultFile + 'ZZandP Gates 1m sideways - 5')
    # mainPriceGateZZGate(BTCUSDT['datasets'][0], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1], resultFile+'ZZandP Gates 1m random')
    #
    # mainPriceGateZZGate(BTCUSDT['datasets'][1], BTCUSDT['uptrendDates'][0], BTCUSDT['uptrendDates'][1], resultFile+'ZZandP Gates 5m uptrend')
    # mainPriceGateZZGate(BTCUSDT['datasets'][1], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],
    #                     resultFile + 'ZZandP Gates 5m downtrend')
    # mainPriceGateZZGate(BTCUSDT['datasets'][1], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],
    #                     resultFile +'ZZandP Gates 5m sideways - 5')
    # mainPriceGateZZGate(BTCUSDT['datasets'][1], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1], resultFile+'ZZandP Gates 5m random')
    #
    # mainPriceGateZZGate(BTCUSDT['datasets'][2], BTCUSDT['uptrendDates'][0], BTCUSDT['uptrendDates'][1], resultFile+'ZZandP Gates 15m uptrend')
    # mainPriceGateZZGate(BTCUSDT['datasets'][2], BTCUSDT['downtrendDates'][0], BTCUSDT['downtrendDates'][1],
    #             resultFile+'ZZandP Gates 15m downtrend')
    # mainPriceGateZZGate(BTCUSDT['datasets'][2], BTCUSDT['sidewaysDates'][0], BTCUSDT['sidewaysDates'][1],
    #             resultFile+'ZZandP Gates 15m sideways - 5')
    # mainPriceGateZZGate(BTCUSDT['datasets'][2], BTCUSDT['randomDates'][0], BTCUSDT['randomDates'][1], resultFile+'ZZandP Gates 15m random')
    
    
    



    ELAPSED = time.time() - OVERALL_START

    print("WHOLE OPERATION took a total of %.2f seconds." % (ELAPSED))

