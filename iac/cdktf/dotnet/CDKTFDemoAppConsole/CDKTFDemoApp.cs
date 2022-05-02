using System;
using Constructs;
using HashiCorp.Cdktf;
using HashiCorp.Cdktf.Providers.Aws;
using HashiCorp.Cdktf.Providers.Aws.Ec2;

namespace AWS.Labs
{
    class CDKTFDemoApp : TerraformStack
    {
        public CDKTFDemoApp(Construct scope, string id) : base(scope, id)
        {
            new AwsProvider(this, "AWS", new AwsProviderConfig { Region = "eu-west-1" });
            var instance = new Instance(this, "compute", new InstanceConfig
            {
                Ami = "ami-01456a894f71116f2",
                InstanceType = "t2.micro"
            });
            instance.Tags.Add("Name", "CDKTFDemoAppEC2");
            new TerraformOutput(this, "public_ip", new TerraformOutputConfig
            {
                Value = instance.PublicIp
            });
        }
        public static void Main(string[] args)
        {
            Console.WriteLine("Deploying components via Terraform from local machine...");
            var app = new App();
            var stack = new CDKTFDemoApp(app, "CDKTFDemoApp");
            app.Synth();
            Console.WriteLine("DONE - Deploying components via Terraform from local machine.");
        }
    }
}