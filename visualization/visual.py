from getData import *
import pandas as pd
from plotly.graph_objs import Scatter,Candlestick,Figure,Layout
import numpy as np
from analyzerFunctions import *
import plotly

def visual():
    data = pd.read_csv('log_data/NEO_270619_01_25_04.csv')

    data['Date'] = pd.to_datetime(data['Date'])

    # startDate = data.iloc[0].Date
    # endDate = data.iloc[-1].Date
    #
    #
    # start = int(datetime.timestamp(startDate)) * 1000 + (8*60*60*1000)
    # end = int(datetime.timestamp(endDate)) * 1000 + (8*60*60*1000)
    #
    # # end = '1561702500000'
    #
    # getData('NEOUSDT',Client.KLINE_INTERVAL_15MINUTE,start=start,end=end)
    # exit()

    klines = pd.read_csv('260619_to_280619_analysis/NEOUSDT_15m.csv')



    buys={}
    buys['date'] = []
    buys['price'] = []
    buys['target'] = []
    buys['exit'] = []
    sells = {}
    sells['date'] = []
    sells['price'] = []
    prices={}
    prices['date'] = []
    prices['price'] = []
    for i,r in data.iterrows():

        prices['date'].append(r['Date'])
        prices['price'].append(r['Current Price'])

        if not pd.isna(r['Open Phase Exited']):
            buys['date'].append(r['Date'])
            buys['price'].append(r['Buy Price'])
            buys['target'].append(data.iloc[i+1]['Target'])
            buys['exit'].append(data.iloc[i + 1]['Drop Threshold'])

        if not pd.isna(r['Mini Sell Price']):
            sells['date'].append(r['Date'])
            sells['price'].append(r['Mini Sell Price'])

    a = Candlestick(x=klines.DateTime,open=klines.open,high=klines.high,low=klines.low,close=klines.close)

    bolliDate = []
    bolliLow = []

    for i,r in klines.iterrows():
        if i<8: continue

        bolliDate.append(r.DateTime)
        bolliLow.append(bollingerLow(klines.iloc[i-5:i].close))

    bolliData = Scatter(name='Bolli',x=bolliDate,y=bolliLow,marker=dict(color='navy',size=4))
    priceData = Scatter(name='Current Price', x=prices['date'],mode='lines', y=prices['price'], marker=dict(color='grey', size=10,symbol='star'))
    targetData =Scatter(name='target',x=buys['date'],y=buys['target'],mode='markers',marker=dict(symbol='triangle-up',color='blue',size=4))
    # miniTargetData = Scatter(name='miniTarget',x=miniTargetDate,y=miniTargetList,mode='markers',marker=dict(symbol='triangle-up',color='pink',size=3))
    #
    buyData = Scatter(name= 'Buy',mode='markers', marker=dict(symbol = 'circle-open-dot',color='royalblue', size=14), x=buys['date'], y=buys['price'])
    sellData = Scatter(name='Sell',mode='markers', marker=dict(symbol='star',color = 'black', size=14), x=sells['date'], y=sells['price'])
    # miniSellData = Scatter(name='miniSell',mode='markers', marker=dict(symbol='circle-open-dot',color='darkgreen', size=10), x=miniSellDate, y=miniSellPrice)
    #
    # buyStopData = Scatter(name='buyStop',mode='markers', marker=dict(symbol='diamond',color='black', size=7), x=buyOrderDate, y=buyOrderStop)
    # buyLimitData = Scatter(name='buyLimit',mode='markers', marker=dict(symbol='diamond-open',color='black', size=7), x=buyOrderDate, y=buyOrderLimit)
    #
    exitData = Scatter(name='exit',mode='markers', marker=dict(symbol='diamond',color='orange', size=7), x=buys['date'], y=buys['exit'])
    # sellLimitData = Scatter(name='sellLimit',mode='markers', marker=dict(symbol='diamond-open',color='orange', size=7), x=sellOrderDate,
    #                         y=sellOrderLimit)
    #
    # miniSellStopData = Scatter(name='miniSellStop',mode='markers', marker=dict(symbol='diamond',color='red', size=7), x=miniSellOrderDate,
    #                            y=miniSellOrderStop)
    # miniSellLimitData = Scatter(name='miniSellLimit',mode='markers', marker=dict(symbol='diamond-open',color='red', size=7), x=miniSellOrderDate,
    #                             y=miniSellOrderLimit)
    #
    # cancelData = Scatter(name='cancel',mode='markers', marker=dict(color='grey', size=7,symbol='cross'), x=cancelDate, y=cancelPrice)
    #
    majorFig = Figure(
        data=[a,
              priceData,
              bolliData,
        targetData,
        buyData,
              exitData,
              sellData
    ],
        layout=Layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=False
                ),
                showgrid=True,
            )))

    print('printing graph...')
    plotly.offline.plot(majorFig,
                        # show_link=False,
                        # # output_type='div',
                        # include_plotlyjs=False,
                        # filename='charts//'+coin+'_'+str(seed)+'_'+ interval+ '_'+datetime.utcnow().strftime("%d%m%y_%H:%M:%S")+'.html',
                        auto_open=True,
                        config={'displaylogo': False,
                                'modeBarButtonsToRemove': ['sendDataToCloud', 'select2d', 'zoomIn2d',
                                                           'zoomOut2d',
                                                           'resetScale2d', 'hoverCompareCartesian',
                                                           'lasso2d'],
                                'displayModeBar': True
                                })
    # endregion





if __name__ == '__main__':

    visual()