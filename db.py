import boto3
import uuid

dynamodb = boto3.resource("dynamodb")
table_name = "summaries"  # Replace with your table name
table = dynamodb.Table(table_name)

def add_feedback():
    try:
        data = "Here is the feedback."
        summary_id = str(uuid.uuid4()) 
        table.put_item(
            Item={
                "id": summary_id,
                "data": data
            }
        )

        return f"Thanks! Feedback submitted successfully."
    except Exception as e:
        return f"Error submitting feedback: {e}"