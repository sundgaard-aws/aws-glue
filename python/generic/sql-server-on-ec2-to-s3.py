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


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

def get_secret2(name, version=None):
    secrets_client = boto3.client("secretsmanager")
    kwargs = {'SecretId': name}
    if version is not None:
        kwargs['VersionStage'] = version
    response = secrets_client.get_secret_value(**kwargs)
    return response
def get_secret(secret_name):
    region_name = "eu-west-1"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception ere, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

dbSourceSecretName = "glue-demo-sql-server-on-ec2-secret"
secretsManagerEntry = get_secret2(dbSourceSecretName)
logger.info("here comes the SecretString...")
logger.info(secretsManagerEntry['SecretString'])
logger.info("db/username")
secretString=secretsManagerEntry['SecretString']
secret=json.loads(secretString)
logger.info(secret)
logger.info("username")
logger.info(secret['username'])

## @type: DataSource
## @args: [format_options = {"quoteChar":"\"","escaper":"","withHeader":True,"separator":","}, connection_type = "s3", format = "csv", connection_options = {"paths": ["s3://aiml-input-data/car_data.csv"], "recurse":True}, transformation_ctx = "DataSource0"]
## @return: DataSource0
## @inputs: []

#DataSource0 = glueContext.create_dynamic_frame.from_options(format_options = {"quoteChar":"\"","escaper":"","withHeader":True,"separator":","}, connection_type = "s3", format = "csv", connection_options = {"paths": ["s3://aiml-input-data/car_data.csv"], "recurse":True}, transformation_ctx = "DataSource0")

## @type: ApplyMapping
## @args: [mappings = [("car", "string", "make", "string"), ("year", "long", "year", "string"), ("engine_hp", "double", "hp", "string"), ("price", "long", "price", "string")], transformation_ctx = "Transform0"]
## @return: Transform0
## @inputs: [frame = DataSource0]


#Transform0 = ApplyMapping.apply(frame = DataSource0, mappings = [("car", "string", "make", "string"), ("year", "long", "year", "string"), ("engine_hp", "double", "hp", "string"), ("price", "string", "price", "string")], transformation_ctx = "Transform0")

## @type: DataSink
## @args: [connection_type = "custom.jdbc", connection_options = {"dbTable":"cars","connectionName":"glue-demo-mysql-cars-connection"}, transformation_ctx = "DataSink0"]
## @return: DataSink0
## @inputs: [frame = Transform0]



#DataSink0 = glueContext.write_dynamic_frame.from_options(frame = Transform0, connection_type = "custom.jdbc", connection_options = {"dbTable":"cars","connectionName":"glue-demo-mysql-cars-connection"}, transformation_ctx = "DataSink0")
# custom start
# glue-demo-mysql-sg
#url = "jdbc:" + secret['engine'] + "://" + secret['host'] + ":" + str(secret['port']) + "/" + secret['dbname']
url="jdbc:sqlserver://172.31.18.220:1433;databaseName=dms-demo-db"
#connectionOptionsOLD = {
#    "url": url,
#    "dbtable": "dms-demo-db",
#    "user": secret['username'],
#    "password": secret['password'],
#    "customJdbcDriverS3Path": "s3://glue-demo-jdbc-drivers/mssql-jdbc-10.2.0.jre11.jar",
#    "customJdbcDriverClassName": "com.microsoft.sqlserver.jdbc.SQLServerDriver"}

connectionOptions = {
    "url": url,
    "dbtable": "dms-demo-db",
    "user": secret['username'],
    "password": secret['password']
}

# Read from JDBC databases with custom driver
tradeFrame = glueContext.create_dynamic_frame.from_options(connection_type="sqlserver", connection_options=connectionOptions)
#DataSink0 = glueContext.write_dynamic_frame.from_options(frame = Transform0, connection_type="sqlserver", connection_options=connectionOptions, transformation_ctx = "DataSink0")

job.commit()

print("ended glue-demo-non-ui-sql-server-on-ec2-to-s3 job.")