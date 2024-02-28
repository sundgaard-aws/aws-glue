import pandas
df.write.option("header",True) \
        .partitionBy("state","city") \
        .mode("overwrite") \
        .csv("/tmp/zipcodes-state")

df.write\
    .bucketBy(16, 'key') \
    .sortBy('value') \
    .saveAsTable('bucketed', format='parquet')

df.write\
    .partitionBy("state","city") \
    .bucketBy(16, 'ccy') \
    .sortBy('value') \
    .saveAsTable('bucketed', format='parquet')

df.write\
    .partitionBy("state","city") \
    .bucketBy(16, 'ccy') \
    .saveAsTable('trades-bucketed', format='parquet')