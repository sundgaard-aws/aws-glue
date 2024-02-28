import sys
import random
import datetime
import uuid
import pandas as pd
import numpy as np

now=datetime.datetime.now()
print("started data enhancements at ["+str(now)+"]...")

df = pd.read_csv('../../sample-data/generic/dj-delta-micro-example.csv', sep=',', quotechar='"', dtype=str, keep_default_na=True, header=None, encoding="utf-8")
dfEnhanced=df.fillna(method='ffill')
print(dfEnhanced)
dfEnhanced.to_csv("../../sample-data/generic/enhanced-dj-file.csv", encoding="utf-8") 
now=datetime.datetime.now()
print("data enhancements ended at ["+str(now)+"].")