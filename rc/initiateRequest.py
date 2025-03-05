import requests
import os

# Replace with your Rocket.Chat server URL
ROCKET_CHAT_URL = "https://chat.genaiconnect.net/"


def create_dm(auth_token, user_id, target_username):
    url = f"{ROCKET_CHAT_URL}/api/v1/im.create"
    headers = {"X-Auth-Token": auth_token, "X-User-Id": user_id, "Content-Type": "application/json"}
    payload = {"username": target_username}
    
    response = requests.post(url, headers=headers, json=payload).json()
    
    if "room" not in response:
        raise Exception(f"Error creating DM: {response}")
    
    return response["room"]["_id"]

# Send a message in the DM room
def send_message(auth_token, user_id, room_id, message_text):
    url = f"{ROCKET_CHAT_URL}/api/v1/chat.postMessage"
    headers = {"X-Auth-Token": auth_token, "X-User-Id": user_id, "Content-Type": "application/json"}
    payload = {"roomId": room_id, "text": message_text}
    
    response = requests.post(url, headers=headers, json=payload).json()
    
    if response.get("success") is not True:
        raise Exception(f"Failed to send message: {response}")

# Main function
def send(TARGET_USERNAME, MESSAGE_TEXT):
    try:
        auth_token = os.environ.get("authToken")
        user_id = os.environ.get("userID")
        # Step 1: Create DM with target user
        room_id = create_dm(auth_token, user_id, TARGET_USERNAME)

        # Step 2: Send the message
        send_message(auth_token, user_id, room_id, MESSAGE_TEXT)
    
    except Exception as e:
        raise Exception(f"Failed to send(): {e}")
