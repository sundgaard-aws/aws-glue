# aws-glue
Create security group for job
Open inbound ports for all TCP on that SG
Create NAT GW or VPCE as IGW won't work (https://aws.amazon.com/premiumsupport/knowledge-center/glue-test-connection-failed/)
- Public route table
- Public subnet (with IGW and NAT)
- Private route table
- Private subnet with NAT route in route table and use this for connection VPC
AWS Glue scripts and IAC templates to get started easy

# data mesh
data-mesh-red-lake-crawler
data-mesh-red-lake-glue-service-role
data-mesh-shared-catalog
classifier: $[*]

# CDK
https://docs.aws.amazon.com/cdk/api/v2/docs/aws-glue-alpha-readme.html

# Python
https://www.w3schools.com/python/gloss_python_string_concatenation.asp