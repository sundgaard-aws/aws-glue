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
# end - functions

# start job
logger.info("starting lab3...")
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
logger.info("logging data frame as text...")
dataFrame = dynamicFrame.toDF()
dataFrame.show()
logger.info("done reading data from S3.")
# end - read from s3


# end - main job part


logger.info("committing...")
job.commit()
logger.info("ended lab3.")
