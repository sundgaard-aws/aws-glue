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
now=datetime.now()
print("started data generation at ["+str(now)+"]...")

# generate PII
now=datetime.now()
print("started data generation at ["+str(now)+"]...")
csvData="balance,ccy,bank_account_id,cpr\n"
i=0
rowsToGenerate=1000000
random.seed()
while i<rowsToGenerate:
    balance=(round(random.random()*1000000))
    fxCurrencies=['EUR','DKK','GBP','USD']
    fxIndex=(round(random.random()*3))
    fxCurrency=fxCurrencies[fxIndex]
    day=(round(random.random()*30))
    month=(round(random.random()*12))
    year=(round(random.random()*80)+10)
    lastFourDigits=(round(random.random()*9999))
    cpr=str(day).zfill(2)+"-"+str(month).zfill(2)+"-"+str(year).zfill(2)+"-"+str(lastFourDigits).zfill(4)
    bankAccountId=(round(random.random()*10000))
    csvData+=str(balance)+","+fxCurrency+","+str(bankAccountId)+","+str(cpr)+"\n"
    i+=1

# write to s3
targetBucketName = getParameter("acc-day-glue-trade-bucket-name")["Parameter"]["Value"]
client = boto3.client('s3')
client.put_object(Body=csvData, Bucket=targetBucketName, Key="synthetic-pii.csv")
now=datetime.now()
print("data generation ended at ["+str(now)+"].")

job.commit()