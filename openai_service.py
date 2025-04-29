import os
import logging
import random
from datetime import datetime, timedelta
try:
    from openai import OpenAI
except ImportError:
    logging.error("OpenAI package not installed. Please install it with 'pip install openai'.")
    OpenAI = None

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
openai = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
logger = logging.getLogger(__name__)

# 1. AgentIntentRecognizer: 意圖識別器
def recognize_intent(user_message):
    """
    判斷使用者訊息屬於：
    - "chat"：一般閒聊/寒暄
    - "professional"：專業問題/需依據標準回答
    """
    chat_keywords = ["你好", "謝謝", "在嗎", "哈囉", "請問在嗎", "今天好嗎", "加油", "辛苦了"]
    professional_keywords = ["碳盤查", "碳足跡", "碳中和", "ISO14064", "SBTi", "環境部", "查證", 
                           "減量專案", "排放", "溫室氣體", "ESG", "永續", "淨零", "碳", "排碳", 
                           "減碳", "報告", "揭露", "標準", "規範", "盤查"]

    if any(word in user_message for word in chat_keywords) and not any(word in user_message for word in professional_keywords):
        return "chat"
    else:
        # 保守策略，未知預設為專業問題（避免漏掉正經問題）
        return "professional"

# 2. AgentClassifier: 問題分類器
def classify_question(user_message):
    """
    分析使用者訊息，分類至適當的 ESG 知識範圍。
    回傳範圍標籤，例如 "ISO14064-1"、"SBTi"、"WBCSD"。
    """
    # 關鍵字分類邏輯
    if any(word in user_message for word in ["盤查", "組織碳排", "組織碳盤查", "範疇一", "範疇二", "範疇三"]):
        return "ISO14064-1"
    elif any(word in user_message for word in ["減量專案", "減碳專案", "碳權", "抵減", "碳補償", "減碳方法"]):
        return "ISO14064-2"
    elif any(word in user_message for word in ["查證", "第三方查核", "確信", "保證", "驗證"]):
        return "ISO14064-3"
    elif any(word in user_message for word in ["碳足跡", "產品碳排", "PCF", "LCA", "生命週期", "CFP"]):
        return "ISO14067"
    elif any(word in user_message for word in ["碳中和", "淨零", "碳移除", "carbon neutral", "net zero"]):
        return "ISO14068-1"
    elif any(word in user_message for word in ["SBTi", "科學基礎目標", "科學基礎減碳"]):
        return "SBTi"
    elif any(word in user_message for word in ["企業策略", "永續策略", "企業永續", "ESG", "WBCSD"]):
        return "WBCSD"
    elif any(word in user_message for word in ["台灣", "環境部", "法規", "管制", "申報"]):
        return "TaiwanReg"
    else:
        return "General"

# 3. AgentKnowledgeAssembler: 知識整合器
def build_knowledge_prompt(category):
    """
    根據分類結果，組合專業背景內容，限制回覆只依據特定標準。
    """
    base_prompt = """你是一位經驗豐富、立場務實的 ESG 顧問，熟悉碳盤查制度、以及相關國際規範。你的回答只能基於特定知識範圍，不可臆測或引用超出範圍的資訊。"""
    
    if category == "ISO14064-1":
        knowledge = """
你應該只引用 ISO14064-1（組織層級溫室氣體排放量化與報告）標準提供回答，相關重點包括：
1. 清冊邊界劃定（營運控制權/財務控制權/股權）
2. 範疇一/二/三排放源辨識與計算方法
3. 七種溫室氣體（CO2/CH4/N2O/HFCs/PFCs/SF6/NF3）的量化要求
4. 盤查基準年（Base Year）選擇與管理
5. 數據品質與文件管理
6. 不確定性評估

請務必指出這是依據ISO14064-1標準提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "ISO14064-2":
        knowledge = """
你應該只引用 ISO14064-2（專案層級溫室氣體減量量化與監測）標準提供回答，相關重點包括：
1. 減量專案設計與方法學選擇
2. 基線情境（Baseline scenario）建立
3. 專案情境邊界與排放源辨識
4. 額外性（Additionality）證明
5. 減量成效監測與量化
6. 專案文件製作與第三方查證要求

請務必指出這是依據ISO14064-2標準提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "ISO14064-3":
        knowledge = """
你應該只引用 ISO14064-3（溫室氣體查證與確證）標準提供回答，相關重點包括：
1. 查證/確證流程與原則
2. 查證團隊組成與能力要求
3. 保證等級（合理/有限）選擇
4. 不符合事項分級與處理
5. 重大性（Materiality）評估
6. 查證報告與聲明書製作

請務必指出這是依據ISO14064-3標準提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "ISO14067":
        knowledge = """
你應該只引用 ISO14067（產品碳足跡）標準提供回答，相關重點包括：
1. 產品系統邊界定義
2. 功能單位（Functional unit）選擇
3. 生命週期盤查與數據收集
4. 分配（Allocation）方法
5. 各階段活動數據與排放係數選用
6. 產品碳足跡標示與宣告要求

請務必指出這是依據ISO14067標準提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "ISO14068-1":
        knowledge = """
你應該只引用 ISO14068-1（碳中和）標準提供回答，相關重點包括：
1. 碳中和（Carbon Neutrality）定義與範圍
2. 移除/抵減方法選擇與評估
3. 碳中和主張與宣告規範
4. 碳中和計畫制定與實施
5. 抵減機制選擇標準
6. 碳中和進度追蹤與報告

請務必指出這是依據ISO14068-1標準提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "SBTi":
        knowledge = """
你應該只引用 SBTi（科學基礎減碳目標倡議）指引提供回答，相關重點包括：
1. 近期與長期減碳目標設定（近期/長期）
2. 目標審核與提交流程
3. Flag模型/SDA模型/ABS模型選擇
4. 氣候變遷情境對齊（1.5°C/well-below 2°C）
5. 範疇三納入要求與計算
6. 目標追蹤與更新機制
7. 淨零承諾與路徑規劃

請務必指出這是依據SBTi標準提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "WBCSD":
        knowledge = """
你應該只引用 WBCSD（世界企業永續發展委員會）指南提供回答，相關重點包括：
1. 企業永續策略與整合
2. 永續報告與揭露框架
3. 價值鏈合作與影響力
4. 氣候與自然解決方案
5. 資源循環與效率
6. 企業社會影響力評估

請務必指出這是依據WBCSD指南提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出標準範圍，請誠實說明並提供一般性建議。
"""
    elif category == "TaiwanReg":
        knowledge = """
你應該只引用台灣環境部發布的法規與指引提供回答，相關重點包括：
1. 溫室氣體減量及管理法規範
2. 碳費徵收與管理機制
3. 溫管法第一批與第二批應盤查登錄對象
4. 溫室氣體申報與查驗作業要求
5. 碳權抵換專案申請流程
6. 環境部永續資訊揭露要求

請務必指出這是依據台灣環境部法規提供的建議，若有其他標準參考，必須明確標示。若使用者提問超出法規範圍，請誠實說明並提供一般性建議。
"""
    else:  # General case
        knowledge = """
你必須基於ISO14064系列、ISO14067、ISO14068-1、SBTi指引、WBCSD指南和台灣環境部法規等權威來源提供回答。

如果無法確定適用的標準，請從以下角度回答：
1. 優先參考台灣法規要求
2. 其次引用國際通用標準
3. 若均無明確規範，請明確說明「目前尚無明確標準」，並提供一般性最佳實務建議

回答時必須指出引用的依據，確保專業性和可追溯性。避免臆測或提供未經標準支持的建議。
"""
    
    return base_prompt + knowledge

# 4. AgentSummaryFetcher: 摘要調用器
def fetch_recent_summaries_if_needed(user_message):
    """
    若使用者提問涉及「過去對話」或「進度問題」，引入最近3天的 daily_summary。
    
    注意：為避免循環導入問題，採用惰性導入方式。
    """
    progress_keywords = ["進度", "之前提到", "上次", "繼續", "我們討論過", "前次", "昨天", "前幾天"]
    
    if any(keyword in user_message for keyword in progress_keywords):
        try:
            # 惰性導入，避免循環引用
            from app import app, db
            from models import DailySummary
            
            with app.app_context():
                # 計算過去三天的日期
                today = datetime.now().date()
                three_days_ago = today - timedelta(days=3)
                
                # 從數據庫中獲取最近三天的摘要
                summaries = DailySummary.query.filter(
                    DailySummary.summary_date >= three_days_ago,
                    DailySummary.summary_date <= today
                ).order_by(DailySummary.summary_date.desc()).all()
                
                if not summaries:
                    logger.info("No recent summaries found")
                    return ""
                
                # 格式化摘要內容
                formatted_summaries = []
                for summary in summaries:
                    date_str = summary.summary_date.strftime("%Y-%m-%d")
                    formatted_summaries.append(f"日期: {date_str}\n{summary.summary_content}")
                
                logger.info(f"Found {len(summaries)} recent summaries")
                return "以下是最近的對話摘要，可參考回答當前問題：\n\n" + "\n\n".join(formatted_summaries)
        except Exception as e:
            logger.error(f"Error fetching summaries: {e}")
            return ""
    
    return ""

# 5. AgentResponseFormatter: 回覆風格整理器
def format_response(raw_response):
    """
    將GPT初步回應轉換成條列式 + emoji強調 + 開場親切語 + 結尾反問。
    """
    # 友善開場語選項
    friendly_openings = [
        "很高興收到您的提問！讓我整理一下重點：",
        "這個問題很重要，我來幫您分析：",
        "感謝您的問題，以下是關鍵資訊：",
        "這是個好問題！讓我為您整理相關要點：",
        "很高興能協助您釐清這個問題，以下是重點："
    ]
    
    # 結尾反問句選項
    closing_questions = [
        "方便分享一下您的產業別，讓我提供更精準的建議嗎？",
        "您目前面臨的主要挑戰是什麼呢？",
        "您對這個方向有什麼想法或顧慮嗎？",
        "是否需要我針對特定環節提供更多細節？",
        "這些資訊對您有幫助嗎？需要針對哪部分深入說明？"
    ]
    
    # Emoji 選項
    emojis = ["✅", "📌", "🔍", "💡", "🌟", "🔑"]
    
    try:
        # 選擇開場語
        opening = random.choice(friendly_openings)
        
        # 處理主體內容：找出要點並加上 emoji
        # 假設內容可能已經有條列或段落分隔
        lines = raw_response.split("\n")
        formatted_points = []
        content_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 跳過可能已經存在的開場白和結尾問句
            if len(formatted_points) == 0 and ("?" not in line and "！" not in line):
                continue
            if "?" in line and len(line) > 15 and len(content_points) > 0:
                continue
                
            # 添加其餘內容作為要點
            if len(content_points) < 3:  # 最多取3個要點
                emoji = random.choice(emojis)
                if not any(emoji in line for emoji in emojis):
                    content_points.append(f"{emoji} {line}")
                else:
                    content_points.append(line)
        
        # 選擇結尾反問句
        closing = random.choice(closing_questions)
        
        # 組合最終回覆
        final_response = f"{opening}\n\n"
        final_response += "\n\n".join(content_points)
        final_response += f"\n\n{closing}"
        
        # 確保字數在 200-220 之間
        if len(final_response) < 200:
            # 太短，擴充內容
            while len(final_response) < 200 and len(content_points) < 3:
                # 分析原回覆，找出可能的擴充點
                more_points = raw_response.split("。")
                for point in more_points:
                    if point.strip() and all(p not in point for p in content_points):
                        emoji = random.choice(emojis)
                        new_point = f"{emoji} {point.strip()}。"
                        content_points.append(new_point)
                        final_response = f"{opening}\n\n"
                        final_response += "\n\n".join(content_points)
                        final_response += f"\n\n{closing}"
                        break
                break  # 防止無限循環
                
        elif len(final_response) > 220:
            # 太長，縮減內容
            while len(final_response) > 220 and len(content_points) > 1:
                content_points.pop()  # 移除最後一個要點
                final_response = f"{opening}\n\n"
                final_response += "\n\n".join(content_points)
                final_response += f"\n\n{closing}"
        
        return final_response
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        # 如果格式化失敗，返回原始回覆
        return raw_response

# 6. AgentStrategicReactor: 對話策略反應器
def decide_need_followup(user_message):
    """
    判斷問題是否不夠完整，需要引導更多細節。
    """
    vague_indicators = ["怎麼做", "如何", "建議", "可以嗎", "可行嗎", "最佳做法", "範例"]
    missing_context = ["哪個產業", "什麼規模", "適合我嗎", "我們公司", "我該怎麼"]
    
    # 檢查是否有模糊指標但缺乏上下文
    has_vague = any(indicator in user_message for indicator in vague_indicators)
    lacks_context = not any(context in user_message for context in missing_context)
    
    if has_vague and lacks_context and len(user_message) < 50:
        return True
    return False

# 輔助函數：生成聊天型回覆
def generate_casual_chat_response(user_message):
    """
    回覆輕鬆聊天型訊息，保持親切、簡短。
    """
    casual_responses = [
        "嗨！很高興收到您的訊息。若有任何永續或ESG相關問題，隨時可以詢問我！",
        "您好！希望您今天一切順利。我隨時準備好協助您解答ESG與永續發展相關問題。",
        "哈囉！有什麼我能幫您的嗎？無論是碳盤查、減碳策略或ESG報告，都可以詢問我。",
        "嗨！感謝您的問候。若您有關於永續發展或碳管理的疑問，歡迎隨時提出。"
    ]
    return random.choice(casual_responses)

# 主函數：整合所有Agent
def generate_response(user_message):
    """
    根據使用者訊息，通過Multi-Agent流程生成專業回覆。
    
    Args:
        user_message (str): 使用者的訊息
    
    Returns:
        str: 生成的專業回覆
    """
    try:
        # Step 1: 判斷是聊天還是專業問題
        intent = recognize_intent(user_message)
        logger.info(f"Recognized intent: {intent}")
        
        # Step 2: 如果是普通聊天，簡單回覆
        if intent == "chat":
            return generate_casual_chat_response(user_message)

        # Step 3: 專業問題處理流程
        # (1) 分類問題
        category = classify_question(user_message)
        logger.info(f"Question category: {category}")
        
        # (2) 檢查是否需要特別引導（問題太模糊）
        needs_followup = decide_need_followup(user_message)
        
        # (3) 構建知識背景 Prompt
        knowledge_prompt = build_knowledge_prompt(category)
        
        # (4) 獲取相關摘要（如有必要）
        summary_context = fetch_recent_summaries_if_needed(user_message)
        
        # (5) 建立最終 Prompt
        system_prompt = f"""
{knowledge_prompt}

🎯 回覆時請掌握以下原則：

1. 回答必須「實事求是、可執行、符合標準」，必要時補充國際標準，但以台灣適用為準。
2. 若使用者提出的作法在台灣尚未被認定合規，請誠實指出潛在限制，但同時提供可行的替代方式或實務建議。
3. 面對模糊、不完整的提問，請引導使用者補充關鍵資訊（如產業類別、是否需揭露、是否涉及查證）。
4. 回答語氣保持專業、親切、有策略性，不需過度保守或逃避問題。

✅ 回覆格式要求：
1. 回覆字數控制在 200～220 字內
2. 開頭一句親切友善的句子
3. 條列重點，最多 2～3 點，用 emoji（✅ 📌 🔍）開頭每點
4. 結尾提出反問，引導對方進一步說明背景或需求

{summary_context}
"""

        # 針對需要引導的問題，調整 prompt
        if needs_followup:
            system_prompt += "\n請特別注意：提問者似乎需要更多引導。請確保在回覆中主動詢問產業類別、組織規模、目標時程等關鍵背景資訊。"
        
        # (6) 呼叫 OpenAI GPT-4o
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=250,
            temperature=0.55
        )
        
        raw_reply = response.choices[0].message.content.strip()
        logger.info(f"Raw GPT response generated: {len(raw_reply)} chars")
        
        # (7) 格式化回覆
        final_reply = format_response(raw_reply)
        logger.info(f"Formatted response: {len(final_reply)} chars")
        
        return final_reply
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "抱歉，我暫時無法處理您的請求。請稍後再試。"

# 保留原有的圖像分析功能
def analyze_image(base64_image):
    """
    分析圖像內容
    
    Args:
        base64_image (str): Base64編碼的圖像數據
    
    Returns:
        str: 圖像描述
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
                            "text": "請描述這張圖片，尤其關注與ESG或永續發展相關的元素："
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
