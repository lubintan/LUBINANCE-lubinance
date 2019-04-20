from datetime import datetime

BTCUSDT = {}
BCHABCUSDT = {}
BNBUSDT = {}
EOSUSDT = {}
ETHUSDT = {}
LTCUSDT = {}
XLMUSDT = {}
ZECUSDT = {}

folder = 'datasets/'

BTCUSDT['datasets'] = [folder + 'BTCUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BTCUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BTCUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]

BTCUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BTCUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BTCUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BTCUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BTCUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BTCUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BTCUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BTCUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)

BCHABCUSDT['datasets'] = [folder + 'BCHABCUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BCHABCUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BCHABCUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
BCHABCUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BCHABCUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BCHABCUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BCHABCUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BCHABCUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BCHABCUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BCHABCUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BCHABCUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)


EOSUSDT['datasets'] = [folder + 'EOSUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'EOSUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'EOSUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
EOSUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
EOSUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
EOSUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
EOSUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
EOSUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
EOSUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
EOSUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
EOSUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)


BNBUSDT['datasets'] = [folder + 'BNBUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BNBUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'BNBUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
BNBUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BNBUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BNBUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BNBUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
BNBUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BNBUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BNBUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
BNBUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)


ETHUSDT['datasets'] = [folder + 'ETHUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ETHUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ETHUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
ETHUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ETHUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ETHUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ETHUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ETHUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
ETHUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
ETHUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
ETHUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)


XLMUSDT['datasets'] = [folder + 'XLMUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'XLMUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'XLMUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
XLMUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
XLMUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
XLMUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
XLMUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
XLMUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
XLMUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
XLMUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
XLMUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)


LTCUSDT['datasets'] = [folder + 'LTCUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'LTCUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'LTCUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
LTCUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
LTCUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
LTCUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
LTCUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
LTCUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
LTCUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
LTCUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
LTCUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)


ZECUSDT['datasets'] = [folder + 'ZECUSDT_1m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ZECUSDT_5m_1 Dec, 2016-17 Apr, 2019.csv',
                         folder + 'ZECUSDT_15m_1 Dec, 2016-17 Apr, 2019.csv',
                         ]
ZECUSDT['uptrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ZECUSDT['downtrendDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ZECUSDT['sidewaysDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ZECUSDT['randomDates'] = [datetime(2000,1,1), datetime(2000,1,1)]
ZECUSDT['uptrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
ZECUSDT['downtrendResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
ZECUSDT['sidewaysResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)
ZECUSDT['randomResults'] = dict(annualRate=None, monthlyRate=None, numOfDays=None, finalBalance=None)

