import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table_name = "feedback"  # Replace with your table name
table = dynamodb.Table(table_name)

def put_entry(paper_num, sender, presenter, feedback, date):
    try:
        feedback_id = if_exists(paper_num, sender, presenter, feedback, date)
        if (feedback_id):
            return update(feedback_id, paper_num, sender, presenter, feedback, date)
        else:
            return add(paper_num, sender, presenter, feedback, date)
    except Exception as e:
        return f"Error in put_entry(): {e}"

def if_exists(paper_num, sender, presenter, feedback, date):
    try:
        response = table.scan(
            FilterExpression=(
                Attr("paper_num").eq(paper_num) & 
                Attr("sender").eq(sender) & 
                Attr("presenter").eq(presenter) & 
                Attr("feedback").eq(feedback) & 
                Attr("date").eq(date)
            )
        )
        items = response.get("Items", [])
        if items:
            return items[0]["id"]
        else:
            return None
    except Exception as e:
        print (f"Error in if_exists(): {e}")
        return None
    
def update(feedback_id, paper_num, sender, presenter, feedback, date):
    try:
        table.update_item(
            Key={"id": feedback_id},
            UpdateExpression="SET paper_num=:p, sender=:s, presenter=:pr, feedback=:f, #d=:d",
            ExpressionAttributeValues={
                ":p": paper_num,
                ":s": sender,
                ":pr": presenter,
                ":f": feedback,
                ":d": date
            },
            ExpressionAttributeNames={  # Use this to map `#d` to `date`
                "#d": "date"
            }
        )
        return "Thank you. Your feedback was updated successfully."
    except Exception as e:
        return f"Error in update(): {e}"
        
def add(paper_num, sender, presenter, feedback, date):
    try:
        feedback_id = str(uuid.uuid4()) 
        table.put_item(
            Item={
                "id": feedback_id,
                "paper_num": paper_num,
                "sender": sender,
                "presenter": presenter,
                "feedback": feedback,
                "date": date
            }
        )

        return f"Thank you. Your feedback was submitted successfully."
    except Exception as e:
        return f"Error in add(): {e}"
    
def get_ungraded_feedback(paper_num, date):
    try:
        response = table.scan(
            FilterExpression=(
                Attr("paper_num").eq(paper_num) &
                Attr("date").eq(date) &
                (
                    Attr("grade").not_exists() |  # Field does not exist
                    Attr("grade").eq("")         # Field exists but is empty
                )
            )
        )
        
        return response.get("Items", [])  # Return the list of matching feedback entries
    except Exception as e:
        print(f"Error in get_ungraded_feedback(): {e}")
        return []
    
def update_feedback_grade(entry_id, grade):
    """ Update the DynamoDB entry with the grade. """
    try:
        table.update_item(
            Key={"id": entry_id},
            UpdateExpression="SET grade = :g",
            ExpressionAttributeValues={
                ":g": grade,

            }
        )
    except Exception as e:
        print(f"Error updating grade for entry {entry_id}: {e}")

def get_unsent_feedback(paper_num, date):
    """Retrieve graded feedback that has not been sent yet (status is False or does not exist)."""
    try:
        response = table.scan(
            FilterExpression=(
                Attr("paper_num").eq(paper_num) &  # Filter by paper number
                Attr("date").eq(date) &  # Filter by date
                Attr("grade").exists() & Attr("grade").ne("") &  # Ensure it's graded
                (Attr("status").not_exists() | Attr("status").eq(False))  # Status is False or not set
            )
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"Error in get_unsent_feedback(): {e}")
        return []


    
def update_feedback_status(entry_id):
    """ Mark feedback as sent in the database. """
    try:
        table.update_item(
            Key={"id": entry_id},
            UpdateExpression="SET #status = :st",
            ExpressionAttributeNames={"#status": "status"},  # Alias for reserved keyword
            ExpressionAttributeValues={":st": True}
        )
    except Exception as e:
        print(f"Error updating status for entry {entry_id}: {e}")

def fetch_feedbacks(paper_num, date):
    """ Retrieve all feedbacks submitted for a given paper and date. """
    try:
        response = table.scan(
            FilterExpression=(
                Attr("paper_num").eq(paper_num) & 
                Attr("date").eq(date)
            )
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []
