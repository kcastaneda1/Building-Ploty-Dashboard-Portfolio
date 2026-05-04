import duckdb


def get_connection_health():
    return duckdb.connect('./data/health_care_fraud.duckdb', read_only= True)


def init_db():
    con = get_connection_health()
    con.execute(
        '''
        CREATE VIEW IF NOT EXISTS healthcare_fraud_v as 
        SELECT 
            *,
            CASE WHEN Is_Fraud = 1 then 'Yes' else 'No' END AS Fraud_Category
        FROM healthcare_fraud
        '''
    )


#def get_data():
#    con = get_connection_health()
#    return con.execute("SELECT * FROM healthcare_fraud_v").df()


#def get_filtered_amount(providers = None, insurances = None, genders = None, frauds = None, start_date = None, end_date = None):
#    con = get_connection_health()
#    query = """
#            SELECT 
#            Claim_Submission_Date,
#            Provider_ID,
#            Insurance_Type,
#            Patient_Gender,
#            Fraud_Category,
#            sum(Claim_Amount) as Total_Claim_Amount,
#            sum(Approved_Amount) as Total_Approved_Amount
#            FROM healthcare_fraud_v
#               WHERE 1=1
#            """
    
#    params = []

#    if start_date and end_date:
#        query += " AND Claim_Submission_Date BETWEEN ? AND ? "
#        params.extend([start_date, end_date])

#    if providers:
#        query += f" AND Provider_ID IN ({','.join(['?'] * len(providers))})"
#        params.extend(providers)

#    if insurances:
#        query += f" AND Insurance_Type IN ({','.join(['?'] * len(insurances))})"
#        params.extend(insurances)

#    if genders:
#        query += f" AND Patient_Gender in ({','.join(['?'] * len(genders))})"
#        params.extend(genders)

#    if frauds:
#        query += f" AND Fraud_Category in ({','.join(['?'] * len(frauds))})"
#        params.extend(frauds)

#    query += """
#            GROUP BY Claim_Submission_Date, Provider_ID, Insurance_Type, Patient_Gender, Fraud_Category
#            ORDER BY Claim_Submission_Date
#            """
#    return con.execute(query, params).df()



#def get_insurance_options(providers = None):
#    con = get_connection_health()
#    query = """
#            SELECT DISTINCT Insurance_Type
#            FROM healthcare_fraud_v
#            WHERE 1=1
#            """
    
#    params = []

#    if providers:
#        query += f" AND Provider_ID IN ({','.join(['?'] * len(providers))})"
#        params.extend(providers)

#    return con.execute(query, params).df()



