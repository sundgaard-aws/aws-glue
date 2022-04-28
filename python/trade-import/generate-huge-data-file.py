import sys
import random
import datetime

now=datetime.datetime.now()
print("started data generation at ["+str(now)+"]...")
largeFXTradeFile=open("../../sample-data/trade/fx-trades-huge.csv",mode="w",encoding="utf-8")
largeFXTradeFile.write("trade_type,amount,ccy,trade_date,trader_id,cpty_id\n")
i=0
rowsToGenerate=20000000
random.seed()
while i<rowsToGenerate:
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

now=datetime.datetime.now()
print("data generation ended at ["+str(now)+"].")