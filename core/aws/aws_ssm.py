import boto3

AWS_S3_CREDS = {
    "aws_access_key_id":"AKIAZ7BFZUH3RA2OLXWB",
    "aws_secret_access_key":"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"
}
def fetch_ssm_config(name):
    ssm = boto3.client('ssm', region_name="eu-west-3",**AWS_S3_CREDS)
    data = ssm.get_parameter(Name=name)
    value = data['Parameter']['Value']
    return value
