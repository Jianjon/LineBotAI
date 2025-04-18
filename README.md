# ESG 顧問 LINE Bot

這是一個基於 Flask 和 OpenAI API 的 LINE Bot 項目，專門為提供 ESG（環境、社會、治理）相關建議而設計。

## 功能特點

- 使用 OpenAI 的 GPT-4o 模型提供專業的 ESG 諮詢
- 使用者對話記錄儲存在 PostgreSQL 資料庫中
- 管理員後台可查看使用者資訊和對話歷史
- 可編輯使用者產業和角色信息

## 技術架構

- **後端框架**：Flask
- **資料庫**：PostgreSQL + SQLAlchemy
- **AI 模型**：OpenAI GPT-4o
- **訊息平台**：LINE Messaging API

## 如何設置

1. 在 LINE Developers 控制台創建一個 Bot 帳號
2. 設置 Webhook URL
3. 配置以下環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `OPENAI_API_KEY`
   - `DATABASE_URL`
   - `SESSION_SECRET`

## 本地開發

1. 克隆此倉庫
2. 安裝依賴：`pip install -r requirements.txt`
3. 運行應用：`gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

## 授權

此項目依照 MIT 授權條款進行授權。