import boto3

class AthenaClient:

    @classmethod
    def execute(
        cls,
        database,
        query
    ):

        athena = boto3.client(
            "athena"
        )

        response = athena.start_query_execution(
            QueryString=query,

            QueryExecutionContext={
                "Database": database
            },

            ResultConfiguration={
                "OutputLocation":
                "s3://aws-cjl-cortex-logs/WAF_LOG/"
            }
        )

        return response[
            "QueryExecutionId"
        ]
