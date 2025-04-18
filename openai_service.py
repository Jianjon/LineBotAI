import os
import logging
from openai import OpenAI

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
openai = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
logger = logging.getLogger(__name__)

def generate_response(user_message):
    """
    Generate a response using OpenAI's API.
    
    Args:
        user_message (str): The user's message
    
    Returns:
        str: The generated response
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是一位具備真誠、務實、帶點批判思維的 ESG 顧問。你曾經創業、也經歷過現實壓力，對企業主的難處有共感，但不會過度迎合。你講話清楚、直白，不繞圈子，善於用條列式、實際案例讓人一聽就懂。你的語氣可以輕鬆、但不輕浮；可以親切、但不虛假；你知道知識要能落地，才是真的幫助。

你對永續是有熱情的，但也知道企業資源有限，所以每一句話都力求「有效」。

請依以下格式回答問題，總長請控制在 200～220 字以內：

1. 開場 1 句話，語氣親切
2. 條列式拆解重點，最多 3 點（使用 emoji）
3. 結尾用 1 句反問或引導提問

回答時：
- 不要用艱澀語言
- 可以適度使用 emoji 做視覺引導
- 結尾常會加一句鼓勵或反問：「這樣能幫上忙嗎？還是你想看別的角度？」

請以此風格進行所有回應。"""
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=250,
            temperature=0.55
        )
        
        # Extract and return the response text
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating OpenAI response: {e}")
        return "抱歉，我暫時無法處理您的請求。請稍後再試。"

def analyze_image(base64_image):
    """
    Analyze an image using OpenAI's API.
    
    Args:
        base64_image (str): Base64-encoded image data
    
    Returns:
        str: Description of the image
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this image briefly:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return "抱歉，我無法分析這張圖片。"
