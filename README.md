# aws-glue

# prerequisite
Login to event engine
Login to AWS
Start cloud console
git clone https://github.com/sundgaard-aws/aws-glue.git
cd aws-glue/iac/cdk
yum install typescript
sudo npm install -g aws-cdk@latest

Create security group for job
Open inbound ports for all TCP on that SG
Create NAT GW or VPCE as IGW won't work (https://aws.amazon.com/premiumsupport/knowledge-center/glue-test-connection-failed/)
- Public route table
- Public subnet (with IGW and NAT)
- Private route table
- Private subnet with NAT route in route table and use this for connection VPC
AWS Glue scripts and IAC templates to get started easy
- Create MySQL RDS database
- Create secret
- Create db security group
- Allow glue sg to db sg
- Create table "trade"
- Create S3 bucket

# data mesh
data-mesh-red-lake-crawler
data-mesh-red-lake-glue-service-role
data-mesh-shared-catalog
classifier: $[*]

# CDK
https://docs.aws.amazon.com/cdk/api/v2/docs/aws-glue-alpha-readme.html

# Python
https://www.w3schools.com/python/gloss_python_string_concatenation.asp
https://www.mkrgeo-blog.com/installing-python-package-in-visual-studio-code/
https://www.datacamp.com/community/tutorials/reading-writing-files-python

# MySQL
mysql -h trade-mart.cb3aiosvufiu.eu-west-1.rds.amazonaws.com -u user1 -pXXX tradedb

# DynamoDB
https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-connect.html#aws-glue-programming-etl-connect-dynamodb
https://aws.amazon.com/premiumsupport/knowledge-center/glue-dynamodb-etl-optimization/