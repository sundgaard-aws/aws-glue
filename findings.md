# AWS Glue Findings
Need to use NAT, public subnets and VPCE seems not to be working
Connector trying to download from https:// instead of s3:// from private bucket with drivers in Glue V3
Glue job not part of a VPC unless you specify a dummy driver
If you specify a newer version of a SQL Server driver the compiled version of AWS Java code is not compatible
