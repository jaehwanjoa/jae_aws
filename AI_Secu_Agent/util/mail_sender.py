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
    ses.send_email(
        Source=sender,
        Destination={
            "ToAddresses": [
                receiver
            ]
        },
        Message={
            "Subject": {
                "Data": subject
            },
            "Body": {
                "Text": {
                    "Data": body
                }
            }
        }
    )
