import sys
import logging
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
import pandas as pd
import boto3

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

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

# Lab 41 - Clean PII Data
start=datetime.now()
s3 = boto3.client("s3") 

sourceBucketName = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
sourceFileName="synthetic-pii.csv"
obj = s3.get_object(Bucket=sourceBucketName, Key=sourceFileName) 
df = pd.read_csv(obj["Body"], index_col="cpr")
logger.info(df)

# Get a few sample IDs to delete as files are auto generated and synthetic
# https://www.shanelynn.ie/pandas-drop-delete-dataframe-rows-columns/
guidA=df.iloc[2]
guidB=df.iloc[125000]
guidC=df.iloc[500000]
logger.info("Random CPR to delete ["+str(guidA.name)+"]")
logger.info("Random CPR to delete ["+str(guidB.name)+"]")
logger.info("Random CPR to delete ["+str(guidC.name)+"]")
logger.info("Items before deletion="+str(df.index.size))

# Delete rows. Parameter is the index value for the index column specified above
df = df.drop(str(guidA.name))
df = df.drop(str(guidB.name))
df = df.drop(str(guidC.name))
logger.info("Items after deletion="+str(df.index.size))

# Write cleaned file to s3
targetBucket = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
targetPath="s3://"+targetBucket+"/synthetic-pii-cleaned.csv"
df.to_csv(targetPath,encoding="UTF-8")

end=datetime.now()
logger.info("actual duration was ["+str(end-start)+"].")
job.commit()