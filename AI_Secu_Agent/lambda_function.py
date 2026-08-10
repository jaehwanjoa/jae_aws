from orchestrator import Orchestrator

def lambda_handler(event, context):

    question = event.get("question")
    customer = event.get("customer")

    return Orchestrator.process(
        question=question,
        customer=customer
    )

import json
import re

def safe_json_loads(raw_json: str):
    try:
        return json.loads(raw_json)

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")

        start = max(0, e.pos - 100)
        end = min(len(raw_json), e.pos + 100)

        print("===== ERROR CONTEXT START =====")
        print(raw_json[start:end])
        print("===== ERROR CONTEXT END =====")

        sanitized = re.sub(
            r'\\(?!["\\/bfnrtu])',
            r'\\\\',
            raw_json
        )

        print("Invalid escape sequence sanitized")

        return json.loads(sanitized)

