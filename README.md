# 祁小寶門鈴 v2（Render 測試版）

這是一顆極簡 MCP：
- `get_latest_chat_id`：一次性設定時讀取 bot 最近收到的私人 chat_id。
- `send_knock`：把一則訊息送到固定的 TELEGRAM_CHAT_ID。

## 第一次部署
Render 環境變數先只需要：
- `TELEGRAM_BOT_TOKEN`：BotFather 的 token

`TELEGRAM_CHAT_ID` 可以先留空。

部署後 MCP URL：
`https://<你的-render-service>.onrender.com/mcp`

ChatGPT 自訂 MCP：
- Server URL：上面的 `/mcp`
- Authentication：None / 無驗證

## 取得 chat_id
1. 先在 Telegram 私聊 bot 傳一句 `v2`。
2. 在 ChatGPT 手動呼叫 `get_latest_chat_id`。
3. 把拿到的純數字填到 Render 的 `TELEGRAM_CHAT_ID`。
4. Redeploy / Restart service。

之後 `send_knock` 就只會傳到這個固定 chat_id。

## 安全設計
- `send_knock` 不接受模型指定任意收件人。
- 訊息最多 500 字。
- send_knock 明確標記為 write、non-destructive、non-idempotent、closed-world。
- get_latest_chat_id 是 setup 用 read-only 工具。
