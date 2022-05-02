import { Construct } from 'constructs';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { ISecurityGroup, IVpc } from 'aws-cdk-lib/aws-ec2';
import { Duration, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { Effect, IRole, ManagedPolicy, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { HttpMethod } from 'aws-cdk-lib/aws-events';
import {Code, GlueVersion, IJob, Job, JobExecutable, PythonVersion, WorkerType} from '@aws-cdk/aws-glue-alpha';

export class ComputeStack extends Stack {
    private ssmHelper = new SSMHelper();
    public apiRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, apiSecurityGroup: ISecurityGroup, props?: StackProps) {
        super(scope, id, props);

        this.apiRole = this.buildExecutionRole();
        this.createJob(this.apiRole);
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

    private createJob(apiRole:IRole): IJob {
        var job = new Job(this, MetaData.PREFIX+"lab1", {
            jobName: MetaData.PREFIX+"lab1",            
            executable: JobExecutable.pythonStreaming({
                glueVersion: GlueVersion.V2_0,
                pythonVersion: PythonVersion.THREE,                
                script: Code.fromAsset("../../python/trade-import/lab1.py")
            }),
            workerCount:2,
            maxRetries:0,
            workerType: WorkerType.G_1X,
            timeout: Duration.minutes(20),
            role: apiRole
        });

        return job;
    }
}