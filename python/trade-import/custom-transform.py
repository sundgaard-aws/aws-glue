def MyTransform (glueContext, dfc) -> DynamicFrameCollection:
    from pyspark.sql.functions import trim
    from pyspark.sql.functions import to_timestamp
    from pyspark.sql.functions import expr
    import uuid

    print("inside MyTransform()...")
    print(dfc)
    print("printing dfc keys...")
    print(dfc.keys())
    dataFrame = dfc.select(list(dfc.keys())[0]).toDF()
    print("found dataFrame...")
    dataFrame.show()
    #dataFrame=dfc[0].toDF()
    trimmedDataFrame = dataFrame.withColumn('amount', trim(dataFrame.amount)).withColumn('ccy', trim(dataFrame.ccy)).withColumn('trade_date', to_timestamp(trim(dataFrame.trade_date), 'dd-MM-yyyy')).withColumn('trader_id', trim(dataFrame.trader_id))
    print("trimmed data frame...")
    #trimmedDataFrame.toDF().show()
    trimmedDataFrame.show()
    print("adding trade_id column with uuid values...")
    trimmedDataFrame = trimmedDataFrame.withColumn('trade_id', expr("uuid()"))
    trimmedDataFrame.show()
    trimmedDynamicFrame = DynamicFrame.fromDF(trimmedDataFrame, glueContext, "trimmedDynamicFrame")
    print("logging trimmed dynamic frame as json...")
    trimmedDynamicFrame.show()
    print("done trimming data frame.")
    return(DynamicFrameCollection({"trimmedDynamicFrame": trimmedDynamicFrame}, glueContext))
    