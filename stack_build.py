# npm install -g aws-cdk
# to install node.js required by aws cdk irrespective of the language
# Install aws cli and then configure credentials using aws configure


from aws_cdk import (
    Stack,
    aws_s3 as s3,
    App, CfnOutput
)
import aws_cdk as cdk

app = App()
stack = Stack(app, "LogoReconProjectStack")

# Create an S3 bucket
bucket = s3.Bucket(
    stack, "OLM_pics_bucket",
    bucket_name="OLM_pics_bucke",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True,
    block_public_access=s3.BlockPublicAccess.BLOCK_ALL
)

# Output the bucket name
CfnOutput(
    stack, "BucketName",
    value=bucket.bucket_name,
    description="The name of the S3 bucket"
)

app.synth()
