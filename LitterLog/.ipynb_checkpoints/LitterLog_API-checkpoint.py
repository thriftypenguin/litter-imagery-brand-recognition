import streamlit as st
import numpy as np
import cv2
import requests
from PIL import Image
from io import BytesIO

# CSS styling (Keep the entire CSS block from the reference code)
css = """
<style>
body {
    font-family: Arial, sans-serif;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    text-align: center;
}
h1, h2 {
    color: #314b81;
}
h1 {
    font-size: 2.5em;
    margin-bottom: 20px;
}
h2 {
    font-size: 1.8em;
    margin-top: 20px;
    margin-bottom: 15px;
}
p {
    margin-bottom: 10px;
}
.container {
    width: 60%;
    height: 50%;
    margin: 10px auto;
}
.image-container img {
    width: 100%;
    height: 50%;
    object-fit: cover;
}
.stButton > button {
    background-color: #314b81;
    color: white;
    font-weight: bold;
    border: none;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: block;
    font-size: 26px;
    margin: 20px auto;
    cursor: pointer;
    border-radius: 4px;
}
.footer {
    margin-top: 30px;
    padding-top: 15px;
    border-top: 1px solid #ddd;
}
/* Center-align Streamlit components */
.stTextInput, .stFileUploader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.stTextInput > div, .stFileUploader > div {
    width: 100%;
    max-width: 100%;
    display: flex;
    justify-content: center;
}
/* Ensure all text is centered */
.stTextInput > label, .stFileUploader > label {
    text-align: center;
    width: 100%;
}
/* Center the file uploader button */
.stFileUploader > div > div {
    display: flex;
    justify-content: center;
}
/* Adjust the file uploader input */
.stFileUploader input[type="file"] {
    width: 100%;
    text-align: center;
}
/* Center success and error messages */
.stSuccess, .stError {
    text-align: center;
}
</style>
"""
def resize_to_size(img, size):
    '''
    Resizes the image, so that the shorter side is equal to given size,
    keeps the aspect ratio.
    :param img: The image to be resized.
    :param size: The size to resize the image to.
    :return: The resized image.
    '''
    h, w = img.shape[:2]
    if h > w:
        width = size
        dim = (width, int(size * h / w)) 
    else:
        height = size
        dim = (int(size * w/h), height)
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return img

st.set_page_config(page_title="LitterLog", layout="wide")
st.markdown(css, unsafe_allow_html=True)

# API endpoints
API_ENDPOINT_BOXES = 'https://ni3gvh9foi.execute-api.us-east-1.amazonaws.com/boxes'
API_ENDPOINT_IMAGE = 'https://ni3gvh9foi.execute-api.us-east-1.amazonaws.com/image'

st.title('Welcome to Litter Log')
st.write('Thank you for your contribution to help us change the world')
st.write('Every photo you share will help the community become more knowledgeable about brand pollution')

# Display the image (you'll need to provide this image or remove this section)
st.markdown('<div class="image-container">', unsafe_allow_html=True)
st.image('litter_log_photo.png', use_column_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Create two columns
left_column, right_column = st.columns(2)

# Left column for file upload
with left_column:
    st.subheader("Upload Your Image")
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

# Right column for displaying the processed image and results
with right_column:
    st.subheader("Processed Image and Results")
    st.text_area('Returning Image', 'Once you upload the photos, a new brand litter score will be generated based on the updated information. You can view the litter scores of the brands you care about while shopping on Amazon. Download the Chrome extension here.')
    
    if uploaded_file is not None:
        # Read the uploaded file
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        # Resize the image to 640 on the shorter side
        img_resized = resize_to_size(img, 640)
        
        # Convert the resized image to PNG format
        is_success, im_buf_arr = cv2.imencode(".png", img_resized)
        byte_im = im_buf_arr.tobytes()
        
        with st.spinner('Processing image... Please wait.'):
            try:
                # Send the image to get bounding boxes
                r_boxes = requests.post(url=API_ENDPOINT_BOXES, data=byte_im, 
                                        headers={'Content-Type': 'application/octet-stream'})
                # Send the image to get processed image
                r_image = requests.post(url=API_ENDPOINT_IMAGE, data=byte_im, 
                                        headers={'Content-Type': 'application/octet-stream'})
                
                if r_boxes.status_code == 200 and r_image.status_code == 200:
                    st.success(f"Image processed successfully!")
                    
                    # Display the processed image
                    img_processed = Image.open(BytesIO(r_image.content))
                    st.image(img_processed, caption='Processed Image with Bounding Boxes', use_column_width=True)
                    
                else:
                    st.error(f"Failed to process image. Status codes: Boxes {r_boxes.status_code}, Image {r_image.status_code}")
                    st.error(f"Error messages: Boxes {r_boxes.text}, Image {r_image.text}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while sending the file: {e}")

# Footer
st.markdown('<div class="footer">Contact Us</div>', unsafe_allow_html=True)