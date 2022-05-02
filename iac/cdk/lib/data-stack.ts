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
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';

export class DataStack extends Stack {
    private glueExecutionRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, rdsMySQLSecurityGroup: ISecurityGroup, glueExecutionRole: IRole, props?: StackProps) {
        super(scope, id, props);
        this.glueExecutionRole = glueExecutionRole;
        this.createInputBucket(glueExecutionRole);
        this.createGlueDriverBucket(glueExecutionRole);
        this.createDynamoDBTradeTable();
        this.createRDSMySQLDB(vpc, rdsMySQLSecurityGroup, this.glueExecutionRole);
        //this.createRDSSecret();
    }
    
    private createGlueDriverBucket(glueExecutionRole: IRole) {
        var name = MetaData.PREFIX+"driver-bucket";
        var bucket = new Bucket(this, name, {
            bucketName:name,
            blockPublicAccess:BlockPublicAccess.BLOCK_ALL,
            encryption: BucketEncryption.S3_MANAGED
        });
        Tags.of(bucket).add(MetaData.NAME, name);
        bucket.grantRead(glueExecutionRole);
        var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"driver-bucket-name", bucket.bucketName, ParameterType.STRING);
        stringParam.grantRead(glueExecutionRole);
    }

    private createInputBucket(glueExecutionRole: IRole) {
        var name = MetaData.PREFIX+"trade-input-bucket";
        var bucket = new Bucket(this, name, {
            bucketName:name,
            blockPublicAccess:BlockPublicAccess.BLOCK_ALL,
            encryption: BucketEncryption.S3_MANAGED
        });
        Tags.of(bucket).add(MetaData.NAME, name);
        bucket.grantRead(glueExecutionRole);
        var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"trade-input-bucket-name", bucket.bucketName, ParameterType.STRING);
        stringParam.grantRead(glueExecutionRole);
    }     
    
    private createRDSMySQLDB(vpc:IVpc, rdsMySQLSecurityGroup: ISecurityGroup, glueExecutionRole: IRole) {
        var name = MetaData.PREFIX+"trade-mart-rds";
        var dbInstance = new DatabaseInstance(this, name, {
            engine: DatabaseInstanceEngine.MYSQL,
            vpc: vpc,
            //vpcSubnets: vpc.selectSubnets(),
            databaseName: "tradedb",
            instanceType: InstanceType.of(InstanceClass.T4G, InstanceSize.MICRO),
            securityGroups: [rdsMySQLSecurityGroup]
        });
        Tags.of(dbInstance).add(MetaData.NAME, name);
        if(dbInstance.secret) {
            var stringParam = new SSMHelper().createSSMParameter(this, MetaData.PREFIX+"trade-mart-secret-name", dbInstance.secret.secretName, ParameterType.STRING);
            stringParam.grantRead(glueExecutionRole);
        }
    }

    private createDynamoDBTradeTable() {
        var name = MetaData.PREFIX+"trades";
        new Table(this, name, {
            tableName: name,
            billingMode: BillingMode.PAY_PER_REQUEST,
            partitionKey: {name: "trade_id", type: AttributeType.STRING}
            ,removalPolicy: RemovalPolicy.DESTROY
        });
    }   

    private createRDSSecret() {
        var name = MetaData.PREFIX+"rds-secret";
        new Secret(this, name, {
            secretName: name,
            description: name
        });
    }
}