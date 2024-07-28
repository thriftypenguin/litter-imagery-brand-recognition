from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
from ultralytics import YOLO
import psycopg2
import im_utils
import db_ops
import pandas as pd

import boto3
s3_client = boto3.client('s3')

# Get a df of unprocesed images
query = f'''
SELECT DISTINCT ON (i.image_id)
	 i.s3_uri AS uri
	, i.image_id as image_id
	, b.brand_id as brand_id 
	, ci.cat_id as cat_id
FROM image AS i 
	LEFT JOIN brand_image AS bi
		ON i.image_id = bi.image_id
	LEFT JOIN brand as b
		ON b.brand_id = bi.brand_id 
	LEFT JOIN category_image as ci
		ON i.image_id = ci.image_id
ORDER BY i.image_id	;'''
image_uri = db_ops.select_to_pandas(query, True, True)
image_uri['brand_id'] = image_uri['brand_id'].fillna(value = 111).astype(int)
image_uri['cat_id'] = image_uri['cat_id'].fillna(value = 20).astype(int)
image_uri['file'] = image_uri['uri'].apply(lambda x: x.split('/')[-1].split('.')[0])

# Get a df of brand names
query = f'''
SELECT *
FROM brand'''
brand_df = db_ops.select_to_pandas(query, True, True)

model = YOLO('/home/ubuntu/box_model/logo-yolo.pt')

for i in range(len(image_uri)):
    print('-'*30)
    try:
        # Get the file names and uris
        original_im_uri = image_uri['uri'].iloc[i]
        image_id = image_uri['image_id'].iloc[i]
        tmp_im_folder = '/home/ubuntu/temp-images'
        im_file = original_im_uri.split('/')[-1]
        scaled_im_uri = original_im_uri.replace('-pics-s3', '-processed-s3/scaled').split('.')[0] + '.jpg'
        scaled_im_local_path = os.path.join(tmp_im_folder, 'scaled', im_file.split('.')[0] + '.jpg')
        boxes_s3_path = scaled_im_uri.replace('/scaled', '/boxes_mult')
        boxes_s3_path = '/'.join(boxes_s3_path.split('/')[:-1]) + '/'
        
        # Download the image from olm bucket, scale it and write to the local folder
        os.system(f"aws s3 cp {original_im_uri} {tmp_im_folder}") 

        image_original = cv2.imread(tmp_im_folder+'/'+im_file)
        image_scaled = im_utils.ScaleImage(image_original, width = 640)
        cv2.imwrite(scaled_im_local_path, image_scaled)

        # Run YOLO inference
        results = model(image_scaled)
            
        boxes_df = pd.DataFrame(columns = ['image_id', 'brand_id', 'cat_id', 'xmin_coord', 'ymin_coord', 'xmax_coord', 'ymax_coord', 'box_pic_uri','conf'])
        w_ratio = image_original.shape[1]/image_scaled.shape[1]
        h_ratio = image_original.shape[0]/image_scaled.shape[0]
        for i in range(len(results[0].boxes.cls)):# Iterate over each box   
            # Get the coordinates of the box on the original image
            xmin, ymin, xmax, ymax = map(int, results[0].boxes.xyxy[i]) 
            xmin = int(xmin * w_ratio)
            xmax = int(xmax * w_ratio)
            ymin = int(ymin * h_ratio)
            ymax = int(ymax * h_ratio)
            postfix = f"-{xmin}-{ymin}-{xmax}-{ymax}"
            box_file = im_file.split('.')[0]+postfix+'.jpg'
            
            # Get the section of the original image that is in the box
            box_im = image_original[ymin:ymax, xmin:xmax,:]
            # Save the box locally as an individual file
            cv2.imwrite(tmp_im_folder + '/scaled/' + box_file, box_im)

            # Add line with the box data to the df for db insertion
            idx = len(boxes_df)
            brand_name = results[0].names[int(results[0].boxes.cls[i])]
            boxes_df.loc[idx, 'brand_id'] = brand_df[brand_df['brand_name'] == brand_name]['brand_id'].iloc[0]
            boxes_df.loc[idx, 'cat_id'] = 0
            boxes_df.loc[idx, 'xmin_coord'] = xmin
            boxes_df.loc[idx, 'ymin_coord'] = ymin
            boxes_df.loc[idx, 'xmax_coord'] = xmax
            boxes_df.loc[idx, 'ymax_coord'] = ymax
            boxes_df.loc[idx, 'image_id']= image_id
            boxes_df.loc[idx, 'box_pic_uri']= boxes_s3_path + box_file
            boxes_df.loc[idx, 'conf']= float(results[0].boxes.conf[i])
        
            # Upload the box file to processed s3 bucket
            os.system(f"aws s3 cp {tmp_im_folder + '/scaled/' + box_file} {boxes_s3_path}") 

        #Delete old boxes for this image
        query = f'''
        DELETE FROM box
        WHERE image_id = {image_id}
        '''
        db_ops.run_single_query(query)
        #Update box table with the new boxes
        db_ops.add_df(boxes_df, "box")

        #Clean up temp folders
        os.system(f"find ~/temp-images/ -maxdepth 2 -type f -delete")
    except Exception as e:
        print(e)