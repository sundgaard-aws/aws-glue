#!/usr/bin/env node
import 'source-map-support/register';
//import { MetaData } from './meta-data';
import { env } from 'process';
import { MetaData } from './meta-data';
import { NetworkStack } from './network-stack';
import { ComputeStack } from './compute-stack';
import { DeveloperStack } from './developer-stack';
import { DataStack } from './data-stack';
import { App } from 'aws-cdk-lib';
import { SecurityStack } from './security-stack';

const app = new App();
var region = process.env["CDK_DEFAULT_REGION"];
region = "eu-west-1"; // override
const recreateS3Buckets=false;
var props = {env: {account: process.env["CDK_DEFAULT_ACCOUNT"], region: region } };
var metaData = new MetaData();

var networkStack = new NetworkStack(app, MetaData.PREFIX+"network-stack", props);
var securityStack = new SecurityStack(app, MetaData.PREFIX+"security-stack", networkStack.Vpc, props);
var computeStack = new ComputeStack(app, MetaData.PREFIX+"compute-stack", networkStack.Vpc, securityStack.GlueVPCNetworkConnectionSecurityGroup, props);
new DataStack(app, MetaData.PREFIX+"data-stack", networkStack.Vpc,  securityStack.MySQLSecurityGroup, securityStack.AuroraPostgreSqlSecurityGroup, computeStack.glueExecutionRole, recreateS3Buckets, region, props);
//new DeveloperStack(app, MetaData.PREFIX+"developer-stack", networkStack.Vpc, props);



