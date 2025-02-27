import requests
from flask import Flask, request, jsonify
from llmproxy import generate
from db.py import add_feedback

app = Flask(__name__)

@app.route('/')
def hello_world():
   return jsonify({"text":'Hello from Koyeb - you reached the main page!'})

@app.route('/query', methods=['POST'])
def main():
    data = request.get_json() 

    # Extract relevant information
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    print(data)

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user} : {message}")

    # Generate a response using LLMProxy
    response = generate(
        model='4o-mini',
        system='answer my question and add keywords',
        query= message,
        temperature=0.0,
        lastk=0,
        session_id='GenericSession'
    )

    response_text = response['response']
    
    # Send response back
    print(response_text)
    response_text = add_feedback()

    return jsonify({"text": response_text})
    
@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()