import { Construct } from 'constructs';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { ISecurityGroup, IVpc } from 'aws-cdk-lib/aws-ec2';
import { Duration, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { Effect, IRole, ManagedPolicy, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { HttpMethod } from 'aws-cdk-lib/aws-events';
import {Code, GlueVersion, IJob, Job, JobExecutable, PythonVersion, WorkerType} from '@aws-cdk/aws-glue-alpha';
import { LoggingLevel } from 'aws-cdk-lib/aws-chatbot';

export class ComputeStack extends Stack {
    private ssmHelper = new SSMHelper();
    public glueExecutionRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, props?: StackProps) {
        super(scope, id, props);

        this.glueExecutionRole = this.buildGlueExecutionRole();
        var codePathRoot = "../../python/trade-import/";
        this.createSimpleETLJob(this.glueExecutionRole, "lab1", codePathRoot+"lab1.py");
        this.createSimpleETLJob(this.glueExecutionRole, "lab2", codePathRoot+"lab2.py");
        this.createSimpleETLJob(this.glueExecutionRole, "lab3", codePathRoot+"lab3.py");
        /*this.createSimpleETLJob(this.apiRole, "lab4", codePathRoot+"lab4.py");
        this.createSimpleETLJob(this.apiRole, "lab5", codePathRoot+"lab5.py");
        this.createSimpleETLJob(this.apiRole, "lab6", codePathRoot+"lab6.py");
        this.createSimpleETLJob(this.apiRole, "lab7", codePathRoot+"lab7.py");
        this.createSimpleETLJob(this.apiRole, "lab8", codePathRoot+"lab8.py");
        this.createSimpleETLJob(this.apiRole, "lab9", codePathRoot+"lab9.py");
        this.createSimpleETLJob(this.apiRole, "lab10", codePathRoot+"lab10.py");*/
    }

    private buildGlueExecutionRole(): IRole {
        var role = new Role(this, MetaData.PREFIX+"execution-role", {
            description: "Glue Execution Role",
            roleName: MetaData.PREFIX+"execution-role",
            assumedBy: new ServicePrincipal("glue.amazonaws.com"),
            managedPolicies: [
                //ManagedPolicy.fromAwsManagedPolicyName("AWSStepFunctionsFullAccess"),
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
        }));
        /*role.addToPolicy(new PolicyStatement({
            effect: Effect.ALLOW,
            resources: ["*"],
            actions: ["secretsmanager:GetSecretValue","dbqms:*","rds-data:*","xray:*","dynamodb:GetItem","dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:Scan","dynamodb:Query"]
        }));*/

        Tags.of(role).add(MetaData.NAME, MetaData.PREFIX+"execution-role");
        return role;
    }      

    private createSimpleETLJob(glueExecutionRole:IRole, jobPostFix:string, codePath:string): IJob {
        var job = new Job(this, MetaData.PREFIX+jobPostFix, {
            jobName: MetaData.PREFIX+jobPostFix,            
            executable: JobExecutable.pythonEtl({
                glueVersion: GlueVersion.V2_0,
                pythonVersion: PythonVersion.THREE,                
                script: Code.fromAsset(codePath)
            }),
            workerCount:2,
            maxRetries:0,
            workerType: WorkerType.G_1X,
            timeout: Duration.minutes(20),
            role: glueExecutionRole,
            continuousLogging: {enabled:true}
        });

        return job;
    }
}