import uuid
from pyspark.sql.functions import lit
from pyspark.sql.functions import udf

i=0
rowsToGenerate=10

while i<rowsToGenerate:
    print(lit(str(uuid.uuid4())))
    i+=1