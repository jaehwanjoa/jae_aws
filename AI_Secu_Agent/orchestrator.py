import json

def process_response(raw_text):

    print("========== RAW JSON START ==========")
    print(raw_text)
    print("========== RAW JSON END ==========")

    response = json.loads(raw_text)

    issues = response["reply"]["DATA"]

    return issues
