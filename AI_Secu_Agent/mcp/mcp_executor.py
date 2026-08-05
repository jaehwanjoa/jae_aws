class MCPExecutor:

    @classmethod
    def execute_athena(
        cls,
        query: str
    ):

        return {
            "tool": "manage_aws_athena_query_executions",

            "operation":
                "start-query-execution",

            "query": query
        }
