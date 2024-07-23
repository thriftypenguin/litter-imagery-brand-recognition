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
    
    # Get the data from brand table
    # Query the database
    query = f'''
    SELECT * 
    FROM brand as br
    WHERE br.brand_name = '{recieved_name.lower() }';
    '''
    cur = conn.cursor()
    cur.execute(query)
    
    # Format response    
    response_list = cur.fetchall()
    brand_name = response_list[0][1]

    # Get the total number of all boxes
    # Query the database
    query = f'''
    SELECT count(box_id) 
    FROM box
    '''
    cur = conn.cursor()
    cur.execute(query)
    
    # Format response    
    response_list = cur.fetchall()
    total_im_count = int(response_list[0][0])
    
    # Get the number of boxes for this brand
    # Query the database
    query = f'''
    UPDATE brand AS b
    SET brand_im_count = temp_table.im_count
    FROM ( SELECT brand_id, count(box_id) as im_count
           FROM box
           GROUP BY brand_id) AS temp_table
    WHERE temp_table.brand_id = b.brand_id;
    
    SELECT brand_im_count, brand_rank
    FROM
    (SELECT brand_name, brand_im_count
            , rank() OVER (ORDER BY brand_im_count DESC) as brand_rank
    FROM brand WHERE brand_im_count > 0) as tbl
    WHERE tbl.brand_name = '{recieved_name.lower()}'
    '''
    cur = conn.cursor()
    cur.execute(query)
    
    # Format response    
    response_list = cur.fetchall()
    print(response_list)
    brand_im_count = int(response_list[0][0])
    brand_rank = int(response_list[0][1])
    
    conf = f"95% confident from {int(0.75*brand_im_count)} to {int(1.25*brand_im_count)}"
    return {
        'statusCode': 200,
        'body': json.dumps({'brand_name':brand_name,
                            'brand_rank':brand_rank,
                            'brand_im_count':brand_im_count,
                            'tot_im_count': total_im_count,
                            'confidence': conf
                            })
    }

