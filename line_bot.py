import os
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

# LINE Bot credentials
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

# Initialize LINE Bot API and WebhookHandler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Setup logging
logger = logging.getLogger(__name__)

def send_message(user_id, message):
    """
    Send a message to a specific LINE user.
    
    Args:
        user_id (str): LINE user ID
        message (str): Message to send
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=message)
        )
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def get_profile(user_id):
    """
    Get profile information for a LINE user.
    
    Args:
        user_id (str): LINE user ID
    
    Returns:
        dict: User profile information or None if failed
    """
    try:
        profile = line_bot_api.get_profile(user_id)
        return {
            "display_name": profile.display_name,
            "user_id": profile.user_id,
            "picture_url": profile.picture_url,
            "status_message": profile.status_message
        }
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return None
