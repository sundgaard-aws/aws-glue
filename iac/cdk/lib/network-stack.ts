import { CfnOutput, Stack, StackProps, Tags } from 'aws-cdk-lib';
import { AclCidr, AclTraffic, Action, CfnInternetGateway, CfnNatGateway, CfnNetworkAcl, CfnRouteTable, CfnSecurityGroup, CfnSubnet, GatewayVpcEndpointAwsService, INetworkAcl, ISecurityGroup, IVpc, NetworkAcl, Port, Protocol, SecurityGroup, SubnetType, TrafficDirection, Vpc } from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';
import { MetaData } from './meta-data';

export class NetworkStack extends Stack {
    public Vpc:IVpc;

    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);
        this.Vpc = this.createVPC();
        this.createVPCEndpoints(this.Vpc);
    }   
    
    private createVPC():IVpc {
        // Link: https://blog.codecentric.de/en/2019/09/aws-cdk-create-custom-vpc/
        var vpc = new Vpc(this, MetaData.PREFIX+"vpc", {
            cidr: "10.90.0.0/16", subnetConfiguration: [
                { cidrMask: 24, name: MetaData.PREFIX+"private-sne", subnetType: SubnetType.PRIVATE_WITH_NAT },
                { cidrMask: 25, name: MetaData.PREFIX+"public-sne", subnetType: SubnetType.PUBLIC }
            ],
            natGateways: 1,
            maxAzs: 2
        });
        
        var publicNacl = this.createPublicNacl(vpc);
        vpc.publicSubnets.forEach( subnet => { subnet.associateNetworkAcl(MetaData.PREFIX+"public-nacl-assoc", publicNacl) } );
        var privateNacl = this.createPrivateNacl(vpc);
        vpc.privateSubnets.forEach( subnet => { subnet.associateNetworkAcl(MetaData.PREFIX+"private-nacl-assoc", privateNacl) } );        
        this.tagVPCResources(vpc);
        new CfnOutput(this, 'Private Subnet ID', { value: vpc.privateSubnets[0].subnetId });
        
        return vpc;
    }
    
    private createPublicNacl(vpc: Vpc):INetworkAcl {
        var publicNacl = new NetworkAcl(this, MetaData.PREFIX+"public-nacl", {
            vpc: vpc,
            networkAclName: MetaData.PREFIX+"public-nacl",
            subnetSelection: {
                subnetType: SubnetType.PUBLIC
            }
        });
        publicNacl.addEntry(MetaData.PREFIX+"public-nacl-allow-all-inbound", {
           cidr: AclCidr.anyIpv4(),
           direction: TrafficDirection.INGRESS,
           ruleAction: Action.ALLOW,
           ruleNumber: 500,
           traffic: AclTraffic.allTraffic(),
           networkAclEntryName: "all-traffic"
        });
        publicNacl.addEntry(MetaData.PREFIX+"public-nacl-allow-all-outbound", {
           cidr: AclCidr.anyIpv4(),
           direction: TrafficDirection.EGRESS,
           ruleAction: Action.ALLOW,
           ruleNumber: 500,
           traffic: AclTraffic.allTraffic(),
           networkAclEntryName: "all-traffic"
        });        
        Tags.of(publicNacl).add(MetaData.NAME, MetaData.PREFIX+"public-nacl");
        return publicNacl;
    }
    
    private createPrivateNacl(vpc: Vpc):INetworkAcl {
        var privateNacl = new NetworkAcl(this, MetaData.PREFIX+"private-nacl", {
            vpc: vpc,
            networkAclName: MetaData.PREFIX+"private-nacl",
            subnetSelection: {
                subnetType: SubnetType.PRIVATE_WITH_NAT
            }
        });
        privateNacl.addEntry(MetaData.PREFIX+"private-nacl-allow-all-inbound", {
           cidr: AclCidr.anyIpv4(),
           direction: TrafficDirection.INGRESS,
           ruleAction: Action.ALLOW,
           ruleNumber: 500,
           traffic: AclTraffic.allTraffic(),
           networkAclEntryName: "all-traffic"
        });
        privateNacl.addEntry(MetaData.PREFIX+"private-nacl-deny-inbound-ssh", {
           cidr: AclCidr.anyIpv4(),
           direction: TrafficDirection.INGRESS,
           ruleAction: Action.DENY,
           ruleNumber: 100,
           traffic: AclTraffic.tcpPort(22),
           networkAclEntryName: "deny-ssh"
        });        
        privateNacl.addEntry(MetaData.PREFIX+"private-nacl-allow-all-outbound", {
           cidr: AclCidr.anyIpv4(),
           direction: TrafficDirection.EGRESS,
           ruleAction: Action.ALLOW,
           ruleNumber: 500,
           traffic: AclTraffic.allTraffic(),
           networkAclEntryName: "all-traffic"
        });
        Tags.of(privateNacl).add(MetaData.NAME, MetaData.PREFIX+"private-nacl");
        return privateNacl;
    }

    private createVPCEndpoints(vpc: IVpc) {
        /*vpc.addGatewayEndpoint(MetaData.PREFIX+"dyndb-ep", {
            service: GatewayVpcEndpointAwsService.DYNAMODB,
            subnets: [
                 { subnetType: SubnetType.PRIVATE_ISOLATED }, { subnetType: SubnetType.PUBLIC }
            ]
        });
        vpc.addGatewayEndpoint(MetaData.PREFIX+"s3-ep", {
            service: GatewayVpcEndpointAwsService.S3,
            subnets: [
                 { subnetType: SubnetType.PRIVATE_ISOLATED }, { subnetType: SubnetType.PUBLIC }
            ]
        });*/
    }
    
    private tagVPCResources(vpc: Vpc) {
        Tags.of(vpc).add(MetaData.NAME, MetaData.PREFIX+"vpc");
        Tags.of(vpc).add(MetaData.NAME, MetaData.PREFIX+"igw", { includeResourceTypes: [CfnInternetGateway.CFN_RESOURCE_TYPE_NAME] });
        Tags.of(vpc).add(MetaData.NAME, MetaData.PREFIX+"nat", { includeResourceTypes: [CfnNatGateway.CFN_RESOURCE_TYPE_NAME]});
        Tags.of(vpc).add(MetaData.NAME, MetaData.PREFIX+"default-nacl", { includeResourceTypes: [CfnNetworkAcl.CFN_RESOURCE_TYPE_NAME]});
        var defaultNacl = NetworkAcl.fromNetworkAclId(vpc, MetaData.PREFIX+"vpc", vpc.vpcDefaultNetworkAcl);
        Tags.of(defaultNacl).add(MetaData.NAME, MetaData.PREFIX+"default-nacl");
        
        Tags.of(vpc).add(MetaData.NAME, MetaData.PREFIX+"default-sg", { includeResourceTypes: [CfnSecurityGroup.CFN_RESOURCE_TYPE_NAME]});
        
        vpc.publicSubnets.forEach( subnet => {
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"public-sne", { includeResourceTypes: [CfnSubnet.CFN_RESOURCE_TYPE_NAME]});
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"public-rt", { includeResourceTypes: [CfnRouteTable.CFN_RESOURCE_TYPE_NAME]});
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"public-nacl", { includeResourceTypes: [CfnNetworkAcl.CFN_RESOURCE_TYPE_NAME]});
        });
        
        vpc.privateSubnets.forEach( subnet => {
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"private-sne", { includeResourceTypes: [CfnSubnet.CFN_RESOURCE_TYPE_NAME]});
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"private-rt", { includeResourceTypes: [CfnRouteTable.CFN_RESOURCE_TYPE_NAME]});
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"private-nacl", { includeResourceTypes: [CfnNetworkAcl.CFN_RESOURCE_TYPE_NAME]});
        });
        
        vpc.isolatedSubnets.forEach( subnet => {
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"isolated-sne", { includeResourceTypes: [CfnSubnet.CFN_RESOURCE_TYPE_NAME]});
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"isolated-rt", { includeResourceTypes: [CfnRouteTable.CFN_RESOURCE_TYPE_NAME]});
            Tags.of(subnet).add(MetaData.NAME, MetaData.PREFIX+"isolated-nacl", { includeResourceTypes: [CfnNetworkAcl.CFN_RESOURCE_TYPE_NAME]});
        });
    }
}