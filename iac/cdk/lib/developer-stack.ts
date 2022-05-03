import { Construct } from 'constructs';
import { MetaData } from './meta-data';
import { SSMHelper } from './ssm-helper';
import { CfnInstance, CfnSecurityGroup, CfnVPC, InstanceType, ISecurityGroup, IVpc, SubnetType } from 'aws-cdk-lib/aws-ec2';
import { CfnOutput, Stack, StackProps } from 'aws-cdk-lib';
import { IRole } from 'aws-cdk-lib/aws-iam';
import {Ec2Environment} from '@aws-cdk/aws-cloud9-alpha';
import { CfnInclude } from 'aws-cdk-lib/cloudformation-include';

export class DeveloperStack extends Stack {
    private ssmHelper = new SSMHelper();
    public glueExecutionRole:IRole;

    constructor(scope: Construct, id: string, vpc: IVpc, props?: StackProps) {
        super(scope, id, props);
        this.createCloud9EnvL1(vpc);
        //this.createCloud9EnvL2(vpc);
    } 

    private createCloud9EnvL1(vpc: IVpc) {
        var postfix = "cloud9-env";
        var cloud9Template = new CfnInclude(this, MetaData.PREFIX+postfix, {
            templateFile: "./yaml/cloud9.yaml"
        });
        //const cfnVPC = cloud9Template.getResource('cloud9-vpc-id') as CfnVPC;
        //cfnVPC.overrideLogicalId(vpc.vpcId);
        const cfnSecurityGroup = cloud9Template.getResource('InstanceSecurityGroup') as CfnSecurityGroup; 
        cfnSecurityGroup.vpcId=vpc.vpcId;
        const cfnInstance = cloud9Template.getResource('Instance') as CfnInstance;
        cfnInstance.subnetId=vpc.privateSubnets[0].subnetId;
    }
    
    private createCloud9EnvL2(vpc: IVpc) {
        // create a cloud9 ec2 environment in a new VPC
        var postfix = "cloud9-env";
        const cloud9Env = new Ec2Environment(this, MetaData.PREFIX+postfix, {
            vpc,
            subnetSelection: { subnetType: SubnetType.PRIVATE_WITH_NAT, },
            instanceType: new InstanceType('t3.micro'),
            ec2EnvironmentName: MetaData.PREFIX+postfix,
            description: MetaData.PREFIX+postfix            
        });
        
        //Tags.of(cloud9Env).add(MetaData.NAME, MetaData.PREFIX+"cloud9-env");
        //Tags.of(cloud9Env).add(MetaData.NAME, MetaData.PREFIX+postfix+"-sg", { includeResourceTypes: [CfnSecurityGroup.CFN_RESOURCE_TYPE_NAME]});
        //Tags.of(cloud9Env).add(MetaData.NAME, MetaData.PREFIX+postfix+"-env", { includeResourceTypes: [CfnEnvironmentEC2.CFN_RESOURCE_TYPE_NAME]});
        //Tags.of(cloud9Env).add(MetaData.NAME, MetaData.PREFIX+postfix+"-role", { includeResourceTypes: [CfnRole.CFN_RESOURCE_TYPE_NAME]});
        
        // print the Cloud9 IDE URL in the output
        new CfnOutput(this, 'URL', { value: cloud9Env.ideUrl });
    }
}