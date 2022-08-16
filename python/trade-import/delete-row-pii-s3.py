import pandas as pd
import boto3
from datetime import datetime
from generic_glue_functions import getParameter

print("started row deletion at ["+str(datetime.now())+"]...")
s3 = boto3.client("s3") 

sourceBucketName = getParameter("acc-day-glue-trade-input-bucket-name")["Parameter"]["Value"]
sourceFileName="synthetic-pii.csv"
obj = s3.get_object(Bucket=sourceBucketName, Key=sourceFileName) 
df = pd.read_csv(obj["Body"], index_col="cpr")
print(df)

# Get a few sample IDs to delete as files are auto generated and synthetic
# https://www.shanelynn.ie/pandas-drop-delete-dataframe-rows-columns/
guidA=df.iloc[2]
guidB=df.iloc[125000]
guidC=df.iloc[500000]
print("Random CPR to delete ["+str(guidA.name)+"]")
print("Random CPR to delete ["+str(guidB.name)+"]")
print("Random CPR to delete ["+str(guidC.name)+"]")
df.index.size

# Delete rows. Parameter is the index value for the index column specified above
df = df.drop(str(guidA.name))
df = df.drop(str(guidB.name))
df = df.drop(str(guidC.name))
df.index.size

# Write cleaned file to s3
targetBucket = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
targetPath="s3://"+targetBucket+"/synthetic-pii-cleaned.csv"
df.to_csv(targetPath,encoding="UTF-8")

print("completed row deletion at ["+str(datetime.now())+"].")