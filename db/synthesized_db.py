import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("synthesized")  # Replace with your actual table name

def add_paper_feedback(date, paper_num, presenter, feedback):
    """Adds a paper feedback entry to the DynamoDB table with a default 'sent' status of False."""
    try:
        # Ensure paper_num is an integer
        paper_num = int(paper_num)
        
        # Insert item into table
        table.put_item(
            Item={
                "date": date,  # Partition Key
                "paper_num": paper_num,  # Sort Key
                "presenter": presenter,
                "feedback": feedback,
                "sent": False  # Default value for tracking if feedback is sent
            }
        )
        print(f"Feedback added for Paper {paper_num} on {date}.")
        return {"message": "Feedback added successfully.", "status": "success"}
    
    except Exception as e:
        raise RuntimeError(f"Error in add_paper_feedback(): {e}")



def get_paper_feedback(date, paper_num):
    """Retrieves feedback for a specific paper on a given date."""
    try:
        # Ensure paper_num is an integer
        paper_num = int(paper_num)
        
        # Query the table using date (PK) and paper_num (SK)
        response = table.get_item(
            Key={
                "date": date,  # Partition Key
                "paper_num": paper_num  # Sort Key
            }
        )
        
        # Check if item exists
        item = response.get("Item")
        if item:
            return {"message": "Feedback retrieved successfully.", "feedback": item, "status": "success"}
        else:
            return {"message": "No feedback found for the given date and paper_num.", "status": "not_found"}

    except Exception as e:
        raise RuntimeError(f"Error in get_paper_feedback(): {e}")
    


def mark_feedback_sent(date, paper_num):
    """Updates the 'sent' field to True for a specific paper on a given date."""
    try:
        # Ensure paper_num is an integer
        paper_num = int(paper_num)
        
        # Update the item in the table
        response = table.update_item(
            Key={
                "date": date,  # Partition Key
                "paper_num": paper_num  # Sort Key
            },
            UpdateExpression="SET sent = :s",
            ExpressionAttributeValues={
                ":s": True  # Set 'sent' to True
            },
            ReturnValues="UPDATED_NEW"
        )

        print(f"Feedback for Paper {paper_num} on {date} marked as sent.")
        return {"message": "Feedback marked as sent.", "status": "success", "updated_attributes": response.get("Attributes", {})}

    except Exception as e:
        raise RuntimeError(f"Error in mark_feedback_sent(): {e}")


