import boto3
from botocore.exceptions import ClientError
AWS_S3_CREDS = {
    "aws_access_key_id":"AKIAZ7BFZUH3RA2OLXWB",
    "aws_secret_access_key":"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"
}
def send_email(subject: str, body_text: str, body_html: str, sender: str, recipient: list, aws_region: str):
    subject = subject
    body_text = body_text

    # The HTML body of the email.
    body_html = body_html

    client = boto3.client('ses', region_name=aws_region,**AWS_S3_CREDS)
    try:
        client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=sender
        )
    except ClientError as e:
        return str(e.response['Error']['Message'])
    else:
        return "Email sent!"
