from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils.model import generate_response

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