from flask import Flask, request, jsonify
from llmproxy import generate
from db import put_entry
from parse import parse_feedback
from dicts import papers
from datetime import datetime
import pytz
app = Flask(__name__)

@app.route('/')
def hello_world():
   return jsonify({"text":'Hello from Koyeb - you reached the main page!'})

@app.route('/query', methods=['POST'])
def main():
    # Set accepting to True if accepting submissions, False otherwise
    accepting = True
    if (accepting == False):
        return jsonify({"text": "Submissions portal for today's class is now closed."})
    
    # Set timezone and extract today's date 
    tz = pytz.timezone("America/New_York")
    date = datetime.now(tz).date()
    
    # Retrieve request payload
    data = request.get_json() 
    sender = data.get("user_name", False)
    message = data.get("text", False)

    # Ignore requests from bot
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})
    
    # Ignore if user_name or text field empty
    if(sender == False or message == False):
        return jsonify({"status": "ignored"})

    # Parse sender's message
    parsed_message = parse_feedback
    if(parsed_message == False):
        return jsonify({"text": "Incorrect format used. Please resubmit in the format provided below.\nPaper Number: paper-number\nFeedback: your-feedback"})
    else:
        print(f"Data payload from : {data}")
        print(f"Message from {sender} : {message}")
        paper_num = parsed_message['paper_number']
        presenter = papers[date][paper_num][1]
        feedback = parsed_message['feedback']

        

        #session_id = papers[parsed_message['paper_number']]
        #response = generate(model='4o-mini', system='answer my question and add keywords', query= message, lastk=0, session_id=session_id)
        #response_text = response['response']
        response = put_entry(paper_num, sender, presenter, feedback, date)
        return jsonify({"text": response})


@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()