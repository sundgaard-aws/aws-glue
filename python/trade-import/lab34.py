import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame

# Script generated for node Custom transform
def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    from pyspark.sql.functions import trim
    from pyspark.sql.functions import to_timestamp
    from pyspark.sql.functions import expr
    import uuid

    print("inside MyTransform()...")
    print(dfc)
    print("printing dfc keys...")
    print(dfc.keys())
    dataFrame = dfc.select(list(dfc.keys())[0]).toDF()
    dataFrame.show()
    trimmedDataFrame = (
        dataFrame.withColumn("amount", trim(dataFrame.amount))
        .withColumn("ccy", trim(dataFrame.ccy))
        .withColumn(
            "trade_date", to_timestamp(trim(dataFrame.trade_date), "dd-MM-yyyy")
        )
        .withColumn("trader_id", trim(dataFrame.trader_id))
    )
    print("trimmed data frame...")
    trimmedDataFrame.show()
    trimmedDynamicFrame = DynamicFrame.fromDF(
        trimmedDataFrame, glueContext, "trimmedDynamicFrame"
    )
    print("logging trimmed dynamic frame as json...")
    trimmedDynamicFrame.show()
    print("done trimming data frame.")
    return DynamicFrameCollection(
        {"trimmedDynamicFrame": trimmedDynamicFrame}, glueContext
    )


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": '"', "withHeader": True, "separator": ","},
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [
            "s3://acc-day-glue-input-040203c1fbb36de893c8289269875383/fx-trades-large.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="S3bucket_node1",
)

# Script generated for node Custom transform
Customtransform_node1657130673409 = MyTransform(
    glueContext, DynamicFrameCollection({"S3bucket_node1": S3bucket_node1}, glueContext)
)

# Script generated for node Select From Collection
SelectFromCollection_node1657130722984 = SelectFromCollection.apply(
    dfc=Customtransform_node1657130673409,
    key=list(Customtransform_node1657130673409.keys())[0],
    transformation_ctx="SelectFromCollection_node1657130722984",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=SelectFromCollection_node1657130722984,
    mappings=[
        ("trade_type", "string", "trade_type", "string"),
        ("amount", "decimal", "trade_amount", "decimal"),
        ("ccy", "string", "trade_ccy", "string"),
        ("trade_date", "timestamp", "trade_date", "timestamp"),
        ("trader_id", "string", "trader_id", "int"),
        ("cpty_id", "string", "counterparty_id", "int"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Script generated for node Aurora PostgreSQL
AuroraPostgreSQL_node3 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database="all-dbs",
    table_name="tm_aurora_tm_aurora_db_public_trade",
    transformation_ctx="AuroraPostgreSQL_node3",
)

job.commit()
