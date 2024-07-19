from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Initialize model
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL = os.getenv("SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")

def completion_gpt( prompt, max_tokens=2048, temperature=0.7, top_p=0.95, n=1, apikey=OPENAI_API_KEY):
    gpt_client = AzureOpenAI(
        api_key =  OPENAI_API_KEY,
        api_version = OPENAI_API_VERSION,
        azure_endpoint = OPENAI_API_BASE
    )

    output = gpt_client.chat.completions.create(
        model= OPENAI_DEPLOYMENT_NAME,
        temperature=temperature,
        messages=prompt,
        top_p=0.95,
        max_tokens=max_tokens
    )
  
    return output.choices[0].message.content

def generate_response(message):
    return completion_gpt([{"role": "user", "content": f"""
    Respond to this user's message with a helpful and respecting tone:
    "{message}"
    """}])


# Routings
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/test')
def hello():
    return "test"

@app.route('/whatsapp', methods=['GET','POST'])
def whatsapp():
    response = MessagingResponse()

    # sender = request.form.get('From')  # Sender's phone number
    message_body = request.form.get('Body')  # User's message

    response.message(generate_response(message_body)) # template

    return str(response)

if __name__ == '__main__':
    app.run(port=8080)