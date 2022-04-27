import { Secret } from "aws-cdk-lib/aws-secretsmanager";
import { ParameterType, StringParameter } from "aws-cdk-lib/aws-ssm";
import { Construct } from "constructs";

export class SSMHelper {

    constructor() {
    }

    public createSSMParameter(stack: Construct, parameterName: string, parameterValue: string, parameterType: ParameterType) {
        new StringParameter(stack, parameterName, {
            description: parameterName,
            parameterName: parameterName,
            stringValue: parameterValue,
            type: parameterType
            // allowedPattern: '.*',
        });
    }
    
    public createSecureSSMParameter(stack: Construct, parameterName: string, parameterValue: string, parameterType: ParameterType) {
        new Secret(stack, parameterName, {
            description: parameterName,
            secretName: parameterName,
            generateSecretString: {}
            // allowedPattern: '.*',
        });
    }    
}