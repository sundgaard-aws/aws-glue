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

# start job
logger.info("starting glue-demo-non-ui-sql-server-on-ec2-to-s3 job...")
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

# ****************************************
def get_secret(name, version=None):
    secrets_client = boto3.client("secretsmanager")
    kwargs = {'SecretId': name}
    if version is not None:
        kwargs['VersionStage'] = version
    response = secrets_client.get_secret_value(**kwargs)
    return response

dbSourceSecretName = "glue-demo-sql-server-on-ec2-secret"
logger.info("getting secret for source db...")
secretsManagerEntry = get_secret(dbSourceSecretName)
logger.info("here comes the SecretString...")
logger.info(secretsManagerEntry['SecretString'])
logger.info("db/username")
secretString=secretsManagerEntry['SecretString']
secret=json.loads(secretString)
logger.info(secret)
logger.info("username")
logger.info(secret['username'])

logger.info("creating dynamic frame from sql server on ec2...")
url="jdbc:sqlserver://172.31.18.220:1433;databaseName=dms-demo-db"
connectionOptions = {
    "url": url,
    "dbtable": "trade",
    "user": secret['username'],
    "password": secret['password'],
    "customJdbcDriverS3Path": "s3://glue-demo-jdbc-drivers/mssql-jdbc-10.2.0.jre11.jar"
}
# Read from JDBC databases with custom driver
tradeFrame = glueContext.create_dynamic_frame.from_options(connection_type="sqlserver", connection_options=connectionOptions)

# Script generated for node ApplyMapping
mapping = ApplyMapping.apply(
    frame=tradeFrame,
    mappings=[
        ("trade_id", "long", "trade_id", "long"),
        ("trade_type", "string", "trade_type", "string")
    ],
    transformation_ctx="ApplyMapping_node2",
)

repartitionedMapping = mapping.repartition(1)

# Script generated for node S3 bucket
S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
    frame=repartitionedMapping,
    connection_type="s3",
    format="csv",
    connection_options={"path": "s3://glue-demo-target-s3-trade-bucket/", "partitionKeys": []},
    transformation_ctx="S3bucket_node3",
)
# ************************************

logger.info("committing...")
job.commit()
logger.info("ended glue-demo-non-ui-sql-server-on-ec2-to-s3 job.")