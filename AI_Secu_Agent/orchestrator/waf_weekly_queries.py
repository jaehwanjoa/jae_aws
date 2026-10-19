class WAFWeeklyQueries:

    @classmethod
    def get_rule_summary_query(
        cls,
        table_name,
        previous_start,
        previous_end,
        current_start,
        current_end
    ):
    
        return f"""
    SELECT
    
        period,
    
        terminatingruleid AS rule_id,
    
        count(*) AS hit_count,
    
        count_if(
            action = 'BLOCK'
        ) AS block_count,
    
        count_if(
            action = 'COUNT'
        ) AS count_count
    
    FROM (
    
        SELECT
    
            CASE
    
                WHEN DATE(
                    from_unixtime(timestamp / 1000)
                )
                BETWEEN DATE '{previous_start}'
                AND DATE '{previous_end}'
                THEN 'PREVIOUS'
    
                ELSE 'CURRENT'
    
            END AS period,
    
            terminatingruleid,
    
            action
    
        FROM {table_name}
    
        WHERE DATE(
            from_unixtime(timestamp / 1000)
        )
        BETWEEN DATE '{previous_start}'
        AND DATE '{current_end}'
    
    )
    
    GROUP BY 1,2
    """
