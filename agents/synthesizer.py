import sys
sys.path.append("../")
import json
from db.feedback_db import fetch_feedbacks
from rc.initiateRequest import send
from proxy.llmproxy import generate
from db.synthesized_db import add_paper_feedback, get_paper_feedback, mark_feedback_sent
from dicts import papers

def chunk_list(data, chunk_size):
    """ Split list into chunks of specified size. """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def synthesize_feedback_in_batches(feedback_list):
    """ Process feedback in batches of 5, maintaining previous synthesis for better continuity. """
    if not feedback_list:
        print("No feedback received for this presentation.")
        return False
    
    feedback_texts = [entry["feedback"] for entry in feedback_list]
    batches = chunk_list(feedback_texts, 5)  # Split into batches of 5


    previous_synthesis = ""

    for batch in batches:
        prompt = f"""
        The following is a batch of student feedback/comments on a research paper presentation. 
        Extract the audience's key comments from it. Combine these insights with those of the previous batch, while minimizing redundancy/similar comments.
        Format in paragraph form, written in first person from the audience's perspective, so that the synthesized feedback can be provided to the presenter.

        Insights from previous feedback batch (if any):
        {previous_synthesis}

        New Feedback Batch:
        {json.dumps(batch, indent=2)}

        Output EXACTLY in JSON format as follows:

        {{
            "synthesized_feedback":"Paragraph with the most important and unique insights combined from summary of new feedback batch and previous feedbacks. 150 words maximum."
        }}
        """

        try:
            # Call LLM with previous synthesis included
            response = generate(model='4o-mini', system='Focus on extracting the key points.', query=prompt, lastk=0, session_id="synthesizer")
            new_synthesis = json.loads(response.get('response', ''))['synthesized_feedback']
            previous_synthesis = new_synthesis  # Update for next batch

        except Exception as e:
            raise RuntimeError(f"Error in synthesize_feedback_in_batches(): {e}")

    return new_synthesis


def main():
    paper_num = 1
    date = "2025-03-04"

    # Step 1: Fetch all feedback entries
    feedback_entries = fetch_feedbacks(paper_num, date)

    if not feedback_entries:
        print("No feedback found for this paper.")
        return

    # Step 2: Identify the presenter
    presenter = feedback_entries[0]["presenter"]  # Assuming all feedbacks have the same presenter


    # Step 3: Synthesize feedback in batches
    synthesized_feedback = synthesize_feedback_in_batches(feedback_entries)

    print("Feedback:", synthesized_feedback)



    # Step4: Store synthesized feedback in DB
    add_paper_feedback(date, paper_num, presenter, synthesized_feedback)

    #return

    # Step 4: Send the synthesized feedback to the presenter
    if(synthesized_feedback):
        send(presenter, f"""Here is a summmary of student feedback on your presentation on the paper **{papers[date][paper_num][0]}**:\n\n"""+ synthesized_feedback)
        print("Feedback sent.")
        mark_feedback_sent(date, paper_num)
        print("Feedback marked as sent.")
        
    else:
        return False

#main()