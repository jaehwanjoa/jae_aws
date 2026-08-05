import boto3
import time

athena = boto3.client(
    "athena"
)


class AthenaExecutor:

    @classmethod
    def execute(
        cls,
        query,
        database,
        output_location
    ):

        response = (
            athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    "Database": database
                },
                ResultConfiguration={
                    "OutputLocation":
                        output_location
                }
            )
        )

        query_execution_id = (
            response["QueryExecutionId"]
        )

        return query_execution_id
