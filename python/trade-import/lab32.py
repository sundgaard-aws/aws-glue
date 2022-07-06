import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame
import logging
import boto3

# define logging
MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger("default-logger")
logger.setLevel(logging.INFO)

# Functions
def getParameter(name):
    ssmClient = boto3.client("ssm")
    response = ssmClient.get_parameter(Name=name, WithDecryption=True)    
    return response

def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    logger.info("inside MyTransform()...")
    logger.info(dfc.keys())
    dataFrame = dfc.select(list(dfc.keys())[0]).toDF()
    logger.info("found dataFrame...")
    dataFrame.show()
    dynamicFrame = DynamicFrame.fromDF(dataFrame, glueContext, "dynamicFrame")
    repartitionedDynamicFrame = dynamicFrame.repartition(10)
    logger.info("repartitioned dynamic frame.")
    return DynamicFrameCollection(
        {"repartitionedDynamicFrame": repartitionedDynamicFrame}, glueContext
    )


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Read input data
tradeInputBucket = getParameter("acc-day-glue-trade-input-bucket-name")["Parameter"]["Value"]
inputPath="s3://"+tradeInputBucket+"/fx-trades-huge.csv"
inputDataFrame = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [inputPath],
        "recurse": True,
    },
    transformation_ctx="inputDataFrame",
)

# Apply mapping
mappedFrame = ApplyMapping.apply(
    frame=inputDataFrame,
    mappings=[
        ("trade_type", "string", "trade_type", "string"),
        ("amount", "string", "amount", "decimal"),
        ("ccy", "string", "ccy", "string"),
        ("trade_date", "string", "trade_date", "string"),
        ("trader_id", "string", "trader_id", "int"),
        ("cpty_id", "string", "cpty_id", "int"),
    ],
    transformation_ctx="mappedFrame",
)

# Transform
transformedNode = MyTransform(glueContext,DynamicFrameCollection({"mappedFrame": mappedFrame}, glueContext))

# Select single data frame
dynamicFrame = SelectFromCollection.apply(
    dfc=transformedNode,
    key=list(transformedNode.keys())[0],
    transformation_ctx="dynamicFrame",
)

# Write to S3
targetBucket = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
targetPath="s3://"+targetBucket+"/huge-by-date-and-ccy/"
s3Sink = glueContext.write_dynamic_frame.from_options(
    frame=dynamicFrame,
    connection_type="s3",
    format="csv",
    connection_options={
        "path": targetPath,
        "partitionKeys": ["trade_date","ccy"],
    },
    transformation_ctx="s3Sink",
)

job.commit