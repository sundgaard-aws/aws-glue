import { Duration, RemovalPolicy, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { Table, BillingMode, AttributeType } from 'aws-cdk-lib/aws-dynamodb';
import { InstanceClass, InstanceSize, InstanceType, ISecurityGroup, IVpc, PrivateSubnet, SecurityGroup, SubnetFilter, SubnetType } from 'aws-cdk-lib/aws-ec2';
import { IRole, PrincipalWithConditions } from 'aws-cdk-lib/aws-iam';
import { EngineVersion } from 'aws-cdk-lib/aws-opensearchservice';
import { AuroraCapacityUnit, AuroraPostgresEngineVersion, DatabaseCluster, DatabaseClusterEngine, DatabaseInstance, DatabaseInstanceEngine, PostgresEngineVersion, ServerlessCluster } from 'aws-cdk-lib/aws-rds';
import { BlockPublicAccess, Bucket, BucketEncryption } from 'aws-cdk-lib/aws-s3';
import { Secret } from 'aws-cdk-lib/aws-secretsmanager';
import { ParameterType } from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { randomUUID } from 'crypto';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { GetCallerIdentityCommand, STSClient } from "@aws-sdk/client-sts";
import { Md5 } from 'ts-md5';
import { DeleteBucketCommand, paginateListObjectsV2, S3Client, S3ClientConfig } from "@aws-sdk/client-s3";
import { json } from 'stream/consumers';
import { stringify } from 'querystring';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';

export class DataStack extends Stack {
    private glueExecutionRole:IRole;
    private cleanupFirst:boolean

    constructor(scope: Construct, id: string, vpc: IVpc, rdsMySQLSecurityGroup: ISecurityGroup, auroraPostgreSqlSecurityGroup: ISecurityGroup, glueExecutionRole: IRole, recreateS3Buckets: Boolean, region:string, props?: StackProps) {
        super(scope, id, props);
        this.glueExecutionRole = glueExecutionRole;
        const _this = this;
        if(recreateS3Buckets) {
            this.getUserHash(region).then(function(userHash){            
                _this.removeBucketsAsync(userHash).then( function() { 
                });                 
            });
        }
        this.getUserHash(region).then(function(userHash){            
            _this.createInputBucket(glueExecutionRole, userHash);
            _this.createGlueDriverBucket(glueExecutionRole, userHash);
            _this.createDataMeshTradeBucket(glueExecutionRole, userHash);
        });
        this.createDynamoDBTradeTable(glueExecutionRole);
        this.createRDSMySQLDB(vpc, rdsMySQLSecurityGroup, this.glueExecutionRole);
        this.createRDSAuroraPostgreSqlDB(vpc, auroraPostgreSqlSecurityGroup, this.glueExecutionRole);
    }
    
    private createGlueDriverBucket(glueExecutionRole: IRole, userHash:string) {
        var id = MetaData.PREFIX+"driver-bucket";
        var name = MetaData.PREFIX+"drivers-"+userHash; // max 63 chars
        var bucket = new Bucket(this, id, {
            bucketName:name,
            blockPublicAccess:BlockPublicAccess.BLOCK_ALL,
            encryption: BucketEncryption.S3_MANAGED
        });
        Tags.of(bucket).add(MetaData.NAME, id);
        bucket.grantRead(glueExecutionRole);
        var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"driver-bucket-name", bucket.bucketName, ParameterType.STRING);
        stringParam.grantRead(glueExecutionRole);
    }

    private createInputBucket(glueExecutionRole: IRole, userHash:string) {            
        var id = MetaData.PREFIX+"trade-input-bucket";
        var name = MetaData.PREFIX+"input-"+userHash; // max 63 chars
        console.log("creating trade input bucket ["+name+"]...");
        var bucket = new Bucket(this, id, {
            bucketName:name,
            blockPublicAccess:BlockPublicAccess.BLOCK_ALL,
            encryption: BucketEncryption.S3_MANAGED
        });
        Tags.of(bucket).add(MetaData.NAME, id);
        bucket.grantRead(glueExecutionRole);
        var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"trade-input-bucket-name", bucket.bucketName, ParameterType.STRING);
        stringParam.grantRead(glueExecutionRole);
        console.log("Bucket ["+name+"] created.");
    }

    private createDataMeshTradeBucket(glueExecutionRole: IRole, userHash:string) {            
        var id = MetaData.PREFIX+"trade-s3";
        var name = id+"-"+userHash; // max 63 chars
        console.log("creating trade bucket ["+name+"]...");
        var bucket = new Bucket(this, id, {
            bucketName:name,
            blockPublicAccess:BlockPublicAccess.BLOCK_ALL,
            encryption: BucketEncryption.S3_MANAGED
        });
        Tags.of(bucket).add(MetaData.NAME, id);
        bucket.grantReadWrite(glueExecutionRole);
        //bucket.grantWrite(glueExecutionRole);
        //bucket.grantPut(glueExecutionRole);
        //bucket.grantPutAcl(glueExecutionRole);
        var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"trade-bucket-name", bucket.bucketName, ParameterType.STRING);
        stringParam.grantRead(glueExecutionRole);
        console.log("Bucket ["+name+"] created.");
    }    
    
    private async getUserHash(region:string): Promise<string> {
        const client = new STSClient({region:region});
        const command = new GetCallerIdentityCommand({});
        var response = await client.send(command);
        if(response.UserId) { 
            console.log("userId=["+response.UserId+"]");
            var hash = Md5.hashStr(response.UserId);
            console.log("hashed userId=["+hash+"]");
            return hash;
        }
        else return "";
    }    
    
    private createRDSMySQLDB(vpc:IVpc, rdsMySQLSecurityGroup: ISecurityGroup, glueExecutionRole: IRole) {
        var name = MetaData.PREFIX+"trade-mart-rds";
        var dbInstance = new DatabaseInstance(this, name, {
            engine: DatabaseInstanceEngine.MYSQL,
            vpc: vpc,
            //vpcSubnets: vpc.selectSubnets(),
            databaseName: "tradedb",
            instanceIdentifier: name,
            instanceType: InstanceType.of(InstanceClass.T4G, InstanceSize.MICRO),
            securityGroups: [rdsMySQLSecurityGroup]
        });
        Tags.of(dbInstance).add(MetaData.NAME, name);
        if(dbInstance.secret) {
            var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"trade-mart-secret-name", dbInstance.secret.secretName, ParameterType.STRING);
            stringParam.grantRead(glueExecutionRole);
        }
    }

    private createRDSAuroraPostgreSqlDB(vpc:IVpc, auroraPostgreSqlSecurityGroup: ISecurityGroup, glueExecutionRole: IRole) {
        var name = MetaData.PREFIX+"tm-aurora";
        var dbInstance = new ServerlessCluster(this, name, {
            engine:  DatabaseClusterEngine.auroraPostgres({ version: AuroraPostgresEngineVersion.VER_10_13 }),
            defaultDatabaseName: "tm_aurora_db",
            backupRetention: Duration.days(1),
            clusterIdentifier: MetaData.PREFIX+"tm-aurora-cluster",
            vpc: vpc,
            //vpcSubnets: vpc.selectSubnets(),
            deletionProtection: false,
            scaling: { minCapacity:AuroraCapacityUnit.ACU_2, maxCapacity:AuroraCapacityUnit.ACU_384, autoPause: Duration.minutes(5) },
            securityGroups: [auroraPostgreSqlSecurityGroup],
            
            //parameterGroup: {}
        });
        Tags.of(dbInstance).add(MetaData.NAME, name);
        if(dbInstance.secret) {
            var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"tm-aurora-secret-name", dbInstance.secret.secretName, ParameterType.STRING);
            stringParam.grantRead(glueExecutionRole);
        }
    }  
    
    /*private createRDSAuroraPostgreSqlDB_OLD(vpc:IVpc, auroraPostgreSqlSecurityGroup: ISecurityGroup, glueExecutionRole: IRole) {
        var name = MetaData.PREFIX+"tm-aurora";
        var dbInstance = new DatabaseCluster(this, name, {
            engine:  DatabaseClusterEngine.auroraPostgres({ version: AuroraPostgresEngineVersion.VER_13_6 }),
            defaultDatabaseName: "tm-aurora-db",
            //backupRetention: Duration.days(1),
            clusterIdentifier: MetaData.PREFIX+"tm-aurora-cluster",
            //vpc: vpc,
            //vpcSubnets: vpc.selectSubnets(),
            deletionProtection: false,
            //scaling: { minCapacity:1, maxCapacity:128, autoPause: Duration.minutes(5) },
            //securityGroups: [auroraPostgreSqlSecurityGroup]
            //parameterGroup: {}
        });
        Tags.of(dbInstance).add(MetaData.NAME, name);
        if(dbInstance.secret) {
            var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"tm-aurora-secret-name", dbInstance.secret.secretName, ParameterType.STRING);
            stringParam.grantRead(glueExecutionRole);
        }
    }*/      

    private createDynamoDBTradeTable(glueExecutionRole:IRole) {
        var name = MetaData.PREFIX+"trades";
        var dynamoDBTable = new Table(this, name, {
            tableName: name,
            billingMode: BillingMode.PAY_PER_REQUEST,
            partitionKey: {name: "trade_id", type: AttributeType.STRING}
            ,removalPolicy: RemovalPolicy.DESTROY
        });
        dynamoDBTable.grantReadWriteData(glueExecutionRole)
    }   

    private async removeBucketsAsync(userHash:string) {
        const driverBucketName = MetaData.PREFIX+"drivers-"+userHash;
        const tradeInputBucketName = MetaData.PREFIX+"input-"+userHash; // max 63 chars
        await this.removeBucketAsync(driverBucketName);
        await this.removeBucketAsync(tradeInputBucketName);
        return new Promise(resolve => true);
    }

    private async removeBucketAsync(bucketName:string) {
        console.log("Removing bucket ["+bucketName+"]...")
        const s3Config: S3ClientConfig = { region: "eu-west-1" };
        const s3Client = new S3Client(s3Config);        
        const command = new DeleteBucketCommand({ Bucket: bucketName });
        try {
            const response = await s3Client.send(command);
            console.log("responseCode=["+response.$metadata.httpStatusCode+"]");
        }
        catch(ex) {
            const bucketDoesNotExistsStr="The specified bucket does not exist";
            var exStr=(ex as String);
            if(!exStr.toString().includes(bucketDoesNotExistsStr)) console.log(exStr);
            else console.log(bucketDoesNotExistsStr);
        }
        finally { console.log("Bucket removed.") }        
    }

    private createRDSSecret() {
        var name = MetaData.PREFIX+"rds-secret";
        new Secret(this, name, {
            secretName: name,
            description: name
        });
    }
}