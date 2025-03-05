import sys
sys.path.append("../")
from proxy.llmproxy import generate
from db.feedback_db import get_ungraded_feedback, update_feedback_grade, update_feedback_status, get_unsent_feedback
from dicts import papers
from rc.initiateRequest import send
import json

def determine_session_id(paper_num, date):
    return str(paper_num) + ":" + date

def grade_feedback(feedback_text, session_id, paper_name):
    rubric = f"""\n\nAbove, you are provided with student-feedback on a research paper presentation on the paper titled, '{paper_name}'. Grade the submitted feedback based on the rubric below and the research paper provided to you: 

    1. Clear Understanding - Does the feedback clearly and accurately describe the main idea presented?
    
    2. Depth - Does the feedback provide suggestions to build on the content of the presented work?

    3. Presentation Style - Does the feedback comment on the positives and/or negatives of the presenter's presentation style?

    4. Respect & Professionalism - Is the feedback polite, respectful, and framed in a way that is encouraging?

    Rate each of the four aspects of the student-feedback submission out of 5, where 0 is the minimum/worse rating and 5 is the maximum/best rating. The explanation in the end should be friendly and polite. You must respond in JSON format. An example output in the exact JSON format required is provided below.
    You must NOT add ```json ```.
    
        {{
            "Clear Understanding": "4",
            "Depth": "5",
            "Presentation Style": "4",
            "Respect & Professionalism": "3",
            "explanation": "overall qualitative comments for the student on their submission"
        }}
    """

    prompt = feedback_text + rubric
    grade = generate(model='4o-mini', system='Grade fairly. Respond in JSON format.', query= prompt, lastk=0, session_id=session_id)
    return str(grade['response'])
    #response_text = response['response']


def main(paper_num, date):


    #Step 1: Fetch ungraded feedback
    feedback_entries = get_ungraded_feedback(paper_num, date)
    if not feedback_entries:
        print("No ungraded feedback found.")
    
    # Step 2: Choose the appropriate session_id
    session_id = determine_session_id(paper_num, date)
    for entry in feedback_entries:
        entry_id = entry["id"]
        feedback_text = entry["feedback"]
        # Step 3: Grade the feedback
        grade = grade_feedback(feedback_text, session_id, papers[date][paper_num][0])
        
        # Step 4: Store the grade and update the database
        update_feedback_grade(entry_id, grade)
        # Step 6: Log in DB that grade has been sent
        # update_feedback_status(entry_id)
    
    if(feedback_entries):
        print("All feedback has been graded.")

    
    #Step 7: Fetch all unsent feedback
    unsent_feedback = get_unsent_feedback(paper_num, date)
    if not unsent_feedback:
        print("No unsent feedback found.")
        return


    for entry in unsent_feedback:
        send_grade = json.loads(entry["grade"])
        send_message = f"Your submission for the paper titled **\"{papers[date][paper_num][0]}\"** has been reviewed:\n\n" + send_grade['explanation']
        send(entry["sender"], send_message)
        update_feedback_status(entry["id"])

    print("All feedback has been sent.")

main(1,"2025-03-04")