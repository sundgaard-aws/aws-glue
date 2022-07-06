# Generate PII to S3
import random
from datetime import datetime
import pandas as pdf
import boto3

# generate PII
now=datetime.now()
print("started data generation at ["+str(now)+"]...")
csvData="balance,ccy,bank_account_id,cpr\n"
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
    csvData+=str(balance)+","+fxCurrency+","+str(bankAccountId)+","+str(cpr)+"\n"
    i+=1

# write to s3
targetBucketName = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
client = boto3.client('s3')
client.put_object(Body=csvData, Bucket=targetBucketName, Key="synthetic-pii-from-notebook.csv")
now=datetime.now()
print("data generation ended at ["+str(now)+"].")

#job.commit()