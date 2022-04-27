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
def get_secret(name, version=None):
    secrets_client = boto3.client("secretsmanager")
    kwargs = {'SecretId': name}
    if version is not None:
        kwargs['VersionStage'] = version
    response = secrets_client.get_secret_value(**kwargs)
    return response
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
# end - get secret


# read from s3
logger.info("doing s3 stuff...")
inputObject="s3://aiml-input-data/car_data.csv"
logger.info("reading data from S3 bucket ["+inputObject+"]...")
DataSource0 = glueContext.create_dynamic_frame.from_options(format_options = {"quoteChar":"\"","escaper":"","withHeader":True,"separator":","}, connection_type = "s3", format = "csv", connection_options = {"paths": [inputObject], "recurse":True}, transformation_ctx = "DataSource0")
logger.info("applying mapping to S3 data...")
Transform0 = ApplyMapping.apply(frame = DataSource0, mappings = [("car", "string", "make", "string"), ("year", "long", "year", "string"), ("engine_hp", "double", "hp", "string"), ("price", "string", "price", "string")], transformation_ctx = "Transform0")
logger.info("done reading and prepping data from S3.")
# end - read from s3


# write to db
logger.info("doing db stuff...")
jdbcURL = "jdbc:" + secret['engine'] + "://" + secret['host'] + ":" + str(secret['port']) + "/" + secret['dbname']
connection_mysql8_options = {
    "url": jdbcURL,
    "dbtable": "car",
    "user": secret['username'],
    "password": secret['password'],
    "customJdbcDriverS3Path": "s3://glue-demo-s3-to-mysql/mysql-connector-java-8.0.25.jar",
    "customJdbcDriverClassName": "com.mysql.cj.jdbc.Driver"}

# Read from JDBC databases with custom driver
logger.info("creating dataframe...")
df_mysql8 = glueContext.create_dynamic_frame.from_options(connection_type="mysql", connection_options=connection_mysql8_options)
logger.info("writing data to database...")
DataSink0 = glueContext.write_dynamic_frame.from_options(frame = Transform0, connection_type="mysql", connection_options=connection_mysql8_options, transformation_ctx = "DataSink0")
logger.info("wrote data to database.")
# end - write to db


# end - main job part


logger.info("committing...")
job.commit()
logger.info("ended trade-import-s3-to-mysql job.")
