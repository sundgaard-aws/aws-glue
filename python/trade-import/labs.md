# Prerequisites
cdk deploy --all
 (200 sec) -network
 (30 sec) -security
 (616 sec) -data
 (57 sec) - compute


# lab 0
``` sh
# ensure you are using Event Engine credentials
aws sts get-caller-identity
aws s3 ls | grep input
echo please type "trade-input-bucket-name"
read tradeInputBucket
cd ~/environment/git/aws-glue/python/trade-import
python generate-large-data-file.py
python generate-huge-data-file.py
aws s3 cp ~/environment/git/aws-glue/sample-data/trade/fx-trades.json s3://$tradeInputBucket/
aws s3 cp ~/environment/git/aws-glue/sample-data/trade/fx-trades.csv s3://$tradeInputBucket/
aws s3 cp ~/environment/git/aws-glue/sample-data/trade/fx-trades-large.csv s3://$tradeInputBucket/
aws s3 cp ~/environment/git/aws-glue/sample-data/trade/fx-trades-huge.csv s3://$tradeInputBucket/
aws s3 ls | grep driver
echo please type "driver-bucket-name"
read driverBucket
cd /tmp/
wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.25/mysql-connector-java-8.0.25.jar
aws s3 cp mysql-connector-java-8.0.25.jar s3://$driverBucket/
```
- Create target table "trade" in MySQL (for performance reasons).

# lab 1
Run an "Empty" job just with context and logging. You can run it either via the console or the CLI. Try both.
``` sh
aws glue list-jobs
aws glue start-job-run --job-name acc-day-glue-lab1
aws glue get-job-runs --job-name acc-day-glue-lab1 --output table
```

# lab 2
Get secret from AWS secrets manager

# lab 3
Read CSV data from S3

# lab 4
Trim data in source data frame

# lab 5
Apply mappings

# lab 6
Write to target DB

# lab 7
Read JSON data from S3

# lab 8 - import large data set
Import large data set 1M+ rows

# lab 9 - import huge data set (SKIP or let timeout)
Import large data set 20M+ rows.
Will most likely timeout as is.
Try to modify table.
Add Cloud9 to RDS security group inbound rule.
mysql -h .rds.amazonaws.com -u xx -pXX tradedb

# lab 10 - writing to a NoSQL DB
Write data to DynamoDB instead of MySQL

# lab 11 - write large data sets to no-sql-db

# lab 12 - using multiple partitions

# lab 13 - write large data sets to no-sql-db using partioning
Run job.
Up number of glue workers to match num partitions (6).
Run job again.
Note diff if any.

# lab 14 - glue crawler for DynamoDB
Create glue crawler for DynamoDB table.
Create glue DB.
Run crawler on demand.

# lab 16 - glue crawler for MySQL
In the RDS MySQL DB
- Create counterparty table.
- Insert data into counterparty table.
- Create cpty table.
- Create crawler for RDS MySQL DB (tradedb/%)

# lab 17 - bookmarks (optional)
- Create UI job transferring data from counterparty to cpty
- Insert more data into counterparty table.
- Note that only new rows are transferred.

# lab 25 - bookmarks (optional)
- Enable and define bookmark
- Read existing data
- Verify that data is written to target
- Add more data to source
- Read data again
- Verify that only new data is read/written to target

# lab 26 - reset bookmark (optional)
- Reset bookmark
