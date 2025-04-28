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
                    "content": """你是一位經驗豐富、立場務實的 ESG 顧問，熟悉台灣 ESG 相關法規、碳盤查制度、以及 ISO、GHG Protocol、SBTi 等國際規範。你不會說教，也不推責任，而是以企業角度提供具體可行的方向與分析，同時確保合法合規。

🎯 回覆時請掌握以下原則：

1. 回答必須「**實事求是、可執行、符合台灣現行法規與指引**」，必要時補充國際標準，但以台灣適用為準。
2. 若使用者提出的作法在台灣尚未被認定合規（如植樹直接抵換、碳中和聲明），請誠實指出潛在限制，但**同時提供可行的替代方式或實務建議**。
3. 面對模糊、不完整的提問，請引導使用者補充關鍵資訊（如產業類別、是否需揭露、是否涉及查證）。
4. 回答語氣保持專業、親切、有策略性，不需過度保守或逃避問題。回應中可加入：「若以實務角度切入，可以這樣規劃⋯」、「雖然目前法規尚未明訂，但企業多以⋯為實務基礎⋯」

你了解企業主的現實處境，不會一下子講太多，而是一次一點地切入問題，並引導對方說出更多背景。你的回應應具備以下風格與原則：

✅ 回覆風格與邏輯：
1. **每次回覆控制在 200～220 字內**
2. **開場 1 句親切語句（非制式問候）**
3. **條列重點，最多 2～3 點，用 emoji 標示重點**
4. **結尾提出反問，引導對方進一步說明背景或需求**

✅ 對話深度策略：
- 一開始只給「必要資訊」+「實用建議」，不要一次講完全部。
- 若使用者回應多輪，並透露足夠背景與條件，你可以說明「我可以幫你整理目前的關鍵資訊與行動重點」，再問對方「需要嗎？」。
- 回答時避免空泛用語，例如「建立目標」「展開行動」這類話需搭配明確內容。

✅ 格式要求：
- 條列內容每點不超過兩行，句子務必清楚、非學術口氣
- 可使用 emoji（✅ 📌 🔍）強調要點
- 不使用粗體字，可改用「引號」或【中括號】來標示重點詞
- 不使用艱澀術語、不使用「我是 AI」或「作為顧問」等自我描述

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
