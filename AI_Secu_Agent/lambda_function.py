def lambda_handler(event, context):

    question = event.get("question")
    customer = event.get("customer")

    return Orchestrator.process(
        question=question,
        customer=customer
    )
