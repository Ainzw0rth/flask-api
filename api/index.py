from flask import Flask, request
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import requests

# Initialize model
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL = os.getenv("SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")

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
def test():
    return "test"

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return str(challenge)
    return 'Invalid verification token', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        app.logger.info(f"Received data: {data}")

        phone_number = None
        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change and 'messages' in change['value']:
                            for message in change['value']['messages']:
                                phone_number = message.get('from')
                                app.logger.info(f"User phone number: {phone_number}")
                                break
                        if phone_number:
                            break
                if phone_number:
                    break
        
        message_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        app.logger.info(f"Received message: {message_body}")

        response_message = generate_response(message_body)
        app.logger.info(f"Generated response: {response_message}")

        payload = {
            'messaging_product': 'whatsapp',
            'to': phone_number,
            'text': {
                'body': response_message
            }
        }

        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        api_response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        app.logger.info(f"API response: {api_response.status_code} - {api_response.text}")

        if api_response.status_code == 200:
            return "Message sent successfully", 200
        else:
            return "Failed to send message", 500
    except Exception as e:
        app.logger.error(f"Exception: {str(e)}")
        return "Server error", 500

if __name__ == '__main__':
    app.run(port=8080)