import sys
import random
import datetime
import uuid
import pandas as pd
import numpy as np

now=datetime.datetime.now()
print("started data enhancements at ["+str(now)+"]...")

df = pd.read_csv('../../sample-data/generic/dj-delta-micro-example.csv', sep=',', quotechar='"', dtype=str, keep_default_na=True, header=None, encoding="utf-8")
#df.info()  # Print the autodetected schema for verification and further tuning
#df.fillna(method='ffill', inplace=True)
#df.mask(data=='nan', None).ffill()
#df.fillna(0)
#print(df.ffill())
#print(df.fillna(method='ffill'))
dfEnhanced=df.fillna(method='ffill')
print(dfEnhanced)
#print(df.fillna(1))
#df.fillna(method='ffill', inplace = True)
#df.ffill()
#print(df.head(5))  # Print a sample of dataframe records, for verification
#print(f"records count = {df.count()}")
#df2 = df.replace(np.nan, None, regex=True)
#df2.ffill()
#df2.fillna(method='ffill', inplace = True)
#df2.fillna(0)
#print(df2.head(5))


#djMicro=open("../../sample-data/generic/dj-delta-micro-example.csv",mode="r",encoding="utf-8")
#djMicro.write("guid,trade_type,amount,ccy,trade_date,trader_id,cpty_id\n")
i=0
#rowsToGenerate=1000000
#random.seed()

#djMicro.close()
dfEnhanced.to_csv("../../sample-data/generic/enhanced-dj-file.csv", encoding="utf-8") 

now=datetime.datetime.now()
print("data enhancements ended at ["+str(now)+"].")