import json
import psycopg2
import boto3
import os

db_name = os.environ['DB_NAME']
PASSWORD = os.environ['PASSWORD']
RDS_HOST = os.environ['RDS_HOST']
RDS_PORT = os.environ['RDS_PORT']
user_name = os.environ['USER_NAME']

aws_pg_params = {
    "host": RDS_HOST,
    "database": "postgres",
    "user": "postgres",
    "password": PASSWORD,
    "port": RDS_PORT
}

connection_success = 1

try:
    conn = psycopg2.connect(**aws_pg_params)
except psycopg2.Error as e:
    print(e)
    connection_success = 0

def lambda_handler(event, context):
    
    recieved_name = event['queryStringParameters']['brand_name']
    query = f'''
    SELECT * 
    FROM brand as br
    WHERE br.name = '{recieved_name}';
    '''
    cur = conn.cursor()
    cur.execute(query)
    # Get list of tuples for all fields
    
    response_list = cur.fetchall()
    return {
        'statusCode': 200,
        'body': json.dumps({'brand_name':response_list[0][1], 'brand_score':response_list[0][2]})
    }

