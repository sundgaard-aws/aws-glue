import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
  
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
print("Session init done")

tradesDyf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://aiml-input-data/trades/fx-trades-large-with-id.csv"]
    },
    transformation_ctx="tradesDynF",
)
print("Read Dynamic frame from S3")
df = tradesDyf.toDF()
df.show()

df.write\
    .partitionBy("ccy") \
    .bucketBy(5, 'guid') \
    .format("parquet") \
    .option("path","s3://aiml-output-data/trades-bucketed-new/") \
    .saveAsTable('sampledb.tradesbuck', format='parquet')
print("Save table in glue with partitioning and bucketing")