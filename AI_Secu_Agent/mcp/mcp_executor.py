import boto3
import time


class MCPExecutor:

    @classmethod
    def execute_athena(
        cls,
        query: str
    ):

        athena = boto3.client(
            "athena",
            region_name="ap-northeast-2"
        )
        
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                "Database": "jaehwan-aws-waf"
            },
            WorkGroup="jaehwan",
            ResultConfiguration={
                "OutputLocation":
                    "s3://202040710-jaehwan-test/athena-results/"
            }
        )
        
        query_id = response[
            "QueryExecutionId"
        ]

        while True:

            status = athena.get_query_execution(
                QueryExecutionId=query_id
            )

            state = status[
                "QueryExecution"
            ][
                "Status"
            ][
                "State"
            ]

            if state == "SUCCEEDED":
                break

            if state in [
                "FAILED",
                "CANCELLED"
            ]:
                raise Exception(
                    f"Athena Query {state}"
                )

            time.sleep(2)

        results = athena.get_query_results(
            QueryExecutionId=query_id
        )

        return results
