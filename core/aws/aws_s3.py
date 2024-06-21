import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
import base64

AWS_KEY_ID = "AKIAZ7BFZUH3RA2OLXWB"
AWS_SECRET = "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"

s3 = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}), region_name='eu-west-3')


def upload_image(key: str, base64_string: str, bucket: str, aws_region: str = "eu-west-3"):
    s3 = boto3.client('s3', 
                      region_name=aws_region,
                      aws_access_key_id=AWS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET
                       )
    new_image = base64.b64decode(base64_string)
    try:
        s3.put_object(
            Bucket=bucket, Key=key, Body=new_image, ACL='public-read',
            ContentType='image/jpeg', ContentEncoding='base64')
        return f"https://{bucket}.s3.{aws_region}.amazonaws.com/{key}"
    except ClientError as e:
        return str(e.response['Error']['Message'])


def get_pre_singed_url(bucket_name: str, object_name: str, expiration=600):
    try:
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        return str(e.response['Error']['Message'])


def delete_object(key: str, bucket: str, aws_region: str = "eu-west-3"):
    s3 = boto3.client('s3', 
                      region_name=aws_region,
                      aws_access_key_id=AWS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET
                       )
    try:
        return s3.delete_object(
            Bucket=bucket,
            Key=key
        )
    except ClientError as e:
        return str(e.response['Error']['Message'])
