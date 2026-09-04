import json
import boto3

from orchestrator import Orchestrator

s3 = boto3.client("s3")


def lambda_handler(event, context):

    print("EVENT=")
    print(json.dumps(event))

    #################################################
    # S3 Event
    #################################################

    if "Records" in event:

        record = event["Records"][0]

        if "s3" in record:

            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            print(f"S3_BUCKET={bucket}")
            print(f"S3_KEY={key}")

            obj = s3.get_object(
                Bucket=bucket,
                Key=key
            )

            body = (
                obj["Body"]
                .read()
                .decode("utf-8")
            )

            data = json.loads(body)

            if isinstance(data, list):
                data = data[0]

            issue_id = data.get("internal_id")

            print(
                f"S3_ISSUE_ID={issue_id}"
            )

            return Orchestrator.process_s3_incident(
                issue_id
            )

    #################################################
    # API Gateway
    #################################################

    body = json.loads(
        event.get("body", "{}")
    )

    question = body.get("question")
    customer = body.get("customer")

    return Orchestrator.process(
        question=question,
        customer=customer
    )
