import sys
import boto3
import logging
import json
import pandas
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as SqlFuncs
from pyspark.context import SparkContext
from botocore.exceptions import ClientError
from pyspark.sql.functions import *
from datetime import datetime

# define logging
MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger("default-logger")
logger.setLevel(logging.INFO)

# functions
def getSecret(name, version=None):
    secrets_client = boto3.client("secretsmanager")
    kwargs = {'SecretId': name}
    if version is not None:
        kwargs['VersionStage'] = version
    response = secrets_client.get_secret_value(**kwargs)
    return response

def getParameter(name):
    ssmClient = boto3.client("ssm")
    response = ssmClient.get_parameter(Name=name, WithDecryption=True)    
    return response
    
def sparkAggregate(glueContext, parentFrame, groups, aggs, transformation_ctx) -> DynamicFrame:
    aggsFuncs = []
    for column, func in aggs:
        aggsFuncs.append(getattr(SqlFuncs, func)(column))
    result = (
        parentFrame.toDF().groupBy(*groups).agg(*aggsFuncs)
        if len(groups) > 0
        else parentFrame.toDF().agg(*aggsFuncs)
    )
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx) 

# Write to S3
def writeCSVToS3(dataFrame, targetS3Path):
    dataFrame=dataFrame.repartition(1)    
    logger.info("writing data to S3 bucket ["+targetS3Path+"]...")
    s3Sink = glueContext.write_dynamic_frame.from_options(
        frame=dataFrame,
        connection_type="s3",
        format="csv",
        connection_options={
            "path": targetS3Path,
            "partitionKeys": [],
        },
        transformation_ctx="s3Sink",
    )
    return s3Sink  
# end - functions
print("functions defined")

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# get secret
rdsSecretName = getParameter("acc-day-glue-trade-mart-secret-name")["Parameter"]["Value"]
logger.info("getting secret for source db with name ["+rdsSecretName+"]...")
secretsManagerEntry = getSecret(rdsSecretName)
logger.info("here comes the SecretString...")
logger.info(secretsManagerEntry['SecretString'])
logger.info("db/username")
secretString=secretsManagerEntry['SecretString']
secret=json.loads(secretString)
logger.info(secret)
logger.info("username")
logger.info(secret['username'])
# end - get secret
print("got secret")

# read from s3
start=datetime.now()
logger.info("reading data from s3 to a dynamic frame...")
tradeInputBucket = getParameter("acc-day-glue-trade-input-bucket-name")["Parameter"]["Value"]
inputObject="s3://"+tradeInputBucket+"/fx-trades-large.csv"
logger.info("reading data from S3 bucket ["+inputObject+"]...")
dynamicFrame = glueContext.create_dynamic_frame.from_options(format_options = {"quoteChar":"\"","escaper":"","withHeader":True,"separator":","}, connection_type = "s3", format = "csv", connection_options = {"paths": [inputObject], "recurse":True}, transformation_ctx = "DataSource0")
logger.info("logging dynamic frame as json...")
#dynamicFrame.show()
logger.info("done reading data from S3.")

end=datetime.now()
duration=end-start
print("duration="+str(duration))
print("read data from s3")
# end - read from s3

# trim data frame
start=datetime.now()
logger.info("trimming data frame...")
dataFrame = dynamicFrame.toDF()
#dataFrame.show()
#logger.info("strip whitespaces and show data frame as text...")
trimmedDataFrame = dataFrame.withColumn('amount', trim(dataFrame.amount)).withColumn('ccy', trim(dataFrame.ccy)).withColumn('trade_date', to_timestamp(trim(dataFrame.trade_date), 'dd-MM-yyyy')).withColumn('trader_id', trim(dataFrame.trader_id))
#trimmedDataFrame = trimmedDataFrame.withColumn('trade_id', lit(str('dummy')))
#logger.info("adding trade_id column with uuid values...")
#trimmedDataFrame = trimmedDataFrame.withColumn('trade_id', expr("uuid()"))
#trimmedDataFrame.show()
trimmedDynamicFrame = DynamicFrame.fromDF(trimmedDataFrame, glueContext, "trimmedDynamicFrame")
#logger.info("logging trimmed dynamic frame as json...")
#trimmedDynamicFrame.show()
logger.info("done trimming data frame.")
# end - trim data frame
#print("trimmed data frame")
end=datetime.now()
duration=end-start
print("duration="+str(duration))

# apply mapping rules
logger.info("applying mapping rules...")
mappedFrame = ApplyMapping.apply(frame = trimmedDynamicFrame, mappings = [
    ("trade_type", "string", "trade_type", "string")
    ,("amount", "string", "trade_amount", "decimal")
    ,("ccy", "string", "trade_ccy", "string")
    ,("trader_id", "string", "trader_id", "int")
    ,("trade_date", "timestamp", "trade_date", "timestamp")
    #,("trade_id", "string", "trade_id", "string")
], transformation_ctx = "mappedFrame")
logger.info("done applying mapping rules.")
# end - apply mapping rules
print("mapping done")

# Aggregate amounts by trader
start=datetime.now()
aggregatedAmountsByTrader=sparkAggregate(
    glueContext,
    parentFrame=mappedFrame,
    groups=["trader_id"],
    aggs=[["trade_amount", "sum"]],
    transformation_ctx="aggregatedData",
)
aggregatedAmountsByTrader.toDF().show()
end=datetime.now()
duration=end-start
print("duration="+str(duration))

# Aggregate amounts by ccy
start=datetime.now()
aggregatedAmountsByCurrency=sparkAggregate(
    glueContext,
    parentFrame=mappedFrame,
    groups=["trade_ccy"],
    aggs=[["trade_amount", "sum"]],
    transformation_ctx="aggregatedData",
)
aggregatedAmountsByCurrency.toDF().show()
end=datetime.now()
duration=end-start
print("duration="+str(duration))

tradeTargetBucket = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
targetS3PathPrefix="s3://"+tradeTargetBucket+"/reports/"
writeCSVToS3(aggregatedAmountsByTrader, targetS3PathPrefix+"aggregated-amount-by-trader")
writeCSVToS3(aggregatedAmountsByCurrency, targetS3PathPrefix+"aggregated-amount-by-ccy")

job.commit()
