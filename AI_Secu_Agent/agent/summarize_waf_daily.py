def summarize_waf_daily(
    uri_list,
    rule_list
):

    return {

        "new_uri": sorted(
            list(set(uri_list))
        ),

        "new_rule": sorted(
            list(set(rule_list))
        )
    }
