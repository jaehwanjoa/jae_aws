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

            cspm_sha256 = None
            cspm_verdict = None

            if data.get("alert_source") == "COMPUTE_POLICY":

                issue = (
                    data
                    .get("original_alert_json", {})
                    .get("original_alert_json", {})
                    .get("issues", [{}])[0]
                )

                normalized = issue.get(
                    "xdm.issue.normalized_fields",
                    {}
                )

                cspm_sha256 = normalized.get(
                    "xdm.file.sha256"
                )

                cspm_verdict = normalized.get(
                    "xdm.malware.verdict"
                )

                print(f"CSPM_SHA256={cspm_sha256}")
                print(f"CSPM_VERDICT={cspm_verdict}")

            issue_id = data.get("internal_id")

            print(
                f"S3_ISSUE_ID={issue_id}"
            )

            return Orchestrator.process_s3_incident(
                issue_id,
                cspm_sha256,
                cspm_verdict
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

#
