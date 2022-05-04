import sys
import boto3
import logging
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from botocore.exceptions import ClientError
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame
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

def writeToRDSMySQL(transformedFrame):
    logger.info("loading data to target data store...")
    glueDriverBucketName = getParameter("acc-day-glue-driver-bucket-name")["Parameter"]["Value"]
    jdbcURL = "jdbc:" + secret['engine'] + "://" + secret['host'] + ":" + str(secret['port']) + "/" + secret['dbname']
    connection_mysql8_options = {
    "url": jdbcURL,
    "dbtable": "trade",
    "user": secret['username'],
    "password": secret['password'],
    "customJdbcDriverS3Path": "s3://"+glueDriverBucketName+"/mysql-connector-java-8.0.25.jar",
    "customJdbcDriverClassName": "com.mysql.cj.jdbc.Driver"}
    logger.info("writing data to database...")
    sinkFrame = glueContext.write_dynamic_frame.from_options(frame = transformedFrame, connection_type="mysql", connection_options=connection_mysql8_options, transformation_ctx = "sinkFrame")
    logger.info("done loading data to target data store.")
# end - functions

# start job
logger.info("starting lab8...")
## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
logger.info("creating spark context...")
sc = SparkContext()
logger.info("creating glue context...")
glueContext = GlueContext(sc)
logger.info("creating spark session...")
spark = glueContext.spark_session
logger.info("creating job...")
job = Job(glueContext)
logger.info("initiating job...")
job.init(args['JOB_NAME'], args)

# main job part

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


# read from s3
logger.info("reading data from s3 to a dynamic frame...")
tradeInputBucket = getParameter("acc-day-glue-trade-input-bucket-name")["Parameter"]["Value"]
inputObject="s3://"+tradeInputBucket+"/fx-trades-large.csv"
logger.info("reading data from S3 bucket ["+inputObject+"]...")
dynamicFrame = glueContext.create_dynamic_frame.from_options(format_options = {"quoteChar":"\"","escaper":"","withHeader":True,"separator":","}, connection_type = "s3", format = "csv", connection_options = {"paths": [inputObject], "recurse":True}, transformation_ctx = "DataSource0")
#logger.info("logging dynamic frame as json...")
#dynamicFrame.show()
logger.info("done reading data from S3.")
# end - read from s3


# trim data frame
logger.info("trimming data frame...")
logger.info("logging data frame as text...")
dataFrame = dynamicFrame.toDF()
dataFrame.show()
logger.info("strip whitespaces and show data frame as text...")
trimmedDataFrame = dataFrame.withColumn('amount', trim(dataFrame.amount)).withColumn('ccy', trim(dataFrame.ccy)).withColumn('trade_date', to_timestamp(trim(dataFrame.trade_date), 'dd-MM-yyyy')).withColumn('trader_id', trim(dataFrame.trader_id))
trimmedDataFrame.show()
trimmedDynamicFrame = DynamicFrame.fromDF(trimmedDataFrame, glueContext, "trimmedDynamicFrame")
logger.info("logging trimmed dynamic frame as json...")
trimmedDynamicFrame.show()
logger.info("done trimming data frame.")
# end - trim data frame


# apply mapping rules
logger.info("applying mapping rules...")
transformedFrame = ApplyMapping.apply(frame = trimmedDynamicFrame, mappings = [
    ("trade_type", "string", "trade_type", "string")
    ,("amount", "string", "trade_amount", "decimal")
    ,("ccy", "string", "trade_ccy", "string")
    ,("trader_id", "string", "trader_id", "int")
    ,("trade_date", "timestamp", "trade_date", "timestamp")
], transformation_ctx = "transformedFrame")
logger.info("done applying mapping rules.")
# end - apply mapping rules

writeToRDSMySQL(transformedFrame)

# end - main job part


logger.info("committing...")
job.commit()
logger.info("ended lab8.")
