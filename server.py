import os
import httpx
from mcp.server import MCPServer
from mcp.types import ToolAnnotations

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

mcp = MCPServer("Qixiaobao Doorbell v2")

@mcp.tool(
    title="Get latest private chat id",
    description=(
        "Read the latest Telegram update received by this bot and return the numeric private chat_id. "
        "Use only during one-time setup. This does not send a message."
    ),
    annotations=ToolAnnotations(
        read_only_hint=True,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
async def get_latest_chat_id() -> str:
    """Return the newest private Telegram chat_id seen by this bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
    data = response.json()
    if not response.is_success or not data.get("ok"):
        raise RuntimeError(f"Telegram getUpdates failed: {data.get('description', response.text)}")

    for update in reversed(data.get("result", [])):
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            continue
        chat = msg.get("chat") or {}
        if chat.get("type") == "private" and chat.get("id") is not None:
            return str(chat["id"])

    raise RuntimeError("No private Telegram update found. Send the bot a message first, then try again.")

@mcp.tool(
    title="Send knock",
    description=(
        "Send exactly one short Telegram message to the owner's fixed private chat. "
        "Use only when the user has explicitly authorized this notification workflow. "
        "Do not call repeatedly."
    ),
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
)
async def send_knock(message: str) -> str:
    """Send one short Telegram doorbell message to the fixed owner chat."""
    if not CHAT_ID:
        raise RuntimeError("TELEGRAM_CHAT_ID is not configured yet.")

    message = message.strip()
    if not message:
        raise ValueError("message must not be empty")
    if len(message) > 500:
        raise ValueError("message must be 500 characters or fewer")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "disable_web_page_preview": True,
            },
        )
    data = response.json()
    if not response.is_success or not data.get("ok"):
        raise RuntimeError(f"Telegram send failed: {data.get('description', response.text)}")
    return "Knock sent."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        stateless_http=True,
        json_response=True,
    )
