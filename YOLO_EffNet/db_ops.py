import json
import numpy as np
import pandas as pd
import psycopg2
import csv
import sys


def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn


def connect_db():
    with open('login_config_awsrds.json') as config_file:
        config = json.load(config_file)

    class Config:
        PASSWORD = config.get('PASSWORD')
        RDS_HOST = config.get('RDS_HOST')
        RDS_PORT = config.get("RDS_PORT")

        aws_pg_params = {
            "host": RDS_HOST,
            "database": "postgres",
            "user": "postgres",
            "password": PASSWORD,
            "port": RDS_PORT
        }
    return connect(Config.aws_pg_params)


connection = connect_db()
cursor = connection.cursor()


# function to run a select query and return rows in a pandas dataframe
# pandas puts all numeric values from postgres to float
# if it will fit in an integer, change it to integer

def select_to_pandas(query, rollback_before_flag, rollback_after_flag):
    """
    function to run a select query and return rows in a pandas dataframe
    """
    cursor = connection.cursor()
    if rollback_before_flag:
        connection.rollback()
    df = pd.read_sql_query(query, connection)
    if rollback_after_flag:
        connection.rollback()

    # fix the float columns that really should be integers
    '''
    for column in df:
        if df[column].dtype == "float64":
            fraction_flag = False
            for value in df[column].values:
                if not np.isnan(value):
                    if value - math.floor(value) != 0:
                        fraction_flag = True
            if not fraction_flag:
                df[column] = df[column].astype('Int64')
    '''
    cursor.close()
    return (df)


def add_df(df, table_name):
    """
    Add a panda df to an existing table in database
    Assume that df index does not matter
    """
    connection.rollback()
    seed = 'INSERT INTO ' + table_name + ' ('
    for val in df.columns:
        seed = seed + val+","
    seed = seed[:-1]+') VALUES ('

    # Add the values to the query
    for i in df.index:
        query = seed
        for val in df.iloc[i, :]:
            query = query + "'"+str(val)+"',"
        query = query[:-1]+');'
        print(query)
        cursor.execute(query)
        connection.commit()


def add_csv(file_name, table_name):
    """
    Add a csv file to an existing table in database
    """

    connection.rollback()

    with open(file_name) as f:
        reader = csv.reader(f, delimiter=",")

        # Construct the header part of the query
        header = next(reader, None)
        seed = 'INSERT INTO ' + table_name + ' ('
        for val in header:
            seed = seed + val+","
        seed = seed[:-1]+') VALUES ('

        # Add the values to the query
        for line in reader:
            query = seed
            for val in line:
                if len(val) < 1:
                    val = "NaN"
                query = query + "'"+val+"',"
            query = query[:-1]+');'
            print(query)
            cursor.execute(query)
            connection.commit()


def execute_many(df, table):
    """
    Using db_ops.cursor.executemany() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    # SQL quert to execute
    query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % (table, cols)
    try:
        cursor = connection.cursor()
        cursor.executemany(query, tuples)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        connection.rollback()
        cursor.close()
        return 1
    print("execute_many() done")
    cursor.close()


def run_single_query(q: str):
    connection.rollback()
    cursor.execute(q)
    connection.commit()
