import random
from ValentinMusic import app
from config import BANNED_USERS

# The channel ID provided by the user for settings menu backgrounds
SETTINGS_PHOTO_CHANNEL = -1002439966467

async def get_random_photo():
    """
    Fetch a random photo message from the specified channel.
    Returns the file_id of the photo.
    """
    try:
        # Fetch the last 100 messages from the channel
        messages = []
        async for message in app.get_chat_history(SETTINGS_PHOTO_CHANNEL, limit=50):
            if message.photo:
                messages.append(message.photo.file_id)
        
        if not messages:
            return None
            
        return random.choice(messages)
    except Exception as e:
        print(f"Error fetching random photo: {e}")
        return None
