import streamlit as st
import requests
import json
from PIL import Image
from io import BytesIO


lambda_endpoint="https://8t4pyjhqx0.execute-api.us-west-2.amazonaws.com/default/DEBI_InvokingSageMaker"

def request_lambda(data):
 return requests.post(lambda_endpoint,json =data).text


# from transformers import pipeline

# Load a text summarization pipeline from Hugging Face Transformers
# summarizer = pipeline("summarization")

# Function to summarize text
def summarize_text(text):
    # summary = summarizer(text, max_length=50, min_length=25, do_sample=False)
    # return summary[0]['summary_text']
    return request_lambda(text)

# Function to fetch an image from an API
def fetch_image(url="https://via.placeholder.com/300"):
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to fetch image from the API.")
        return None
st.set_page_config(layout="wide")
st.title("Automatic Radiology Impression Report Generator")

# Create two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Scan Image")
    image = fetch_image("https://th.bing.com/th/id/OIP.w-R4SATia_WHKevgHqFdBQHaJC?rs=1&pid=ImgDetMain")  # Replace the URL with the actual API endpoint
    if image:
        st.image(image, caption="Brain Scan Image from API", use_column_width=True)

with col2:
    # Text input for summarization
    st.header("Finding")
    input_text = st.text_area("Enter Finding", key="input_area")
    
    # Button to trigger summarization
    if st.button("generate impressions", key="generate_btn"):
        if input_text.strip():
            summarized_text = summarize_text(input_text)
            st.text_area("generated impressions:", summarized_text)
            # Clear the input field
            st.session_state.input_area = ""
        else:
            st.error("Please enter some text to generate impressions.")
