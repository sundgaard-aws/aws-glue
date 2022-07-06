import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import random
from datetime import datetime
import logging
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

# actual processing
start=datetime.now()

# loop folders
s3Client = boto3.client('s3')
sourceBucketName = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
paginator = s3Client.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=sourceBucketName, Prefix="huge-by-ccy/",Delimiter="/")

for page in pages:
    for prefix in page["CommonPrefixes"]:
        mergedContents=""
        folderPrefix=prefix["Prefix"]
        objectPaginator = s3Client.get_paginator('list_objects_v2')
        objectPages = objectPaginator.paginate(Bucket=sourceBucketName, Prefix=folderPrefix)
        for objectPage in objectPages:
            for obj in objectPage['Contents']:
                key=obj["Key"]
                print(key)
                s3Obj=s3Client.get_object(Bucket=sourceBucketName, Key=key)
                s3Contents=s3Obj["Body"].read().decode('utf-8')
                mergedContents=mergedContents+str(s3Contents)+"\n"
        # write to s3
        targetBucketName = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
        client = boto3.client('s3')
        client.put_object(Body=mergedContents, Bucket=targetBucketName, Key=folderPrefix+"merged.csv")

end=datetime.now()
print("actual duration was ["+str(end-start)+"].")

job.commit()