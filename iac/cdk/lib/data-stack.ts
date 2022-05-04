import { RemovalPolicy, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { Table, BillingMode, AttributeType } from 'aws-cdk-lib/aws-dynamodb';
import { InstanceClass, InstanceSize, InstanceType, ISecurityGroup, IVpc, PrivateSubnet, SecurityGroup, SubnetFilter, SubnetType } from 'aws-cdk-lib/aws-ec2';
import { IRole } from 'aws-cdk-lib/aws-iam';
import { EngineVersion } from 'aws-cdk-lib/aws-opensearchservice';
import { DatabaseInstance, DatabaseInstanceEngine, PostgresEngineVersion } from 'aws-cdk-lib/aws-rds';
import { BlockPublicAccess, Bucket, BucketEncryption } from 'aws-cdk-lib/aws-s3';
import { Secret } from 'aws-cdk-lib/aws-secretsmanager';
import { ParameterType } from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { randomUUID } from 'crypto';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { GetCallerIdentityCommand, STSClient } from "@aws-sdk/client-sts";
import { Md5 } from 'ts-md5';

export class DataStack extends Stack {
    private glueExecutionRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, rdsMySQLSecurityGroup: ISecurityGroup, glueExecutionRole: IRole, props?: StackProps) {
        super(scope, id, props);
        this.glueExecutionRole = glueExecutionRole;
        const _this = this;
        this.getUserHash().then(function(userHash){
            _this.createInputBucket(glueExecutionRole, userHash);
            _this.createGlueDriverBucket(glueExecutionRole, userHash);
        });
        this.createDynamoDBTradeTable(glueExecutionRole);
        this.createRDSMySQLDB(vpc, rdsMySQLSecurityGroup, this.glueExecutionRole);
        //this.createRDSSecret();
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
        var bucket = new Bucket(this, id, {
            bucketName:name,
            blockPublicAccess:BlockPublicAccess.BLOCK_ALL,
            encryption: BucketEncryption.S3_MANAGED
        });
        Tags.of(bucket).add(MetaData.NAME, id);
        bucket.grantRead(glueExecutionRole);
        var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"trade-input-bucket-name", bucket.bucketName, ParameterType.STRING);
        stringParam.grantRead(glueExecutionRole);
    }
    
    private async getUserHash(): Promise<string> {
        const client = new STSClient({});
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

    private createRDSSecret() {
        var name = MetaData.PREFIX+"rds-secret";
        new Secret(this, name, {
            secretName: name,
            description: name
        });
    }
}