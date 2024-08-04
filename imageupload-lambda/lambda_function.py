import boto3, cv2, random, base64, json
import numpy as np

def str_to_array(encoded_str):
    aux_path = '/tmp/tmp.png'
    with open(aux_path, 'wb') as f:
        f.write(base64.b64decode(encoded_str))
        f.close
    return cv2.imread(aux_path)

def array_to_str(im_array):
    aux_path = '/tmp/tmp.png'
    cv2.imwrite(aux_path, im_array)
    
    with open(aux_path, 'rb') as f:
        encoded_im = base64.b64encode(f.read())
        f.close
    return encoded_im.decode('utf-8')

def lambda_handler(event, context):
    ENDPOINT_NAME = 'yolov8-pytorch-2024-07-18-21-09-58-005126'            
    
    # Read the image into a numpy  array
    #orig_image = cv2.imread('test_image.jpg')
    orig_image = str_to_array(event['body'])
    
    # Calculate the parameters for image resizing
    image_height, image_width, _ = orig_image.shape
    model_height, model_width = 640, 640
    x_ratio = image_width/model_width
    y_ratio = image_height/model_height
    
    # Resize the image as numpy array
    resized_image = cv2.resize(orig_image, (model_height, model_width))
    # Conver the array into jpeg
    resized_jpeg = cv2.imencode('.jpg', resized_image)[1]
    # Serialize the jpg using base 64
    payload = base64.b64encode(resized_jpeg)
    
    runtime= boto3.client('runtime.sagemaker')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                            ContentType='text/csv',
                                            Body=payload)
    response_body = response['Body'].read()
    result = json.loads(response_body.decode('ascii'))

    if 'boxes' in result:
        for idx,(x1,y1,x2,y2,conf,lbl) in enumerate(result['boxes']):
            # Draw Bounding Boxes
            x1, x2 = int(x_ratio*x1), int(x_ratio*x2)
            y1, y2 = int(y_ratio*y1), int(y_ratio*y2)
            color = (random.randint(10,255), random.randint(10,255), random.randint(10,255))
            cv2.rectangle(orig_image, (x1,y1), (x2,y2), color, 4)
            cv2.putText(orig_image, f"Class: {int(lbl)}", (x1,y1-40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            cv2.putText(orig_image, f"Conf: {int(conf*100)}", (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            if 'masks' in result:
                # Draw Masks
                mask = cv2.resize(np.asarray(result['masks'][idx]), dsize=(image_width, image_height), interpolation=cv2.INTER_CUBIC)
                for c in range(3):
                    orig_image[:,:,c] = np.where(mask>0.5, orig_image[:,:,c]*(0.5)+0.5*color[c], orig_image[:,:,c])
    
    im_to_return = array_to_str(orig_image)
            
    return {
        'statusCode': 200,
        'body': im_to_return,
        'isBase64Encoded': True,
        'headers': {'content-type':'image/png'}
    }