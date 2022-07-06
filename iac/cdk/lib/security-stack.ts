import { Stack, StackProps, Tags } from 'aws-cdk-lib';
import { ISecurityGroup, IVpc, Port, SecurityGroup } from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';
import { MetaData } from './meta-data';

export class SecurityStack extends Stack {
    public GlueVPCNetworkConnectionSecurityGroup: ISecurityGroup;
    public MySQLSecurityGroup: ISecurityGroup;
    public AuroraPostgreSqlSecurityGroup: ISecurityGroup;

    constructor(scope: Construct, id: string, vpc: IVpc, props?: StackProps) {
        super(scope, id, props);
        this.MySQLSecurityGroup = this.createMySQLSecurityGroup(vpc);
        this.AuroraPostgreSqlSecurityGroup = this.createAuroraPostgreSqlSecurityGroup(vpc);
        this.GlueVPCNetworkConnectionSecurityGroup = this.createGlueVPCNetworkConnectionSecurityGroup(vpc);        
    }   
    
    private createGlueVPCNetworkConnectionSecurityGroup(vpc: IVpc): ISecurityGroup {
        var postFix = "vpc-network-conn-sg";
        var glueNetworkConnSecurityGroup = new SecurityGroup(this, MetaData.PREFIX+postFix, {
            vpc: vpc,
            securityGroupName: MetaData.PREFIX+postFix,
            description: MetaData.PREFIX+postFix,
            allowAllOutbound: true
        });
        
        Tags.of(glueNetworkConnSecurityGroup).add(MetaData.NAME, MetaData.PREFIX+postFix);
        glueNetworkConnSecurityGroup.connections.allowFrom(glueNetworkConnSecurityGroup, Port.allTraffic(), "AWS Glue needs allow self on all inbound");
        this.MySQLSecurityGroup.connections.allowFrom(glueNetworkConnSecurityGroup, Port.tcp(3306), "AWS Glue");
        this.AuroraPostgreSqlSecurityGroup.connections.allowFrom(glueNetworkConnSecurityGroup, Port.tcp(5432), "AWS Glue");
        return glueNetworkConnSecurityGroup;
    }

    private createAuroraPostgreSqlSecurityGroup(vpc: IVpc): ISecurityGroup {
        var postFix = "aurora-postgresql-sg";
        var securityGroup = new SecurityGroup(this, MetaData.PREFIX+postFix, {
            vpc: vpc,
            securityGroupName: MetaData.PREFIX+postFix,
            description: MetaData.PREFIX+postFix,
            allowAllOutbound: true
        });
        
        Tags.of(securityGroup).add(MetaData.NAME, MetaData.PREFIX+postFix);
        return securityGroup;
    }

    private createMySQLSecurityGroup(vpc: IVpc): ISecurityGroup {
        var postFix = "rds-mysql-sg";
        var securityGroup = new SecurityGroup(this, MetaData.PREFIX+postFix, {
            vpc: vpc,
            securityGroupName: MetaData.PREFIX+postFix,
            description: MetaData.PREFIX+postFix,
            allowAllOutbound: true
        });
        
        Tags.of(securityGroup).add(MetaData.NAME, MetaData.PREFIX+postFix);
        return securityGroup;
    }
}