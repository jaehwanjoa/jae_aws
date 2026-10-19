import time

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

    @classmethod
    def wait(
        cls,
        query_execution_id
    ):

        athena = boto3.client(
            "athena"
        )

        while True:

            response = (
                athena.get_query_execution(
                    QueryExecutionId=
                    query_execution_id
                )
            )

            state = (
                response
                ["QueryExecution"]
                ["Status"]
                ["State"]
            )

            print(
                f"ATHENA_STATUS={state}"
            )

            if state == "SUCCEEDED":

                return True

            if state in [
                "FAILED",
                "CANCELLED"
            ]:
            
                reason = (
                    response
                    ["QueryExecution"]
                    ["Status"]
                    .get(
                        "StateChangeReason",
                        "UNKNOWN"
                    )
                )
            
                print(
                    f"ATHENA_ERROR={reason}"
                )
            
                raise Exception(
                    f"Athena Query {state}: {reason}"
                )
    
            time.sleep(2)


    @classmethod
    def get_results(
        cls,
        query_execution_id
    ):
    
        athena = boto3.client(
            "athena"
        )
    
        response = (
            athena.get_query_results(
                QueryExecutionId=
                query_execution_id
            )
        )
    
        rows = (
            response
            ["ResultSet"]
            ["Rows"]
        )
    
        if len(rows) <= 1:
            return []
    
        headers = [
            col["VarCharValue"]
            for col in rows[0]["Data"]
        ]
    
        results = []
    
        for row in rows[1:]:
    
            item = {}

            for idx, header in enumerate(headers):
            
                value = None
            
                if idx < len(row["Data"]):
                    value = row["Data"][idx].get(
                        "VarCharValue"
                    )
            
                item[header] = value
            
            results.append(
                item
            )
    
        return results

    @classmethod
    def query(
        cls,
        database,
        query
    ):

        query_execution_id = (
            cls.execute(
                database,
                query
            )
        )

        cls.wait(
            query_execution_id
        )

        return cls.get_results(
            query_execution_id
        )
