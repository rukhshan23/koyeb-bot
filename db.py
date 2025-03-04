import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table_name = "feedback"  # Replace with your table name
table = dynamodb.Table(table_name)

def put_entry(paper_num, sender, presenter, feedback, date):
    try:
        feedback_id = if_exists(paper_num, sender, date)
        if (feedback_id):
            return update(feedback_id, paper_num, sender, presenter, feedback, date)
        else:
            return add(paper_num, sender, presenter, feedback, date)
    except Exception as e:
        return f"Error in put_entry(): {e}"

def if_exists(paper_num, sender, date):
    """Check if an entry exists based on paper_num, sender, and date WITHOUT using a GSI."""
    try:
        response = table.scan(
            FilterExpression=(
                Attr("paper_num").eq(paper_num) & 
                Attr("sender").eq(sender) & 
                Attr("date").eq(date)
            ),
            Limit=1  # Get only one match to reduce unnecessary scanning
        )
        items = response.get("Items", [])
        return items[0]["id"] if items else None  # Return first match's ID if exists
    except Exception as e:
        print(f"Error in if_exists(): {e}")
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