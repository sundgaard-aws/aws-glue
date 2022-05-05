import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node mysql (trade2)
mysqltrade2_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="mysql-glue-db",
    table_name="mysql_tradedb_trade2",
    transformation_ctx="mysqltrade2_node1",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=mysqltrade2_node1,
    mappings=[
        ("trade_id", "int", "trade_id", "string"),
        ("trade_amount", "decimal", "trade_amount", "long"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Script generated for node mysql (trade3)
mysqltrade3_node1651684303690 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database="mysql-glue-db",
    table_name="mysql_tradedb_trade3",
    transformation_ctx="mysqltrade3_node1651684303690",
)

job.commit()
