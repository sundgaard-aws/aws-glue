import boto3
import uuid
from datetime import datetime
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

startTimes={}
def startStopwatch():    
    id=str(uuid.uuid4())
    startTimes[id]=datetime.now()
    return id

def stopStopwatch(uuid):
    endTime=datetime.now()
    startTime=startTimes[uuid]
    return str(endTime-startTime)
