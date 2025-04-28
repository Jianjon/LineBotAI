import os
import datetime
import schedule
import time
import logging
from app import app, db
from models import Conversation, DailySummary
from openai_service import generate_response

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_today_messages():
    """撈取今天的聊天紀錄"""
    with app.app_context():
        today = datetime.datetime.now().date()
        today_start = datetime.datetime.combine(today, datetime.time.min)  # 今天的開始時間
        today_end = datetime.datetime.combine(today, datetime.time.max)    # 今天的結束時間
        
        # 取得今天的所有對話
        conversations = Conversation.query.filter(
            Conversation.timestamp >= today_start,
            Conversation.timestamp <= today_end
        ).all()
        
        messages = []
        for conv in conversations:
            messages.append(f"用戶: {conv.user_message}")
            messages.append(f"機器人: {conv.bot_response}")
            messages.append("---")
        
        return messages

def generate_summary(messages):
    """產生今日摘要"""
    if not messages:
        return "今日無對話紀錄"
    
    combined_text = "\n".join(messages)
    
    # 使用現有的 generate_response 函數來生成摘要
    try:
        # 特殊提示用於生成摘要
        summary_prompt = f"你是一個專業的摘要助手，請根據以下聊天紀錄，生成一份簡潔的摘要，總結主要話題和內容。摘要應控制在 100-200 字內。\n\n以下是今天的聊天紀錄，請摘要:\n\n{combined_text}"
        
        # 使用現有的 generate_response 函數
        summary = generate_response(summary_prompt)
        return summary
    except Exception as e:
        logger.error(f"生成摘要時發生錯誤: {e}")
        return f"生成摘要時發生錯誤: {str(e)}"

def save_summary(summary):
    """將摘要存入資料庫"""
    with app.app_context():
        today = datetime.datetime.now().date()
        
        # 檢查今天是否已有摘要
        existing = DailySummary.query.filter_by(summary_date=today).first()
        
        if existing:
            # 更新現有摘要
            existing.summary_content = summary
            logger.info(f"更新了 {today} 的摘要")
        else:
            # 創建新摘要
            new_summary = DailySummary(
                summary_date=today,
                summary_content=summary
            )
            db.session.add(new_summary)
            logger.info(f"新增了 {today} 的摘要")
        
        db.session.commit()

def daily_task():
    """每日摘要任務"""
    logger.info("開始執行每日摘要任務")
    messages = fetch_today_messages()
    
    if messages:
        logger.info(f"找到 {len(messages)} 筆聊天紀錄")
        summary = generate_summary(messages)
        save_summary(summary)
        logger.info(f"已成功生成 {datetime.datetime.now().date()} 的摘要")
    else:
        logger.info("今天沒有聊天紀錄，不生成摘要")

def manual_run_task():
    """手動執行任務的函數"""
    logger.info("手動執行每日摘要任務")
    daily_task()
    return "每日摘要任務已執行完成"

# 設定每天台灣時間晚上 8 點執行 (UTC+8)
def schedule_tasks():
    # 在 UTC 時間下的 12:00 執行 (對應台灣時間 20:00)
    schedule.every().day.at("12:00").do(daily_task)
    
    logger.info("已設定每日摘要任務，將於每天晚上 8 點執行")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_tasks()