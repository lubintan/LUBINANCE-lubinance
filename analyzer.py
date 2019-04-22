from analyzerFunctions import *
from testInfo import *
import csv


def main(dataFile,begin,end):
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

       #
    # region: add lowFirst column if no timing data
    if 'lowFirst' not in df.columns: df['lowFirst'] = df.open < df.close
    df = pd.DataFrame(df.iloc[:]).reset_index(drop=True)
    # endregion
    trendLine1, trendLine2, trendLine3 = getActiveTrend(df)

    # region:all bars
    # allBars = Ohlc(name='All Bars', x=df.date, open=df.open,
    #                close=df.close, high=df.high, low=df.low,
    #                opacity=0.8,
    #                line=dict(width=2.5),
    #                # hoverinfo='none',
    #                hoverlabel=dict(bgcolor='pink'),
    #
    #                # showlegend=False,
    #                # increasing=dict(line=dict(color= '#17BECF')),
    #                # decreasing=dict(line=dict(color= '#17BECF')),
    #                # increasing=dict(line=dict(color='black')),
    #                # decreasing=dict(line=dict(color='black')),
    #                )
    # endregion



    # region:trendlines plotting
    # plot minor trendline points and lines
    # minor= plotTrendlines(trendLine1, name='Minor', color='brown', width=3)

    # # plot intermediate trendline points and lines
    # intermediate, intermediateTops, intermediateBottoms = plotTrendlines(trendLine2, intermediateStuff,
    #                                                                      name='Intermediate', color='orange', width=3)
    #
    # major, majorTops, majorBottoms = plotTrendlines(trendLine3, majorStuff, name='Major', color='navy', width=4)

    # # region: major data to plot
    # majorData = [
    #     allBars,
    #     # minor,
    #     ]
    #
    # majorFig = Figure(data=majorData,
    #                   layout=Layout(title=dataFile,xaxis=dict(
    #         rangeslider=dict(
    #             visible=False
    #         ),)))
    # plotly.offline.plot(majorFig)
    #endregion



    #region: analysis

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
    print('end assetsBTC:', btcAssets, '=', btcAssets * df.iloc[-1].close, 'USDT')

    totalHoldings = assets + (btcAssets * df.iloc[-1].close)

    days = (df.iloc[-1].date - df.iloc[0].date).days

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





    return annualRate, monthlyRate, days, totalHoldings


def timeCounterWrapper(dataFile, begin, end):
    startTime = time.time()

    annualRate, monthlyRate, numOfDays,finalBalance = main(dataFile, begin, end)

    endTime = time.time()
    elapsed = endTime - startTime
    print("Operation took a total of %.2f seconds." % (elapsed))
    print()

    return annualRate, monthlyRate, numOfDays, finalBalance

    time.sleep(2)


if __name__ == '__main__':

    OVERALL_START = time.time()

    numTrends = 4.0

    with open(
            "{}_{}.csv".format(
                'lubinanaceSimData100USDT',
                time.time()
            ),
            mode='w+'  # set file write mode
    ) as f:
        writer = csv.writer(f)
        writer.writerow(['Crypto Pair', 'Interval', 'Trend','Annual Rate', 'Monthly Rate', 'Final Balance','Sample Days', 'Sample Start', 'Sample End'])

        for eachData in allData:

            dataFile = eachData['datasets'][0]
            eachData['1mResults']={}
            totalAnnualRate = 0
            totalMonthlyRate = 0
            totalNumDays = 0
            totalBalance = 0

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['uptrendDates'][0],
                                                                                  eachData['uptrendDates'][1])
            writer.writerow([eachData['name'], '1m', 'up', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['uptrendDates'][0], eachData['uptrendDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['1mResults']['uptrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
            #                                               finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['downtrendDates'][0],
                                                                                  eachData['downtrendDates'][1])
            writer.writerow([eachData['name'], '1m', 'down', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['downtrendDates'][0], eachData['downtrendDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['1mResults']['downtrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
            #                                                 finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['sidewaysDates'][0],
                                                                                  eachData['sidewaysDates'][1])
            writer.writerow([eachData['name'], '1m', 'sideways', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['sidewaysDates'][0], eachData['sidewaysDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['1mResults']['sidewaysResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
            #                                                finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['randomDates'][0],
                                                                                  eachData['randomDates'][1])
            writer.writerow([eachData['name'], '1m', 'random', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['randomDates'][0], eachData['randomDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['1mResults']['randomResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate, numOfDays=numOfDays,
            #                                              finalBalance=finalBalance)



            writer.writerow([eachData['name'], '1m', 'Average', totalAnnualRate/numTrends, totalMonthlyRate/numTrends, totalBalance/numTrends, totalNumDays/numTrends,
                             0, 0])

    ##########################################################
            dataFile = eachData['datasets'][1]
            eachData['5mResults'] = {}
            totalAnnualRate = 0
            totalMonthlyRate = 0
            totalNumDays = 0
            totalBalance = 0

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['uptrendDates'][0],
                                                                                  eachData['uptrendDates'][1])
            writer.writerow([eachData['name'], '5m', 'up', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['uptrendDates'][0], eachData['uptrendDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['5mResults']['uptrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                               numOfDays=numOfDays,
            #                                               finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['downtrendDates'][0],
                                                                                  eachData['downtrendDates'][1])
            writer.writerow([eachData['name'], '5m', 'down', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['downtrendDates'][0], eachData['downtrendDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['5mResults']['downtrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                                 numOfDays=numOfDays,
            #                                                 finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['sidewaysDates'][0],
                                                                                  eachData['sidewaysDates'][1])
            writer.writerow([eachData['name'], '5m', 'sideways', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['sidewaysDates'][0], eachData['sidewaysDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['5mResults']['sidewaysResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                                numOfDays=numOfDays,
            #                                                finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['randomDates'][0],
                                                                                  eachData['randomDates'][1])
            writer.writerow([eachData['name'], '5m', 'random', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['randomDates'][0], eachData['randomDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['5mResults']['randomResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                              numOfDays=numOfDays,
            #                                              finalBalance=finalBalance)

            writer.writerow(
                [eachData['name'], '5m', 'Average', totalAnnualRate / numTrends, totalMonthlyRate / numTrends,
                 totalBalance / numTrends, totalNumDays / numTrends,
                 0, 0])

            ################################################################################################
            dataFile = eachData['datasets'][2]
            eachData['15mResults'] = {}
            totalAnnualRate = 0
            totalMonthlyRate = 0
            totalNumDays = 0
            totalBalance = 0

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['uptrendDates'][0],
                                                                                  eachData['uptrendDates'][1])
            writer.writerow([eachData['name'], '15m', 'up', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['uptrendDates'][0], eachData['uptrendDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['15mResults']['uptrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                               numOfDays=numOfDays,
            #                                               finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['downtrendDates'][0],
                                                                                  eachData['downtrendDates'][1])
            writer.writerow([eachData['name'], '15m', 'down', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['downtrendDates'][0], eachData['downtrendDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['15mResults']['downtrendResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                                 numOfDays=numOfDays,
            #                                                 finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['sidewaysDates'][0],
                                                                                  eachData['sidewaysDates'][1])
            writer.writerow([eachData['name'], '15m', 'sideways', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['sidewaysDates'][0], eachData['sidewaysDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['15mResults']['sidewaysResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                                numOfDays=numOfDays,
            #                                                finalBalance=finalBalance)

            annualRate, monthlyRate, numOfDays, finalBalance = timeCounterWrapper(dataFile, eachData['randomDates'][0],
                                                                                  eachData['randomDates'][1])
            writer.writerow([eachData['name'], '15m', 'random', annualRate, monthlyRate, finalBalance, numOfDays,
                             eachData['randomDates'][0], eachData['randomDates'][1]])
            totalAnnualRate += annualRate
            totalMonthlyRate += monthlyRate
            totalBalance += finalBalance
            totalNumDays += numOfDays
            # eachData['15mResults']['randomResults'] = dict(annualRate=annualRate, monthlyRate=monthlyRate,
            #                                              numOfDays=numOfDays,
            #                                              finalBalance=finalBalance)

            writer.writerow(
                [eachData['name'], '15m', 'Average', totalAnnualRate / numTrends, totalMonthlyRate / numTrends,
                 totalBalance / numTrends, totalNumDays / numTrends,
                 0, 0])

    ELAPSED = time.time() - OVERALL_START

    print("WHOLE OPERATION took a total of %.2f seconds." % (ELAPSED))

