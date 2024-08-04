from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import psycopg2
import im_utils
import db_ops
import pandas as pd

import glob
from datetime import datetime
import time

from keras.saving import load_model

SIZE = 254 #Size of the images this model will deal with
IMDIM = 3
IMG_SIZE = (SIZE, SIZE)            # Define the image size
INPUT_SHAPE = (*IMG_SIZE, IMDIM)       # Define the input_shape

RAND_SEED  = 42 # The answer to the ultimate question of life, the universe, and everything

query = f'''
SELECT b.box_id AS box_id
    , b.box_pic_uri AS box_uri
	, i.image_id as image_id
	, br.brand_id as brand_id 
	, br.brand_name as brand_name 
FROM box AS b 
	LEFT JOIN brand as br
		ON b.brand_id = br.brand_id 
	LEFT JOIN image as i
		ON i.image_id = b.image_id
ORDER BY i.image_id	;
'''
box_df = db_ops.select_to_pandas(query, True, True)
box_df = box_df.sort_values(by = 'box_id')

# load model
model = load_model("./B0_custaug_model/B0_custaug_model.keras")

# load dataframe that correlated model index and database ID
id_idx_df = pd.read_csv('brand_ids_idx.csv', sep = '\t')

for i in range(len(box_df)):
    try:
        print(f'---------{i}---------')
        box_uri = box_df['box_uri'].iloc[i].split('.')[0] + '.jpg'
        # print(f"box_uri: {box_uri}")
        box_id = box_df['box_id'].iloc[i]
        tmp_im_folder = '/home/ubuntu/temp-images'
        file_name = box_uri.split('/')[-1]
        # print(f"file_name: {file_name}")
        local_file_path = os.path.join(tmp_im_folder, file_name)
        # print(f"local_file_path: {local_file_path}")
        
        #Copy image from S3 to local folder
        os.system(f"aws s3 cp {box_uri} {tmp_im_folder}") 
        
        # Read the image
        img = cv2.imread(local_file_path, cv2.IMREAD_COLOR)
        
        #Resize the image so that the smaller side is the right size
        h, w = img.shape[:2]
        if h > w:
            width = SIZE
            dim = (width, int(SIZE* h / w)) 
        else:
            height = SIZE
            dim = (int(SIZE* w/h), height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        
        # Crop the image to a square of the target size
        h, w = img.shape[:2]
        if h > w:
            img = img[(h-w)//2:(h-w)//2 + w, :, :]
        else:
            img = img[:, (w-h)//2:(w-h)//2 + h, :]
        
        # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Run the model inference on the test images
        y_pred = model.predict(img.reshape(1,254,254,3))
        y_pred_dense = np.argmax(y_pred, axis=1)
        result = id_idx_df[id_idx_df['idx'] == y_pred_dense[0]]
        
        # Update brand id for the box we just analyzed
        query = f'''
        UPDATE box
        SET brand_id = {int(result['brand_id'].iloc[0])}
        WHERE box_id = {box_id}
        '''
        db_ops.run_single_query(query)
        os.system(f"find ~/temp-images/ -maxdepth 2 -type f -delete")
    except Exception as e:
        print(e)