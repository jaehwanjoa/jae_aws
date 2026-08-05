def lambda_handler(
    event,
    context
):

    question = event["question"]

    table_name = event["table_name"]

    result = Orchestrator.process(
        question=question,
        table_name=table_name
    )

    return result
