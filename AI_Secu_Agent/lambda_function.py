from orchestrator.orchestrator import Orchestrator

def lambda_handler(event, context):

    question = event["question"]

    return Orchestrator.process(
        question
    )
