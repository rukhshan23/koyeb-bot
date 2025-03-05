import sys
sys.path.append("../")
from flask import Flask, request, jsonify
from db.feedback_db import put_entry
from parse import parse_feedback
from dicts import papers
from datetime import datetime
import pytz
from agents.grader import grade_feedback
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
    date = str(datetime.now(tz).date())

    print(date)
    
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
    parsed_message = parse_feedback(message)
    if(parsed_message == False):
        return jsonify({"text": "Incorrect submission format. Please resubmit, ensuring that the paper number is either 1, 2 or 3 and the submission format is as follows:\n\nPaper Number: paper-number\nFeedback: your-feedback"})
    else:
        print(f"Data payload from : {data}")
        print(f"Message from {sender} : {message}")
        paper_num = parsed_message['paper_number']
        presenter = papers[date][paper_num][1]
        feedback = parsed_message['feedback']

        response = grade_feedback(feedback, str(paper_num)+":"+date, papers[date][paper_num][0])

        #response = put_entry(paper_num, sender, presenter, feedback, date)

        return jsonify({"text": response})


@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()