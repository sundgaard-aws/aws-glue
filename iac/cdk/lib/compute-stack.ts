import { Construct } from 'constructs';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { ISecurityGroup, IVpc } from 'aws-cdk-lib/aws-ec2';
import { Duration, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { Effect, IRole, ManagedPolicy, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { HttpMethod } from 'aws-cdk-lib/aws-events';
import {Code, GlueVersion, IJob, Job, JobExecutable, PythonVersion} from '@aws-cdk/aws-glue-alpha';

export class ComputeStack extends Stack {
    private runtime:Runtime = Runtime.NODEJS_12_X;    
    private ssmHelper = new SSMHelper();
    public apiRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, apiSecurityGroup: ISecurityGroup, props?: StackProps) {
        super(scope, id, props);

        this.apiRole = this.buildExecutionRole();
        this.createJob(apiSecurityGroup, vpc);
    }

    private buildExecutionRole(): IRole {
        var role = new Role(this, MetaData.PREFIX+"execution-role", {
            description: "Glue Execution Role",
            roleName: MetaData.PREFIX+"execution-role",
            assumedBy: new ServicePrincipal("glue.amazonaws.com"),
            managedPolicies: [
                ManagedPolicy.fromAwsManagedPolicyName("AWSStepFunctionsFullAccess"),
                ManagedPolicy.fromAwsManagedPolicyName("AmazonSSMFullAccess"),
                ManagedPolicy.fromManagedPolicyArn(this, "AWSLambdaSQSQueueExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"),
                ManagedPolicy.fromManagedPolicyArn(this, "AWSLambdaBasicExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"),
                ManagedPolicy.fromManagedPolicyArn(this, "AWSLambdaVPCAccessExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole")
            ],
        });
        role.addToPolicy(new PolicyStatement({
          effect: Effect.ALLOW,
          resources: ["*"],
          actions: ["secretsmanager:GetSecretValue","dbqms:*","rds-data:*","xray:*","dynamodb:GetItem","dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:Scan","dynamodb:Query"]
        }));

        Tags.of(role).add(MetaData.NAME, MetaData.PREFIX+"execution-role");
        return role;
    }      

    private createJob(): IJob {
        var job = new Job(this, MetaData.PREFIX+"sql-server-to-s3", {
            jobName: MetaData.PREFIX+"sql-server-to-s3",
            executable: JobExecutable.pythonStreaming({
                glueVersion: GlueVersion.V2_0,
                pythonVersion: PythonVersion.THREE,
                script: Code.fromAsset("../../python/simple.py")
            }),
        });

        return job;
    }
}