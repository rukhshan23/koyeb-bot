import requests
import json
from sample_feedbacks import feedbacks
from concurrent.futures import ThreadPoolExecutor
import time
# response_main = requests.get("https://new-courtnay-rukhshans-org-20d6f220.koyeb.app/")
# print('Web Application Response:\n', response_main.text, '\n\n')


# data = {"text":"Paper Number: 1\nFeedback: Great Paper.", "user_name":"rukhshan"}
# response_llmproxy = requests.post("https://new-courtnay-rukhshans-org-20d6f220.koyeb.app/query", json=data)
# print('LLMProxy Response:\n', response_llmproxy.text)

def send_feedback(feedback):
    """Function to send a single feedback request."""
    #api_url = "https://new-courtnay-rukhshans-org-20d6f220.koyeb.app/query"
    api_url = "http://127.0.0.1:5000/query"
    data = {
        "text": f"Paper Number: 1\nFeedback: {feedback}",
        "user_name": "rukhshan",
    }
    response = requests.post(api_url, json=data)
    
    # Print response for debugging
    print(f"Sent feedback: {response.status_code} - {response.text}")

def populate_with_feedbacks_parallel():
    """Send feedbacks in parallel using ThreadPoolExecutor."""

    # Use ThreadPoolExecutor to send requests in parallel
    with ThreadPoolExecutor(max_workers=11) as executor:
        executor.map(send_feedback, feedbacks.values())


def populate_with_feedbacks():
    # Define API endpoint
    # api_url = "https://new-courtnay-rukhshans-org-20d6f220.koyeb.app/query"
    api_url = "http://127.0.0.1:5000/query"

    # Loop through feedbacks and send each one to the API
    for feedback in feedbacks.values():
        data = {
            "text": f"Paper Number: 1\nFeedback: {feedback}",
            "user_name": "rukhshan",

        }
        response = requests.post(api_url, json=data)

        # Print response for debugging
        print(f"Sent feedback for Paper 1: {response.status_code} - {response.text}")

#populate_with_feedbacks()

populate_with_feedbacks_parallel()