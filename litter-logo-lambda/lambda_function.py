import json
#import psycopg2

def lambda_handler(event, context):
    brands_dict = {'1':'CocaCola', '2':'Corona', '3':'Budweiser', '4':'Miller', '5':'LoveIs'}
    scores_dict = {'1':1, '2':2, '3':3, '4':4, '5':5}
    brandID = event['queryStringParameters']['brandID']
    return {
        'statusCode': 200,
        'body': json.dumps({'brand_name':brands_dict[brandID], 'brand_score':scores_dict[brandID]})
    }

