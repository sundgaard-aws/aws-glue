import datetime

start=datetime.datetime.now()
df.write().mode("overwrite").csv("output.csv")
end=datetime.datetime.now()
duration=end-start
print("duration="+str(duration))