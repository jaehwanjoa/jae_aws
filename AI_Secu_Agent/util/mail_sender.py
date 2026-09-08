import boto3

ses = boto3.client(
    "ses",
    region_name="ap-northeast-2"
)

def send_mail(
    subject: str,
    body: str,
    receiver: str,
    sender: str
):

    response = ses.send_email(
        Source=sender,
        Destination={
            "ToAddresses": [
                receiver
            ]
        },
        Message={
            "Subject": {
                "Data": subject,
                "Charset": "UTF-8"
            },
            "Body": {
                "Html": {
                    "Data": body,
                    "Charset": "UTF-8"
                }
            }
        }
    )

    print(
        f"SES_MESSAGE_ID={response['MessageId']}"
    )
