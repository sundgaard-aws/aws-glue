import boto3

# merge files per partition
s3Client = boto3.client('s3')
samplePartitionBucketName="<bucket-name>"
paginator = s3Client.get_paginator('list_objects_v2')
bucketPrefix="<folder>"
pages = paginator.paginate(Bucket=samplePartitionBucketName, Prefix=bucketPrefix)
fullContents=""

for page in pages:
    for obj in page['Contents']:
        key=obj["Key"]
        print(key)
        s3Obj=s3Client.get_object(Bucket=samplePartitionBucketName, Key=key)
        s3Contents=s3Obj["Body"].read().decode('utf-8')
        fullContents=fullContents+str(s3Contents)+"\n"

s3Client.put_object(Body=fullContents, Bucket=samplePartitionBucketName, Key=bucketPrefix+"/merged.csv")
