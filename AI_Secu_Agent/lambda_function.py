import json
from orchestrator import Orchestrator


def lambda_handler(event, context):

    print("EVENT=")
    print(json.dumps(event))

    body = json.loads(
        event.get("body", "{}")
    )

    question = body.get("question")
    customer = body.get("customer")

    return Orchestrator.process(
        question=question,
        customer=customer
    )
