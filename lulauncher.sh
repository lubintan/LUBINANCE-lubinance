#!/bin/bash
for coin in BTC LTC ETH XRP EOS ONE MATIC ATOM NEO ZIL LINK XLM QTUM DASH ZEC NANO BNB BTT TRX IOTA
do
    echo $coin
    gnome-terminal  --command "python /home/lubin/Desktop/lubinance/lubinance3B.py ${coin}" &
    sleep 15
done