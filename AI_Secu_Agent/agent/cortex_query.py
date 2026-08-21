from agent.filter_map import FILTER_MAP


def build_issue_query(route):

    if not route:
        return None

    if route["source"] != "cortex":
        return None

    query = FILTER_MAP.get(route["intent"])

    print("FILTER_MAP_DEBUG=")
    print(query)

    return query
