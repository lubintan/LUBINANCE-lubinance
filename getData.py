import dateparser
import pytz,time
from datetime import datetime
from binance.client import Client
import csv


def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds

    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str

    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms

# uses the date_to_milliseconds and interval_to_milliseconds functions
# https://gist.github.com/sammchardy/3547cfab1faf78e385b3fcb83ad86395
# https://gist.github.com/sammchardy/fcbb2b836d1f694f39bddd569d1c16fe



def get_historical_klines(symbol, interval, start_str, end_str=None):
    """Get Historical Klines from Binance

    See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

    If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date string in UTC format
    :type start_str: str
    :param end_str: optional - end date string in UTC format
    :type end_str: str

    :return: list of OHLCV values

    """


    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    # convert our date strings to milliseconds
    start_ts = date_to_milliseconds(start_str)

    # if an end time was passed convert it
    end_ts = None
    if end_str:
        end_ts = date_to_milliseconds(end_str)

    idx = 0
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts,
            endTime=end_ts
        )

        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)

    return output_data

def getData(symbol, interval, start,end):
    startTime = time.time()

    # symbol = "BTCUSDT"
    # start = str(1559059200000-3600000)
    # end = "1559318400000"
    # interval = Client.KLINE_INTERVAL_15MINUTE

    # start = "1559520000000"
    # end= "1559779200000"


    # create the Binance client, no need for api key
    client = Client("", "")

    # info = client.get_symbol_info('BNBBTC')
    #
    # print(info)
    # exit()

    # klines = client.get_historical_klines(symbol, interval, start, end)

    startStr = '260619'
    endStr = '280619'

    # open a file with filename including symbol, interval and start and end converted to milliseconds
    with open(
            "{}_to_{}_analysis//{}_{}.csv".format(
                startStr,
                endStr,
                symbol,
                interval,

            ),
            mode='w'  # set file write mode
    ) as f:
        writer = csv.writer(f)

        writer.writerow(['DateTime','open','high','low','close','vol'])

        for row in client.get_historical_klines_generator(symbol, interval, start, end):
            writer.writerow([
                datetime.utcfromtimestamp(row[0]/1000),
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                ]
            )

            # print(datetime.utcfromtimestamp(row[0]/1000))


    endtime = time.time()

    print('Process took: %.2f seconds'%(endtime-startTime))

if __name__ == '__main__':

    # markets=['LTCUSDT','EOSUSDT','XLMUSDT','ZECUSDT','BTTUSDT','ETHUSDT','QTUMUSDT']
    # # markets = ['ZECUSDT']
    # intervals = [Client.KLINE_INTERVAL_1MINUTE,Client.KLINE_INTERVAL_5MINUTE, Client.KLINE_INTERVAL_15MINUTE,
    #              Client.KLINE_INTERVAL_30MINUTE,
    #              Client.KLINE_INTERVAL_1HOUR]
    # 
    # 
    # for sym in markets:
    #     for inter in intervals:
    #         print(sym, 'requesting')
    # 
    #         getData(sym,inter)
    # 
    #         print(sym, 'done')
    #         print()

    
    A = [[1.000551761348488, 'USDT', 'BTC', 'MITH'],
    [1.000983030239766, 'USDT', 'BTC', 'ATOM'],
    [1.000661505994268, 'USDT', 'BTC', 'ZRX'],
    [1.0007296419310914, 'USDT', 'BTC', 'ZEC'],
    [1.0005816091491004, 'USDT', 'BTC', 'ATOM'],
    [1.000929214289184, 'USDT', 'BTC', 'ZRX'],
    [1.0006185692485579, 'USDT', 'ETH', 'BNB'],
    [1.001447690798754, 'USDT', 'BTC', 'NULS'],
    [1.0005944967792757, 'USDT', 'ETH', 'BNB'],
    [1.0006526337655046, 'USDT', 'BTC', 'IOTA'],
    [1.000517010319798, 'USDT', 'BTC', 'MITH'],
    [1.0005833789227097, 'USDT', 'BTC', 'BNB'],
    [1.0007465771812616, 'USDT', 'ETH', 'ZEC'],
    [1.0005975395896611, 'USDC', 'ETH', 'ZEC'],
    [1.0005402896000473, 'USDT', 'BTC', 'XMR'],
    [1.0025039918710987, 'USDT', 'BTC', 'FTM'],
    [1.0009446284261714, 'USDT', 'ETH', 'NULS'],
    [1.0008923458388692, 'USDT', 'BTC', 'ZRX'],
    [1.0006360568989594, 'USDT', 'BTC', 'ZRX'],
    [1.0006024522602397, 'USDT', 'BTC', 'ZRX'],
    [1.0008875839537665, 'USDT', 'BTC', 'ZRX'],
    [1.0009861428462472, 'USDT', 'BTC', 'ZRX'],
    [1.0010145154402534, 'USDT', 'ETH', 'IOST'],
    [1.0007765268972388, 'USDT', 'BTC', 'ATOM'],
    [1.0005169742932178, 'USDT', 'ETH', 'IOST'],
    [1.0006352476658267, 'USDT', 'BTC', 'IOTA'],
    [1.0011704518492186, 'USDC', 'BTC', 'ATOM'],
    [1.0006727117213874, 'USDC', 'BTC', 'ATOM'],
    [1.00118853900948, 'USDC', 'BTC', 'ATOM'],
    [1.000769341431225, 'USDT', 'ETH', 'ONT'],
    [1.0006393198693, 'USDT', 'BTC', 'XLM'],
    [1.0006929173019241, 'USDT', 'BTC', 'QTUM'],
    [1.0005239487819657, 'PAX', 'BTC', 'ADA'],
    [1.0013979742416386, 'USDT', 'BTC', 'MITH'],
    [1.0005222189053224, 'USDT', 'BTC', 'DASH'],
    [1.0005364725113954, 'USDT', 'BTC', 'DASH'],
    [1.0006081888996783, 'USDT', 'BTC', 'FET'],
    [1.0005628329121057, 'USDT', 'BTC', 'IOTA'],
    [1.0007372824197183, 'USDC', 'BTC', 'ATOM'],
    [1.0014620263486294, 'USDC', 'BTC', 'ATOM'],
    [1.0022620607085548, 'USDC', 'BTC', 'ATOM'],
    [1.0014014497070298, 'USDC', 'BTC', 'ATOM'],]

    B = []

    for each in A:
        B.append(each[0])

    B.sort()
    B.reverse()

    for el in B:
        print(el)

    # [1.000551761348488, 'USDT', 'BTC', 'MITH']
    # [1.000983030239766, 'USDT', 'BTC', 'ATOM']
    # [1.000661505994268, 'USDT', 'BTC', 'ZRX']
    # [1.0007296419310914, 'USDT', 'BTC', 'ZEC']
    # [1.0005816091491004, 'USDT', 'BTC', 'ATOM']
    # [1.000929214289184, 'USDT', 'BTC', 'ZRX']
    # [1.0006185692485579, 'USDT', 'ETH', 'BNB']
    # [1.001447690798754, 'USDT', 'BTC', 'NULS']
    # [1.0005944967792757, 'USDT', 'ETH', 'BNB']
    # [1.0006526337655046, 'USDT', 'BTC', 'IOTA']
    # [1.000517010319798, 'USDT', 'BTC', 'MITH']
    # [1.0005833789227097, 'USDT', 'BTC', 'BNB']
    # [1.0007465771812616, 'USDT', 'ETH', 'ZEC']
    # [1.0005975395896611, 'USDC', 'ETH', 'ZEC']
    # [1.0005402896000473, 'USDT', 'BTC', 'XMR']
    # [1.0025039918710987, 'USDT', 'BTC', 'FTM']
    # [1.0009446284261714, 'USDT', 'ETH', 'NULS']
    # [1.0008923458388692, 'USDT', 'BTC', 'ZRX']
    # [1.0006360568989594, 'USDT', 'BTC', 'ZRX']
    # [1.0006024522602397, 'USDT', 'BTC', 'ZRX']
    # [1.0008875839537665, 'USDT', 'BTC', 'ZRX']
    # [1.0009861428462472, 'USDT', 'BTC', 'ZRX']
    # [1.0010145154402534, 'USDT', 'ETH', 'IOST']
    # [1.0007765268972388, 'USDT', 'BTC', 'ATOM']
    # [1.0005169742932178, 'USDT', 'ETH', 'IOST']
    # [1.0006352476658267, 'USDT', 'BTC', 'IOTA']
    # [1.0011704518492186, 'USDC', 'BTC', 'ATOM']
    # [1.0006727117213874, 'USDC', 'BTC', 'ATOM']
    # [1.00118853900948, 'USDC', 'BTC', 'ATOM']
    # [1.000769341431225, 'USDT', 'ETH', 'ONT']
    # [1.0006393198693, 'USDT', 'BTC', 'XLM']
    # [1.0006929173019241, 'USDT', 'BTC', 'QTUM']
    # [1.0005239487819657, 'PAX', 'BTC', 'ADA']
    # [1.0013979742416386, 'USDT', 'BTC', 'MITH']
    # [1.0005222189053224, 'USDT', 'BTC', 'DASH']
    # [1.0005364725113954, 'USDT', 'BTC', 'DASH']
    # [1.0006081888996783, 'USDT', 'BTC', 'FET']
    # [1.0005628329121057, 'USDT', 'BTC', 'IOTA']
    # [1.0007372824197183, 'USDC', 'BTC', 'ATOM']
    # [1.0014620263486294, 'USDC', 'BTC', 'ATOM']
    # [1.0022620607085548, 'USDC', 'BTC', 'ATOM']
    # [1.0014014497070298, 'USDC', 'BTC', 'ATOM']
    #
    # USDT
    # BTC
    # OMG
    # True
    # True
    # True
    # False
    # 0.9946
    # TimeTaken: 0.310480
    # s
    # Time
    # Since
    # Start: 6:10: 12.709594
    #
    # [1.000551761348488, 'USDT', 'BTC', 'MITH']
    # [1.000983030239766, 'USDT', 'BTC', 'ATOM']
    # [1.000661505994268, 'USDT', 'BTC', 'ZRX']
    # [1.0007296419310914, 'USDT', 'BTC', 'ZEC']
    # [1.0005816091491004, 'USDT', 'BTC', 'ATOM']
    # [1.000929214289184, 'USDT', 'BTC', 'ZRX']
    # [1.0006185692485579, 'USDT', 'ETH', 'BNB']
    # [1.001447690798754, 'USDT', 'BTC', 'NULS']
    # [1.0005944967792757, 'USDT', 'ETH', 'BNB']
    # [1.0006526337655046, 'USDT', 'BTC', 'IOTA']
    # [1.000517010319798, 'USDT', 'BTC', 'MITH']
    # [1.0005833789227097, 'USDT', 'BTC', 'BNB']
    # [1.0007465771812616, 'USDT', 'ETH', 'ZEC']
    # [1.0005975395896611, 'USDC', 'ETH', 'ZEC']
    # [1.0005402896000473, 'USDT', 'BTC', 'XMR']
    # [1.0025039918710987, 'USDT', 'BTC', 'FTM']
    # [1.0009446284261714, 'USDT', 'ETH', 'NULS']
    # [1.0008923458388692, 'USDT', 'BTC', 'ZRX']
    # [1.0006360568989594, 'USDT', 'BTC', 'ZRX']
    # [1.0006024522602397, 'USDT', 'BTC', 'ZRX']
    # [1.0008875839537665, 'USDT', 'BTC', 'ZRX']
    # [1.0009861428462472, 'USDT', 'BTC', 'ZRX']
    # [1.0010145154402534, 'USDT', 'ETH', 'IOST']
    # [1.0007765268972388, 'USDT', 'BTC', 'ATOM']
    # [1.0005169742932178, 'USDT', 'ETH', 'IOST']
    # [1.0006352476658267, 'USDT', 'BTC', 'IOTA']
    # [1.0011704518492186, 'USDC', 'BTC', 'ATOM']
    # [1.0006727117213874, 'USDC', 'BTC', 'ATOM']
    # [1.00118853900948, 'USDC', 'BTC', 'ATOM']
    # [1.000769341431225, 'USDT', 'ETH', 'ONT']
    # [1.0006393198693, 'USDT', 'BTC', 'XLM']
    # [1.0006929173019241, 'USDT', 'BTC', 'QTUM']
    # [1.0005239487819657, 'PAX', 'BTC', 'ADA']
    # [1.0013979742416386, 'USDT', 'BTC', 'MITH']
    # [1.0005222189053224, 'USDT', 'BTC', 'DASH']
    # [1.0005364725113954, 'USDT', 'BTC', 'DASH']
    # [1.0006081888996783, 'USDT', 'BTC', 'FET']
    # [1.0005628329121057, 'USDT', 'BTC', 'IOTA']
    # [1.0007372824197183, 'USDC', 'BTC', 'ATOM']
    # [1.0014620263486294, 'USDC', 'BTC', 'ATOM']
    # [1.0022620607085548, 'USDC', 'BTC', 'ATOM']
    # [1.0014014497070298, 'USDC', 'BTC', 'ATOM']