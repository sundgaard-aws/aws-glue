import sys
import random
import datetime

now=datetime.datetime.now()
print("started data generation at ["+str(now)+"]...")
piiFile=open("../../sample-data/pii/synthetic-pii.csv",mode="w",encoding="utf-8")
piiFile.write("balance,ccy,bank_account_id,cpr\n")
i=0
rowsToGenerate=1000000
random.seed()
while i<rowsToGenerate:
    balance=(round(random.random()*1000000))
    fxCurrencies=['EUR','DKK','GBP','USD']
    fxIndex=(round(random.random()*3))
    fxCurrency=fxCurrencies[fxIndex]
    day=(round(random.random()*30))
    month=(round(random.random()*12))
    year=(round(random.random()*80)+10)
    lastFourDigits=(round(random.random()*9999))
    cpr=str(day).zfill(2)+"-"+str(month).zfill(2)+"-"+str(year).zfill(2)+"-"+str(lastFourDigits).zfill(4)
    bankAccountId=(round(random.random()*10000))
    piiFile.write(str(balance)+","+fxCurrency+","+str(bankAccountId)+","+str(cpr)+"\n")
    i+=1

piiFile.close()

now=datetime.datetime.now()
print("data generation ended at ["+str(now)+"].")