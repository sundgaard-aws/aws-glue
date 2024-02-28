import pandas as pd
import datetime

print("started data generation at ["+str(datetime.datetime.now())+"]...")

df = pd.read_csv('../../sample-data/trade/fx-trades-large-with-id.csv', index_col=0)
print(df)

# Get a few sample IDs to delete as files are auto generated and synthetic
#guidA=df.iloc[2,0]
guidA=df.iloc[2]
guidB=df.iloc[125000]
guidC=df.iloc[500000]
print("Random GUID to delete ["+str(guidA.name)+"]")
print("Random GUID to delete ["+str(guidB.name)+"]")a
print("Random GUID to delete ["+str(guidC.name)+"]")

# Delete rows. Parameter is the index value for the index column specified above
df = df.drop(str(guidA.name))
df = df.drop(str(guidB.name))
df = df.drop(str(guidC.name))
df.to_csv('../../sample-data/trade/fx-trades-large-with-id-cleaned.csv')

print("data generation ended at ["+str(datetime.datetime.now())+"].")