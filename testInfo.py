from datetime import datetime

BTCUSDT = {}
BCHABCUSDT = {}
BNBUSDT = {}
EOSUSDT = {}
ETHUSDT = {}
LTCUSDT = {}
XLMUSDT = {}
ZECUSDT = {}

allData = [BTCUSDT,BNBUSDT,EOSUSDT,ETHUSDT,LTCUSDT,XLMUSDT,ZECUSDT]

folder = 'datasets/'

BTCUSDT['datasets'] = [folder + 'BTCUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BTCUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BTCUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]

BTCUSDT['uptrendDates'] = [datetime(2017,9,15), datetime(2017,12,18)]
BTCUSDT['downtrendDates'] = [datetime(2017,12,17), datetime(2018,2,6)]
BTCUSDT['sidewaysDates'] = [datetime(2018,12,18), datetime(2019,3,13)]
# BTCUSDT['sidewaysDates'] = [datetime(2019,1,16), datetime(2019,1,17,16)]
BTCUSDT['randomDates'] = [datetime(2018,7,26), datetime(2019,2,6)]
BTCUSDT['name'] = 'BTC/USDT'


BCHABCUSDT['datasets'] = [folder + 'BCHABCUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BCHABCUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BCHABCUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
BCHABCUSDT['uptrendDates'] = [datetime(2018,12,17), datetime(2018,12,21)]
BCHABCUSDT['downtrendDates'] = [datetime(2018,11,17), datetime(2018,12,18)]
BCHABCUSDT['sidewaysDates'] = [datetime(2019,1,9), datetime(2019,2,24)]
BCHABCUSDT['randomDates'] = [datetime(2018,11,25), datetime(2019,4,14)]
BCHABCUSDT['name'] = 'BCHABC/USDT'


BNBUSDT['datasets'] = [folder + 'BNBUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BNBUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BNBUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
BNBUSDT['uptrendDates'] = [datetime(2019,1,1), datetime(2019,4,5)]
BNBUSDT['downtrendDates'] = [datetime(2018,1,5), datetime(2018,2,7)]
BNBUSDT['sidewaysDates'] = [datetime(2018,3,1), datetime(2018,9,1)]
BNBUSDT['randomDates'] = [datetime(2018,8,1), datetime(2019,3,8)]
BNBUSDT['name'] = 'BNB/USDT'


EOSUSDT['datasets'] = [folder + 'EOSUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'EOSUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'EOSUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
EOSUSDT['uptrendDates'] = [datetime(2018,5,28), datetime(2018,6,3)]
EOSUSDT['downtrendDates'] = [datetime(2018,6,1), datetime(2018,12,11)]
EOSUSDT['sidewaysDates'] = [datetime(2018,9,1), datetime(2018,11,1)]
EOSUSDT['randomDates'] = [datetime(2018,8,10), datetime(2019,4,15)]
EOSUSDT['name'] = 'EOS/USDT'


ETHUSDT['datasets'] = [folder + 'ETHUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ETHUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ETHUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
ETHUSDT['uptrendDates'] = [datetime(2018,4,4), datetime(2018,5,7)]
ETHUSDT['downtrendDates'] = [datetime(2018,2,17), datetime(2018,4,10)]
ETHUSDT['sidewaysDates'] = [datetime(2018,1,14), datetime(2018,2,17)]
ETHUSDT['randomDates'] = [datetime(2018,7,1), datetime(2019,3,1)]
ETHUSDT['name'] = 'ETH/USDT'

LTCUSDT['datasets'] = [folder + 'LTCUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'LTCUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'LTCUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
LTCUSDT['uptrendDates'] = [datetime(2018,3,30), datetime(2018,5,10)]
LTCUSDT['downtrendDates'] = [datetime(2017,12,13), datetime(2018,12,17)]
LTCUSDT['sidewaysDates'] = [datetime(2018,11,1), datetime(2019,3,3)]
LTCUSDT['randomDates'] = [datetime(2018,3,1), datetime(2019,4,12)]
LTCUSDT['name'] = 'LTC/USDT'


XLMUSDT['datasets'] = [folder + 'XLMUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'XLMUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'XLMUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
XLMUSDT['uptrendDates'] = [datetime(2018,6,27), datetime(2018,7,27)]
XLMUSDT['downtrendDates'] = [datetime(2018,11,11), datetime(2018,12,15)]
XLMUSDT['sidewaysDates'] = [datetime(2019,1,1), datetime(2019,4,1)]
XLMUSDT['randomDates'] = [datetime(2018,9,1), datetime(2018,11,21)]
XLMUSDT['name'] = 'XLM/USDT'


ZECUSDT['datasets'] = [folder + 'ZECUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ZECUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ZECUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
ZECUSDT['uptrendDates'] = [datetime(2019,3,28), datetime(2019,4,4)]
ZECUSDT['downtrendDates'] = [datetime(2019,4,3), datetime(2019,4,5)]
ZECUSDT['sidewaysDates'] = [datetime(2019,3,24), datetime(2019,3,30)]
ZECUSDT['randomDates'] = [datetime(2019,3,21), datetime(2019,4,17)]
ZECUSDT['name'] = 'ZEC/USDT'

