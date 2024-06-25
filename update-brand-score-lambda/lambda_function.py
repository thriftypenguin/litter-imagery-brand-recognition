import json
import psycopg2
import boto3
import os

PASSWORD = os.environ['PASSWORD']
RDS_HOST = os.environ['RDS_HOST']
RDS_PORT = os.environ['RDS_PORT']

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
    print(f'connection_success: {connection_success}')
    query = f'''
    UPDATE brand AS b
    SET score = temp_table.score
    FROM (
    	SELECT brand_id AS brand_id, ROUND (SUM(qty)*100.0/(SELECT SUM(qty) FROM brand_image), 5) AS score
    	FROM brand_image
    	GROUP BY brand_id) AS temp_table
    WHERE temp_table.brand_id = b.brand_id
    '''
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

    return {
        'statusCode': 200
    }
