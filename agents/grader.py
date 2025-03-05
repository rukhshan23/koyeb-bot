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
    rubric = f"""\n\nAbove, you are provided with feedback from a student in the audience on a **lecture-style presentation** of the research paper titled **'{paper_name}'**.
        ### **Your Task**
        1. **Evaluate the student's feedback** based on the criteria below.
        2. **Assign a rating (0-5) for each category**, ensuring that your ratings are grounded in specific evidence from the feedback.
        3. **Provide a qualitative explanation** at the end to justify your ratings.
        4. **Output must be in JSON format** (example format given below). **Do not include markdown syntax (```json)**.

        ---

        ### **🔹 Rating Criteria (Evaluate the Feedback, NOT the Presentation)**
        1. **Understanding (0-5)** – Does the feedback show that the student **clearly understood the main idea of the paper**?
        2. **Future Ideas (0-5)** – Does the feedback provide **constructive suggestions** to build upon the presented work?
        3. **Comments on Style (0-5)** – Does the feedback include **insights on the presenter’s style** (e.g., clarity, engagement, pacing)?
        4. **Respect & Professionalism (0-5)** – Is the feedback **polite, respectful, and constructive**, even if critical?

        **Guidance for Ratings:**
        - **5** = Strong evidence of this criterion in the feedback.
        - **3-4** = Some evidence, but weak or lacking in depth.
        - **0-2** = Poor, missing, or irrelevant.

        ---

        Sample feedback 1: Great paper!
        Sample output 1:

        {{
            "Clear Understanding": "1",
            "Future Ideas": "0",
            "Presentation Style": "1",
            "Respect & Professionalism": "2",
            "explanation": "Your feedback would be even more valuable if you included specific details to demonstrate your understanding of the paper and offered suggestions for building on the work. Additionally, sharing thoughts on the presenter's style—such as clarity, engagement, or pacing—could make your feedback more constructive and helpful. Keep going—you’re on the right track!"
        }}

        Sample feedback 2: The presentation was fine, and I understood most of it. The presenter spoke well, but some slides were a little text-heavy. Maybe next time, they could add more visuals. The topic was interesting, but I didn’t really see how it connects to real-world applications.
        Sample output 2:

        {{
            "Clear Understanding": "3",
            "Future Ideas": "2",
            "Presentation Style": "3",
            "Respect & Professionalism": "4",
            "explanation": "Your feedback shows a good understanding of the presentation, and your suggestion for adding more visuals is a helpful start! To make your feedback even more impactful, consider elaborating on the key contributions of the paper and providing more depth in your suggestions. Adding more detailed comments on the presenter’s style—such as their clarity, pacing, or engagement—could also make your feedback more constructive. Keep going—you're on the right track!"
        }}

        Sample feedback 3: The presentation effectively explained the key contributions of the paper, especially the perceptions of autonomy of autistic people in the context of LLM-powered writing assistance. I liked how the presenter broke down complex concepts into simpler parts. One area for improvement could be addressing the ethical implications more thoroughly. The pacing was good, and the speaker engaged well with questions. Overall, a very strong presentation!
        Sample output 3:

        {{
            "Clear Understanding": "5",
            "Future Ideas": "4",
            "Presentation Style": "5",
            "Respect & Professionalism": "5",
            "explanation": "Your feedback demonstrates a strong understanding of the paper’s main ideas, which is great to see! Your suggestion regarding ethical considerations adds depth and shows thoughtful engagement with the topic. The comments on presentation style are specific and constructive, making them especially useful for the presenter. Additionally, your respectful and encouraging tone enhances the impact of your feedback—well done!"
        }}





    """

    prompt = feedback_text + rubric

    print("PROMPT:", prompt)
    grade = generate(model='gpt-4o', system='Grade fairly. Respond in JSON format.', query= prompt, lastk=0, session_id=session_id, rag_threshold = 0.2,
    rag_usage = True, rag_k = 5)
    print(grade)
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

#main(1,"2025-03-04")