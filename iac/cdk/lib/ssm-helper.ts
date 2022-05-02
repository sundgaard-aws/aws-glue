import { ISecret, Secret } from "aws-cdk-lib/aws-secretsmanager";
import { ParameterType, StringParameter } from "aws-cdk-lib/aws-ssm";
import { Construct } from "constructs";

export class SSMHelper {

    constructor() {
    }

    public createSSMParameter(stack: Construct, parameterName: string, parameterValue: string, parameterType: ParameterType): StringParameter {
        var param = new StringParameter(stack, parameterName, {
            description: parameterName,
            parameterName: parameterName,
            stringValue: parameterValue,
            type: parameterType
            // allowedPattern: '.*',
        });
        return param;
    }
    
    public createSecureSSMParameter(stack: Construct, parameterName: string, parameterValue: string, parameterType: ParameterType): ISecret {
        var secretParam = new Secret(stack, parameterName, {
            description: parameterName,
            secretName: parameterName,
            generateSecretString: {}
            // allowedPattern: '.*',
        });
        return secretParam;
    }    
}