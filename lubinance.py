from interactData import *
from analyzerFunctions import *



def lubinance():


        startingUSD = float(1e3)
        assets = startingUSD
        btcAssets = 0
        txFee = 0.002  # 0.22%

        totalUSDTtxed = 0



        client = Client(apiK,sK)

        prevDate = datetime(2018,1,1)


        while True:
            time.sleep(4)

            start_time = time.time()

            dataPoints = getPricePanda(client,'BTCUSDT',client.KLINE_INTERVAL_1MINUTE,'30 minutes ago UTC')
            dataPoints['lowFirst'] = dataPoints.open < dataPoints.close

            currentDate = dataPoints.iloc[-1].date

            if currentDate == prevDate: continue

            prevDate = currentDate

            currentPrice = get_price(client,'BTCUSDT')

            print('-------------------------')
            print('date', currentDate, 'current BTC/USDT price:', currentPrice)

            min = getActiveTrend(dataPoints)

            if len(min) < 4:
                print('not enough points')
                continue

            # if min.iloc[-1].date != currentDate:  # "inside bar, skip"
            #     print('inside bar, skip')
            #     continue

            min = min.reset_index(drop=True)

            # btcAssets = get_asset_balance(client,'BTC')
            # assets = get_asset_balance(client, 'USDT')


            # sell condition
            if (min.iloc[-3].point < min.iloc[-2].point) and (min.iloc[-1].point < min.iloc[-2].point):

                if btcAssets == 0:
                    print(str(min.iloc[-1].date), ': no BTC to sell')
                    continue

                sellPrice = currentPrice

                assets = btcAssets * sellPrice

                assets = np.round(assets * (1 - txFee), 3)

                btcAssets = 0

                totalUSDTtxed += assets

                print(str(currentDate), 'sell at:', sellPrice, 'assets:', assets, 'USD')





            elif (min.iloc[-3].point > min.iloc[-2].point) and (min.iloc[-1].point > min.iloc[-2].point):

                if assets == 0:
                    print(min.iloc[-1].date, ': no USDT to buy BTC with')
                    continue

                buyPrice = currentPrice


                btcAssets = assets / buyPrice
                btcAssets = np.round(btcAssets * (1 - txFee), 3)

                assets = 0

                totalUSDTtxed += btcAssets * buyPrice

                print(str(currentDate), 'buy at:', buyPrice, 'assets:', btcAssets, 'BTC')
            else:
                print('no tx')

            print('Total Txed:', totalUSDTtxed)
            print('USDT:', assets)
            print('BTC:',btcAssets)



            elapsed = time.time() - start_time
            print('Time Taken:',elapsed,'s')


if __name__ == '__main__':
    lubinance()

