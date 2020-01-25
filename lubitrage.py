from interactData import *
from datetime import timedelta

depth = 2
targetPercent = 1.005
pollInterval = 0.3

microInterval = 0.1

counterLimit = 12




def cumulative_qty_for_selling(client,pair,price):
    limit = '5'
    orders = get_order_book(client, pair, limit=limit)
    depthIndex = depth - 5
    bids = orders['bids']

    cumQty = 0
    for eachBid in bids:
        if float(eachBid[0]) > price:
            cumQty += float(eachBid[1])

    return cumQty


def cumulative_qty_for_buying(client, pair, price):
    limit = '5'
    orders = get_order_book(client, pair, limit=limit)
    depthIndex = depth - 5
    asks = orders['asks']

    cumQty = 0
    for eachAsk in asks:
        if float(eachAsk[0]) > price:
            cumQty += float(eachAsk[1])

    return cumQty

def worst_order_for_selling(client,pair):
    limit = '5'
    orders = get_order_book(client, pair, limit=limit)
    depthIndex = depth - 5
    bids = orders['bids']

    if len(bids) != 5: return None, None

    worstBid = bids[depthIndex]
    worstPrc = float(worstBid[0])
    worstQty = float(worstBid[1])

    return worstPrc, worstQty

def worst_order_for_buying(client,pair):
    limit = '5'
    orders = get_order_book(client, pair, limit=limit)
    depthIndex = depth - 5
    asks = orders['asks']

    if len(asks) != 5: return None, None
    worstAsk = asks[depthIndex]
    worstPrc = float(worstAsk[0])
    worstQty = float(worstAsk[1])

    return worstPrc, worstQty

def pri_to_sec(client,baseQty,baseAsset,priAsset,secAsset,targetHits,beginTime):
    startTime = time.time()
    print()
    if len(targetHits) > 0:
        for each in targetHits:
            print(each)
        print()
    print(baseAsset, priAsset, secAsset)

    target = baseQty * targetPercent

    priPrc, priQty = worst_order_for_buying(client, priAsset + baseAsset)
    secPrc, secQty = worst_order_for_buying(client, secAsset + priAsset)
    terPrc, terQty = worst_order_for_selling(client, secAsset + baseAsset)

    if priPrc == None or secPrc == None or terPrc == None or priQty == None or secQty == None or terQty == None:
        time.sleep(pollInterval)
        return

    priQtyDes = baseQty / priPrc
    secQtyDes = priQtyDes / secPrc
    finQty = secQtyDes * terPrc

    priFmtPrc, priFmtQty = formattedPrcQty('BTC', priPrc, priQtyDes)
    secFmtPrc, secFmtQty = formattedPrcQty('BTC', secPrc, secQtyDes)
    terFmtPrc, terFmtQty = formattedPrcQty('BTC', terPrc, secQtyDes)

    priTest = priQtyDes < priQty
    secTest = secQtyDes < secQty
    terTest = secQtyDes < terQty
    finTest = finQty > target
    execute = priTest and secTest and terTest and finTest
    print(priTest)
    print(secTest)
    print(terTest)
    print(finTest)
    print('%.4f' % (finQty / baseQty))

    # execution part

    if finTest:
        targetHits.append([finQty / baseQty, baseAsset, priAsset, secAsset])

    if execute:
        # test execution
        priExcQty = cumulative_qty_for_buying(client, priAsset + baseAsset, priPrc)
        secExcQty = cumulative_qty_for_buying(client, secAsset + priAsset, secPrc)
        terExcQty = cumulative_qty_for_selling(client, secAsset + baseAsset, terPrc)

        priExcTest = priQtyDes < priExcQty
        secExcTest = secQtyDes < secExcQty
        terExcTest = secQtyDes < terExcQty

        clearedExec = priExcTest and secExcTest and terExcTest

        print(priExcTest, secExcTest, terExcTest)
        print(clearedExec)

    endTime = time.time()
    timeTaken = endTime - startTime
    timeSince = timedelta(seconds=endTime) - timedelta(seconds=beginTime)

    print('TimeTaken: %3fs' % (timeTaken))
    print('Time Since Start:', timeSince)

def sec_to_pri(client,baseQty,baseAsset,pri,sec,targetHits,beginTime):

    priAsset = sec
    secAsset = pri

    startTime = time.time()
    print()
    if len(targetHits) > 0:
        for each in targetHits:
            print(each)
        print()
    print(baseAsset, priAsset, secAsset)

    target = baseQty * targetPercent

    priPrc, priQty = worst_order_for_buying(client, priAsset + baseAsset)
    secPrc, secQty = worst_order_for_selling(client, priAsset + secAsset)
    terPrc, terQty = worst_order_for_selling(client, secAsset + baseAsset)

    if priPrc == None or secPrc == None or terPrc == None or priQty == None or secQty == None or terQty == None:
        time.sleep(pollInterval)
        return

    priQtyDes = baseQty / priPrc
    secQtyDes = priQtyDes * secPrc
    finQty = secQtyDes * terPrc

    priFmtPrc, priFmtQty = formattedPrcQty('BTC', priPrc, priQtyDes)
    secFmtPrc, secFmtQty = formattedPrcQty('BTC', secPrc, secQtyDes)
    terFmtPrc, terFmtQty = formattedPrcQty('BTC', terPrc, secQtyDes)

    priTest = priQtyDes < priQty
    secTest = secQtyDes < secQty
    terTest = secQtyDes < terQty
    finTest = finQty > target
    execute = priTest and secTest and terTest and finTest
    print(priTest)
    print(secTest)
    print(terTest)
    print(finTest)
    print('%.4f' % (finQty / baseQty))

    # execution part

    if finTest:
        targetHits.append([finQty / baseQty, baseAsset, priAsset, secAsset])

    if execute:
        # test execution
        priExcQty = cumulative_qty_for_buying(client, priAsset + baseAsset, priPrc)
        secExcQty = cumulative_qty_for_selling(client, priAsset + secAsset, secPrc)
        terExcQty = cumulative_qty_for_selling(client, secAsset + baseAsset, terPrc)

        priExcTest = priQtyDes < priExcQty
        secExcTest = secQtyDes < secExcQty
        terExcTest = secQtyDes < terExcQty

        clearedExec = priExcTest and secExcTest and terExcTest

        print(priExcTest, secExcTest, terExcTest)
        print(clearedExec)

    endTime = time.time()
    timeTaken = endTime - startTime
    timeSince = timedelta(seconds=endTime) - timedelta(seconds=beginTime)

    print('TimeTaken: %3fs' % (timeTaken))
    print('Time Since Start:', timeSince)

def pri_to_sec_mkt_prc(client,baseQty,baseAsset,priAsset,secAsset,targetHits,beginTime):
    startTime = time.time()
    print()
    if len(targetHits) > 0:
        for each in targetHits:
            print(each)
        print()
    print(baseAsset, priAsset, secAsset)

    target = baseQty * targetPercent

    totalVol = get_past_volume(client,secAsset+priAsset)

    prices = client.get_all_tickers()
    for each in prices:
        if each['symbol'] == priAsset + baseAsset:
            priPrc = float(each['price'])
        if each['symbol'] == secAsset + priAsset:
            secPrc = float(each['price'])
        if each['symbol'] == secAsset + baseAsset:
            terPrc = float(each['price'])


    # priPrc = get_price(client, priAsset + baseAsset)
    # secPrc = get_price(client, secAsset + priAsset)
    # terPrc = get_price(client, secAsset + baseAsset)

    if priPrc == None or secPrc == None or terPrc == None:
        time.sleep(pollInterval)
        return None

    priQtyDes = baseQty / priPrc
    secQtyDes = priQtyDes / secPrc

    if totalVol < secQtyDes:
        print('** Not Enough Volume ** ')
        return None

    finQty = secQtyDes * terPrc

    # priFmtPrc, priFmtQty = formattedPrcQty('BTC', priPrc, priQtyDes)
    # secFmtPrc, secFmtQty = formattedPrcQty('BTC', secPrc, secQtyDes)
    # terFmtPrc, terFmtQty = formattedPrcQty('BTC', terPrc, secQtyDes)

    finTest = finQty > target
    # print(finTest)
    # print('%.4f' % (finQty / baseQty))

    # execution part

    if finTest:

        #Buy PPP-USDT
        priFmtPrc, priFmtQty = formattedPrcQty(priAsset+baseAsset, priPrc, priQtyDes)
        buyId = limit_buy(client,priAsset+baseAsset,priFmtQty,priFmtPrc)
        counter = 0
        while get_order_status(client,priAsset+baseAsset,buyId) != Client.ORDER_STATUS_FILLED:
            if counter >= counterLimit:
                cancel_order(client,priAsset+baseAsset,buyId)
                print('Order', buyId, 'Cancelled')
                return None
            time.sleep(microInterval)
            print('Waiting on',priAsset+baseAsset)
            counter += 1

        #Buy SSS-PPP
        priQty = get_asset_balance(client,priAsset)
        secQty = priQty/secPrc
        secFmtPrc, secFmtQty = formattedPrcQty(secAsset+priAsset, secPrc, secQty)

        buyId2 = limit_buy(client,secAsset+priAsset,secFmtQty,secFmtPrc)
        while get_order_status(client,secAsset+priAsset,buyId2) != Client.ORDER_STATUS_FILLED:
            time.sleep(microInterval)
            print('Waiting on',secAsset+priAsset)

        #Sell SSS-USDT
        secQty = get_asset_balance(client,secAsset)
        terFmtPrc, terFmtQty = formattedPrcQty(secAsset+baseAsset, terPrc, secQty)
        sellId = limit_sell(client,secAsset+baseAsset,terFmtQty,terFmtPrc)
        while get_order_status(client,secAsset+baseAsset,sellId) != Client.ORDER_STATUS_FILLED:
            time.sleep(2*microInterval)
            print('Waiting on', secAsset+baseAsset)

        finQty = get_cumQty(client,secAsset+baseAsset,sellId)
        finQty = 0.999 * finQty




        # print('priQty', priQtyDes, 'secQty', secQtyDes, 'finQty',finQty)
        # print(priAsset+baseAsset,'priPrc', priPrc,'|',secAsset+priAsset, 'secPrc',secPrc,'| terPrc',terPrc)
        targetHits.append([finQty / baseQty, baseAsset, priAsset, secAsset])
        # test execution
        # priExcQty = cumulative_qty_for_buying(client, priAsset + baseAsset, priPrc)
        # secExcQty = cumulative_qty_for_buying(client, secAsset + priAsset, secPrc)
        # terExcQty = cumulative_qty_for_selling(client, secAsset + baseAsset, terPrc)
        #
        # priExcTest = priQtyDes < priExcQty
        # secExcTest = secQtyDes < secExcQty
        # terExcTest = secQtyDes < terExcQty
        #
        # clearedExec = priExcTest and secExcTest and terExcTest
        #
        # print(priExcTest, secExcTest, terExcTest)
        # print('Execution Test:',clearedExec)

        return finQty

    endTime = time.time()
    timeTaken = endTime - startTime
    timeSince = timedelta(seconds=endTime) - timedelta(seconds=beginTime)

    print('TimeTaken: %3fs' % (timeTaken))
    print('Time Since Start:', timeSince)
    return None

def sec_to_pri_mkt_prc(client,baseQty,baseAsset,pri,sec,targetHits,beginTime):
    priAsset = sec
    secAsset = pri

    startTime = time.time()
    print()
    if len(targetHits) > 0:
        for each in targetHits:
            print(each)
        print()
    print(baseAsset, priAsset, secAsset)

    target = baseQty * targetPercent
    totalVol = get_past_volume(client, priAsset+secAsset)

    prices = client.get_all_tickers()
    for each in prices:
        if each['symbol'] == priAsset + baseAsset:
            priPrc = float(each['price'])
        if each['symbol'] == priAsset + secAsset:
            secPrc = float(each['price'])
        if each['symbol'] == secAsset + baseAsset:
            terPrc = float(each['price'])

    # priPrc = get_price(client, priAsset + baseAsset)
    # secPrc = get_price(client, priAsset + secAsset)
    # terPrc = get_price(client, secAsset + baseAsset)

    if priPrc == None or secPrc == None or terPrc == None:
        time.sleep(pollInterval)
        return None

    priQtyDes = baseQty / priPrc

    if totalVol < priQtyDes:
        print('** Not Enough Volume ** ')
        return None

    secQtyDes = priQtyDes * secPrc
    finQty = secQtyDes * terPrc

    # priFmtPrc, priFmtQty = formattedPrcQty('BTC', priPrc, priQtyDes)
    # secFmtPrc, secFmtQty = formattedPrcQty('BTC', secPrc, secQtyDes)
    # terFmtPrc, terFmtQty = formattedPrcQty('BTC', terPrc, secQtyDes)

    finTest = finQty > target

    print(finTest)
    print('%.4f' % (finQty / baseQty))

    # execution part

    if finTest:

        # Buy PPP-USDT
        priFmtPrc, priFmtQty = formattedPrcQty(priAsset+baseAsset, priPrc, priQtyDes)
        buyId = limit_buy(client, priAsset + baseAsset, priFmtQty, priFmtPrc)

        counter = 0
        while get_order_status(client, priAsset + baseAsset, buyId) != Client.ORDER_STATUS_FILLED:
            if counter >= counterLimit:
                cancel_order(client, priAsset + baseAsset, buyId)
                print('Order',buyId,'Cancelled')
                return None
            time.sleep(microInterval)
            print('Waiting on', priAsset + baseAsset)

            counter += 1

        # Sell PPP-SSS
        priQty = get_asset_balance(client, priAsset)
        secFmtPrc, secFmtQty = formattedPrcQty(priAsset+secAsset, secPrc, priQty)
        sellId = limit_sell(client, priAsset+secAsset, secFmtQty, secFmtPrc)
        while get_order_status(client, priAsset+secAsset, sellId) != Client.ORDER_STATUS_FILLED:
            time.sleep(microInterval)
            print('Waiting on', priAsset+secAsset)

        # Sell SSS-USDT
        secQty = get_asset_balance(client, secAsset)
        terFmtPrc, terFmtQty = formattedPrcQty(secAsset + baseAsset, terPrc, secQty)
        sellId2 = limit_sell(client, secAsset + baseAsset, terFmtQty, terFmtPrc)
        while get_order_status(client, secAsset + baseAsset, sellId2) != Client.ORDER_STATUS_FILLED:
            time.sleep(2 * microInterval)
            print('Waiting on', secAsset + baseAsset)

        finQty = get_cumQty(client,secAsset+baseAsset, sellId2)
        finQty = 0.999 * finQty



        # print('priQty', priQtyDes, 'secQty', secQtyDes, 'finQty', finQty)
        # print(priAsset+baseAsset,'priPrc', priPrc,'|',priAsset+secAsset, 'secPrc', secPrc,'| terPrc', terPrc)
        targetHits.append([finQty / baseQty, baseAsset, priAsset, secAsset])
        # priExcQty = cumulative_qty_for_buying(client, priAsset + baseAsset, priPrc)
        # secExcQty = cumulative_qty_for_selling(client, priAsset + secAsset, secPrc)
        # terExcQty = cumulative_qty_for_selling(client, secAsset + baseAsset, terPrc)
        #
        # priExcTest = priQtyDes < priExcQty
        # secExcTest = secQtyDes < secExcQty
        # terExcTest = secQtyDes < terExcQty
        #
        # clearedExec = priExcTest and secExcTest and terExcTest
        #
        # print(priExcTest, secExcTest, terExcTest)
        # print('Execution cleared:', clearedExec)

        return finQty

    endTime = time.time()
    timeTaken = endTime - startTime
    timeSince = timedelta(seconds=endTime) - timedelta(seconds=beginTime)

    print('TimeTaken: %3fs' % (timeTaken))
    print('Time Since Start:', timeSince)
    return None

def lubitrage():
    client = Client(apiK, sK)



    stableCoins = ['USDT']
    mainMkts = ['BTC', 'ETH']

    baseAssets = stableCoins
    priAssets = mainMkts
    targetHits=[]
    beginTime = time.time()
    print('startTime',datetime.now())
    baseQty = 50.0
    while True:
        try:
            for baseAsset in baseAssets:
                for priAsset in priAssets:

                    for secAsset in trgPairs[baseAsset + priAsset]:
                        time.sleep(.4)
                        result = pri_to_sec_mkt_prc(client,baseQty,baseAsset,priAsset,secAsset,targetHits,beginTime)

                        if result != None:
                            baseQty = result

                        time.sleep(.4)
                        result = sec_to_pri_mkt_prc(client, baseQty, baseAsset, priAsset, secAsset, targetHits, beginTime)

                        if result != None:
                            baseQty = result

                    # input()
        #check that order can go through




        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                OSError) as e:
            print(e)
            continue


        except(BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException,
               BinanceOrderMinPriceException,
               BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceRequestException) as e:

            print(e)
            continue


if __name__ == '__main__':
    lubitrage()
