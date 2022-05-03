import { Construct } from 'constructs';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { CfnSecurityGroup, InstanceType, ISecurityGroup, IVpc, SubnetType, Vpc } from 'aws-cdk-lib/aws-ec2';
import { CfnOutput, Duration, RemovalPolicy, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { CfnRole, Effect, IRole, ManagedPolicy, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { HttpMethod } from 'aws-cdk-lib/aws-events';
import {Code, Connection, ConnectionType, GlueVersion, IConnection, IJob, Job, JobExecutable, PythonVersion, WorkerType} from '@aws-cdk/aws-glue-alpha';
import {Ec2Environment} from '@aws-cdk/aws-cloud9-alpha';
import { LoggingLevel } from 'aws-cdk-lib/aws-chatbot';
import { ILogGroup, LogGroup } from 'aws-cdk-lib/aws-logs';
import { CfnEnvironmentEC2 } from 'aws-cdk-lib/aws-cloud9';

export class ComputeStack extends Stack {
    private ssmHelper = new SSMHelper();
    public glueExecutionRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, glueVPCNetworkConnectionSecurityGroup: ISecurityGroup, props?: StackProps) {
        super(scope, id, props);

        this.glueExecutionRole = this.buildGlueExecutionRole();
        var codePathRoot = "../../python/trade-import/";
        var logGroup = this.createGlueLogGroup(this.glueExecutionRole);
        var glueVPCConnection = this.createGlueVPCConn(vpc, glueVPCNetworkConnectionSecurityGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab1", codePathRoot+"lab1.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab2", codePathRoot+"lab2.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab3", codePathRoot+"lab3.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab4", codePathRoot+"lab4.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab5", codePathRoot+"lab5.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab6", codePathRoot+"lab6.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab7", codePathRoot+"lab7.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab8", codePathRoot+"lab8.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab9", codePathRoot+"lab9.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab10", codePathRoot+"lab10.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab11", codePathRoot+"lab11.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab12", codePathRoot+"lab12.py", logGroup);
        this.createSimpleETLJob(this.glueExecutionRole, glueVPCConnection, "lab13", codePathRoot+"lab13.py", logGroup);
        /*this.createSimpleETLJob(this.glueExecutionRole, "lab8", codePathRoot+"lab8.py");
        this.createSimpleETLJob(this.glueExecutionRole, "lab9", codePathRoot+"lab9.py");
        this.createSimpleETLJob(this.glueExecutionRole, "lab10", codePathRoot+"lab10.py");*/
    } 
    
    private createGlueVPCConn(vpc:IVpc,glueVPCNetworkConnectionSecurityGroup:ISecurityGroup):IConnection {
        var vpcConn = new Connection(this, MetaData.PREFIX+"vpc-conn", {
            type: ConnectionType.NETWORK,
            connectionName: MetaData.PREFIX+"vpc-conn",
            description: MetaData.PREFIX+"vpc-conn",
            subnet: vpc.privateSubnets[0],
            securityGroups: [glueVPCNetworkConnectionSecurityGroup]
        });
        return vpcConn;
    }    
    
    private createGlueLogGroup(glueExecutionRole: IRole): ILogGroup {
        var logGroup = new LogGroup(this, MetaData.PREFIX+"glue-logs", {
            //logGroupName: MetaData.PREFIX+"glue-logs",
            logGroupName: "/aws-glue/jobs",
            removalPolicy: RemovalPolicy.DESTROY
        });
        logGroup.grantWrite(glueExecutionRole);
        return logGroup;
    }

    private createSimpleETLJob(glueExecutionRole:IRole, glueVPCConnection:IConnection, jobPostFix:string, codePath:string, logGroup:ILogGroup): IJob {
        var job = new Job(this, MetaData.PREFIX+jobPostFix, {
            jobName: MetaData.PREFIX+jobPostFix,            
            executable: JobExecutable.pythonEtl({
                glueVersion: GlueVersion.V3_0,
                pythonVersion: PythonVersion.THREE,                
                script: Code.fromAsset(codePath)
            }),
            workerCount:2,
            maxRetries:0,
            maxConcurrentRuns:1,            
            workerType: WorkerType.G_1X,
            timeout: Duration.minutes(20),
            role: glueExecutionRole,
            continuousLogging: {enabled:true, quiet:false, logGroup: logGroup},
            enableProfilingMetrics:true,
            connections: [glueVPCConnection]
        });        
        Tags.of(job).add(MetaData.NAME, MetaData.PREFIX+jobPostFix);
        return job;
    }


    private buildGlueExecutionRole(): IRole {
        var role = new Role(this, MetaData.PREFIX+"execution-role", {
            description: "Glue Execution Role",
            roleName: MetaData.PREFIX+"execution-role",
            assumedBy: new ServicePrincipal("glue.amazonaws.com"),
            managedPolicies: [
                ManagedPolicy.fromAwsManagedPolicyName("CloudWatchFullAccess"),
                //ManagedPolicy.fromAwsManagedPolicyName("AWSGlueServiceRole"),
                ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSGlueServiceRole"),
                //ManagedPolicy.fromAwsManagedPolicyName("AmazonSSMFullAccess"),
                //ManagedPolicy.fromManagedPolicyArn(this, "AWSLambdaSQSQueueExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"),
                //ManagedPolicy.fromManagedPolicyArn(this, "AWSLambdaBasicExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"),
                //ManagedPolicy.fromManagedPolicyArn(this, "AWSLambdaVPCAccessExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole")
            ],
        });
        role.addToPolicy(new PolicyStatement({
          effect: Effect.ALLOW,
          resources: ["*"],
          actions: ["secretsmanager:GetSecretValue","dbqms:*","rds-data:*","xray:*","dynamodb:GetItem","dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:Scan","dynamodb:Query"]
          //           "cloudwatch:*",   "logs:*", "glue:GetConnection"
        }));
        /*role.addToPolicy(new PolicyStatement({
            effect: Effect.ALLOW,
            resources: ["*"],
            actions: ["glue:GetConnection","ec2:DescribeSubnets","ec2:DescribeSecurityGroups"]
            //           "cloudwatch:*",   "logs:*", "glue:GetConnection"
          }));*/
        /*role.addToPolicy(new PolicyStatement({
            effect: Effect.ALLOW,
            resources: ["*"],
            actions: ["secretsmanager:GetSecretValue","dbqms:*","rds-data:*","xray:*","dynamodb:GetItem","dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:Scan","dynamodb:Query"]
        }));*/

        Tags.of(role).add(MetaData.NAME, MetaData.PREFIX+"execution-role");
        return role;
    }       
}