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
logger.info("starting trade-import-s3-to-mysql job...")
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
inputObject="s3://"+tradeInputBucket+"/fx-trades.csv"
logger.info("reading data from S3 bucket ["+inputObject+"]...")
dynamicFrame = glueContext.create_dynamic_frame.from_options(format_options = {"quoteChar":"\"","escaper":"","withHeader":True,"separator":","}, connection_type = "s3", format = "csv", connection_options = {"paths": [inputObject], "recurse":True}, transformation_ctx = "DataSource0")
logger.info("logging dynamic frame as json...")
dynamicFrame.show()
logger.info("number of partitions in dynamic frame ["+str(dynamicFrame.getNumPartitions())+"]")
dynamicFrame=dynamicFrame.repartition(4)
logger.info("number of partitions in dynamic frame after repartitioning ["+str(dynamicFrame.getNumPartitions())+"]")
logger.info("done reading data from S3.")
# end - read from s3


# end - main job part


logger.info("committing...")
job.commit()
logger.info("ended trade-import-s3-to-mysql job.")
