import streamlit as st
import numpy as np
from PIL import Image
from main import donut

# potentially explore st.data_editor

document = st.camera_input(label = "Take a Photo", help = "Take a photo of a document")

uploaded_document = st.file_uploader(label = "Upload a Photo", type = ["jpg", "jpeg", "png"], accept_multiple_files = False, help = "Upload a photo document")

# if document is not None:
#     img = Image.open(document)
#     img_array = np.array(img)
#     st.image(img)
#     st.write(img_array.shape)
    

#     # To change the image to other formats: visit this link https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input

# if uploaded_document is not None:
#     img = Image.open(uploaded_document)
#     img_array = np.array(img)
#     st.image(img)
#     st.write(img_array.shape)
#     with st.spinner("Running inference..."):
#         run_donut = donut.run_inference(img, image_name="testing.jpg")
#     st.success("Inference complete!")

img = None
if document is not None:
    img = Image.open(document)
elif uploaded_document is not None:
    img = Image.open(uploaded_document)

# If we have an image, show it and the Extract button
if img is not None:
    img_array = np.array(img)
    st.image(img, caption="Input Image")
    st.write("Image shape:", img_array.shape)

    if st.button("Extract"):
        with st.spinner("Running inference..."):
            run_donut = donut.run_inference(img, image_name="testing.jpg")
            st.write("Extracted result:", run_donut)
        st.success("Inference complete!")