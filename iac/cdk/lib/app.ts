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

const app = new App();
var region = process.env["CDK_DEFAULT_REGION"];
region = "eu-west-1"; // override
var props = {env: {account: process.env["CDK_DEFAULT_ACCOUNT"], region: region } };
var metaData = new MetaData();

var networkStack = new NetworkStack(app, MetaData.PREFIX+"network-stack", props);
var computeStack = new ComputeStack(app, MetaData.PREFIX+"compute-stack", networkStack.Vpc, networkStack.GlueVPCNetworkConnectionSecurityGroup, props);
new DataStack(app, MetaData.PREFIX+"data-stack", networkStack.Vpc,  networkStack.MySQLSecurityGroup, computeStack.glueExecutionRole, props);
//new DeveloperStack(app, MetaData.PREFIX+"developer-stack", networkStack.Vpc, props);