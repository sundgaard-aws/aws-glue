import pandas as pd
import datetime
import boto3
#from io import StringIO
#import fsspec
#import s3fs

print("started row deletion at ["+str(datetime.datetime.now())+"]...")

bucket = "acc-day-glue-trade-input-bucket"
file_name = "fx-trades-large-with-id.csv"
cleanedFileName="fx-trades-large-with-id-cleaned.csv"

s3 = boto3.client("s3") 
obj = s3.get_object(Bucket=bucket, Key=file_name) 
df = pd.read_csv(obj["Body"], index_col=0)
print(df)

# Get a few sample IDs to delete as files are auto generated and synthetic
guidA=df.iloc[2]
guidB=df.iloc[125000]
guidC=df.iloc[500000]
print("Random GUID to delete ["+str(guidA.name)+"]")
print("Random GUID to delete ["+str(guidB.name)+"]")
print("Random GUID to delete ["+str(guidC.name)+"]")

# Delete rows. Parameter is the index value for the index column specified above
df = df.drop(str(guidA.name))
df = df.drop(str(guidB.name))
df = df.drop(str(guidC.name))

df.to_csv("s3://"+bucket+"/fx-trades-large-with-id-cleaned.csv",encoding="UTF-8")
#csv_buffer = StringIO()
#df.to_csv(csv_buffer)
#s3_resource = boto3.resource('s3')
#s3_resource.Object(bucket, cleanedFileName).put(Body=csv_buffer.getvalue())

print("completed row deletion at ["+str(datetime.datetime.now())+"].")