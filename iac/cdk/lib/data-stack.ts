import { RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Table, BillingMode, AttributeType } from 'aws-cdk-lib/aws-dynamodb';
import { IVpc } from 'aws-cdk-lib/aws-ec2';
import { IRole } from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { MetaData } from './meta-data';

export class DataStack extends Stack {
    private apiRole:IRole;
    constructor(scope: Construct, id: string, vpc: IVpc, apiRole: IRole, props?: StackProps) {
        super(scope, id, props);
        this.apiRole = apiRole;
        //this.createTradeTable();        
    }

    /*private createTradeTable() {
        var name = MetaData.PREFIX+"trade";
        new Table(this, name, {
            tableName: name,
            billingMode: BillingMode.PAY_PER_REQUEST,
            partitionKey: {name: "trade_guid", type: AttributeType.STRING}
            //,sortKey: {name: "trade_type", type: AttributeType.STRING}
            ,removalPolicy: RemovalPolicy.DESTROY
        });
    }*/
}