import random
import sys

print("started data generation...")
largeFXTradeFile=open("../../sample-data/trade/fx-trades-large.csv",mode="w",encoding="utf-8")
largeFXTradeFile.write("trade_type,amount,ccy,trade_date,trader_id,cpty_id\n")
i=0
random.seed()
while i<10:
    amount=(round(random.random()*1000000))
    fxCurrencies=['EUR','DKK','GBP','USD']
    fxIndex=(round(random.random()*3))
    fxCurrency=fxCurrencies[fxIndex]
    day=(round(random.random()*30))
    month=(round(random.random()*12))
    date=str(day).zfill(2)+"-"+str(month).zfill(2)+"-2021"
    traderId=(round(random.random()*100))
    counterpartyId=(round(random.random()*800))
    largeFXTradeFile.write("FXSPOT,"+str(amount)+","+fxCurrency+","+date+","+str(traderId)+","+str(counterpartyId)+"\n")
    i+=1

largeFXTradeFile.close()

print("data generation ended.")