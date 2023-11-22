import os
import streamlit as st
from openai import OpenAI
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

# Check if the API key is available
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable in the .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Function to encode the image
def encode_image(uploaded_image):
    image_bytes = uploaded_image.read()
    return base64.b64encode(image_bytes).decode('utf-8')

# Streamlit app
st.title("OpenAI Image Recognizer")

# Sidebar to set the message
st.sidebar.header("Set Message")
user_message = st.sidebar.text_input("User Message", "What’s in this image?")

# Option to upload an image or enter image URL
st.sidebar.header("Upload Images or Enter Image URLs")

num_images = st.sidebar.number_input("Number of images", 1, 10, 1)

image_list = []

for i in range(num_images):
    st.sidebar.write(f"Image {i + 1}")
    upload_option = st.sidebar.selectbox(
        f"Choose an option for Image {i + 1}",
        ["Upload an image", "Enter image URL"]
    )

    if upload_option == "Upload an image":
        uploaded_image = st.sidebar.file_uploader(f"Upload Image {i + 1}", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            base64_image = encode_image(uploaded_image)
            image_list.append({"type": "image", "data": base64_image})
    elif upload_option == "Enter image URL":
        image_url = st.sidebar.text_input(f"Enter URL for Image {i + 1}")
        if image_url:
            image_list.append({"type": "image_url", "data": image_url})

if st.sidebar.button("Generate Response"):
    messages = [{"type": "text", "text": user_message}] + image_list
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": messages
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=payload)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        st.subheader("Chatbot Response")
        st.write(content)
    else:
        st.subheader("Error")
        st.write("Failed to get a response from the chatbot. Please check your input.")
