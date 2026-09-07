import json
import boto3

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-northeast-2"
)

MODEL_ID = "anthropic.claude-sonnet-4"

class BedrockAnalyzer:

    @staticmethod
    def analyze(prompt):

        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "anthropic_version":
                "bedrock-2023-05-31",

                "max_tokens":
                1500,

                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        result = json.loads(
            response["body"].read()
        )

        return result["content"][0]["text"]
