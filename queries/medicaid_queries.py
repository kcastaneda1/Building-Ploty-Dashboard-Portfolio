import duckdb as db
import pandas as pd 

DB_PATH = "data/medicaid.duckdb"


def get_connection():
    return db.connect(DB_PATH, read_only= True)

def get_medicaid_raw():
    con = get_connection()

    try:
        query = """
        SELECT * FROM medicaid_raw
        """

        return con.execute(query).df()
    finally:
        con.close()

# Queries that will populate CMS dashboard


def get_enrollment_trend(filters):
    con= get_connection()

    try:
        query = """
        SELECT 
            reporting_date,
            state_name,
            total_medicaid_chip_enrollment,
            total_medicaid_enrollment,
            total_chip_enrollment 
        FROM vw_enrollment_trend
        WHERE 1=1
        """

        params = []
        states = filters['state']
        cols = ['reporting_date','state_name', 'total_medicaid_chip_enrollment','total_medicaid_enrollment', 'total_chip_enrollment']
        empty_df = pd.DataFrame(columns= cols)

        # if all filters are unselected return "empty data - No data"
        if not states:
            return empty_df

        # normalize data if a state is selected to a list ['state 1] not a string like 'string 1'
        # if multiple states are selected then list has to be ['state 1', 'state 2']
        else:
            if isinstance(states,str):
                states = [states]

            available_states = con.execute(
                "SELECT DISTINCT state_name FROM vw_enrollment_trend"
            ).fetchdf()['state_name'].tolist()

            # set GLOBAL FILTERS
            # if all states are selected then show top 10
            # else show selected states
            if set(states) == set(available_states):
                query += """
                AND state_name IN (
                    SELECT
                        state_name 
                    FROM vw_enrollment_trend 
                    WHERE reporting_date BETWEEN ? AND ?
                    GROUP BY state_name
                    ORDER BY max(total_medicaid_chip_enrollment) DESC
                    LIMIT 10
                )
                """
                params.extend([
                    filters['start_date'],
                    filters['end_date']
                ])
            else:
                query += f" AND state_name IN ({','.join(['?'] * len(states))})"
                params.extend(states)

        query += """
        AND reporting_date BETWEEN ? AND ?
        ORDER BY reporting_date, state_name
        """    

        params.extend([
            filters['start_date'],
            filters['end_date']
        ])

        return con.execute(query,params).df()
    finally:
        con.close()

def get_state_enrollment_growth(filters):
    con = get_connection()

    try:
        query = """
        SELECT 
            state_abbreviation,
            state_name,
            reporting_date,
            total_medicaid_and_chip_enrollment,
            previous_enrollment,
            enrollment_change,
            enrollment_pct_change 
        FROM vw_state_enrollment_growth
        WHERE 1 = 1
        """

        params = []
        states = filters['state']
        cols = ['state_abbreviation','state_name','reporting_date','total_medicaid_and_chip_enrollment','previous_enrollment',
                'enrollment_change','enrollment_pct_change']
        empty_df = pd.DataFrame(columns= cols)

        if not states:
            return empty_df
        else:
            if isinstance(states,str):
                states=[states]
            available_states = con.execute("SELECT DISTINCT state_name FROM vw_state_enrollment_growth"
                                           ).fetchdf()['state_name'].tolist()

            if set(states) == set(available_states):
                query += """
                AND state_name in (
                    SELECT 
                        state_name 
                    FROM vw_state_enrollment_growth
                    WHERE reporting_date BETWEEN ? AND ? 
                    GROUP BY state_name 
                    ORDER BY max(enrollment_change) DESC
                    LIMIT 10    
                    )
                """
                params.extend([
                    filters['start_date'],
                    filters['end_date']
                ])
            else:
                query += f" AND state_name IN ({','.join(['?'] * len(states))})"
                params.extend(states)
        query += """
        AND reporting_date BETWEEN ? AND ? 
        ORDER BY reporting_date, state_name 
        """
        params.extend([
            filters['start_date'],
            filters['end_date']
        ])

        return con.execute(query,params).df()
    finally:
        con.close()

def get_call_center_trend(filters):
    con = get_connection()
    try:
        query = """
        SELECT 
            date_trunc('month',reporting_date) as reporting_date, 
            state_name,
            sum(total_call_center_volume_number_of_calls) as total_call_volume,
            avg(average_call_center_wait_time_minutes) as avg_wait_time,
            avg(average_call_center_abandonment_rate) as avg_abandoment_rate 
        FROM  medicaid_final
        WHERE 1 = 1 
        """
        params = []
        states = filters['state']
        cols = ['reporting_date','state_name','total_call_volume','avg_wait_time','avg_abandonmnet_rate']
        empty_df = pd.DataFrame(columns= cols)

        if not states:
            return empty_df
        else:
            if isinstance(states, str):
                states = [states]
            available_states = con.execute(
                "SELECT DISTINCT state_name from medicaid_final"
            ).fetchdf()['state_name'].tolist()

            if set(states) == set(available_states):
                query += """
                AND state_name IN (
                    SELECT 
                        state_name,
                    FROM medicaid_final 
                    WHERE reporting_date BETWEEN ? AND ? 
                    GROUP BY state_name 
                    ORDER BY max(total_call_center_volume_number_of_calls) DEC
                    LIMIT 10
                    )
                """
                params.extend([
                    filters['start_date'],
                    filters['end_date']
                ])
            else:
                placeholders = ",".join(["?"] * len(states))
                query += f"""
                AND state_name in ({placeholders})
                """                        
                params.extend(states)

        params += """
        AND reporting_date BETWEEN ? AND ?
        GROUP BY reporting_date, state_name 
        ORDER BY reporting_date, state_name
        """

        params.extend([
            filters['start_date'],
            filters['end_date']
        ])

        return con.execute(query,params).df()
    finally:
        con.close()

def get_operational_performance(filters):
    # this will create a table, does not need global filter logic 
    con = get_connection()
    try:
        query =  """
            SELECT 
                date_trunc('month',reporting_date) as reporting_date,
                state_name,
                sum(total_medicaid_and_chip_enrollment) as total_enrollment,
                sum(total_call_center_volume_number_of_calls) AS total_call_volume,
                avg(average_call_center_wait_time_minutes) AS avg_wait_time,
                avg(average_call_center_abandonment_rate) AS avg_abandonment_rate,
                sum(total_medicaid_and_chip_determinations_processed_in_less_th_1e84) AS processed_less_than_24_hours,
                sum(total_medicaid_and_chip_determinations_processed_between_24_756e) AS processed_24_hours_to_7_days,
                sum(total_medicaid_and_chip_determinations_processed_between_8__a7a5) AS processed_8_to_30_days,
                SUM(total_medicaid_and_chip_determinations_processed_between_31_a42c) AS processed_31_to_45_days,
                SUM(total_medicaid_and_chip_determinations_processed_in_more_th_a7ec) AS processed_more_than_45_days
            FROM medicaid_final
            WHERE 1 = 1
            """
        params = []
        states = filters['state']
        cols = ['reporting_date','state_name','total_enrollment','total_call_volume','avg_wait_time','avg_abandonment_rate',
                  'processed_less_than_24_hours','processed_24_hours_to_7_days','processed_8_to_30_days', 'processed_31_to_45_days',
                  'processed_more_than_45_days']
        empty_df = pd.DataFrame(columns=cols)

        if not states:
            return empty_df
        else:
            if isinstance(states,str):
                states = [states]
            query += f" AND state_name in ({','.join(['?'] * len(states))})"
            params.extend(states)

        query +="""
                AND reporting_date BETWEEN ? AND ?
                GROUP BY reporting_date, state_name
                ORDER BY reporting_date, state_name 
                """   
        params.extend([
            filters['start_date'],
            filters['end_date']
        ])
        return con.execute(query,params).df()
    finally:
        con.close()

    
