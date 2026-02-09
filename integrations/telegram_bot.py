
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import config
from remote_handler import handle_remote_command

# Suppress debug logs
logging.getLogger('httpx').setLevel(logging.WARNING)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Security: Verify User ID
    allowed_id = config.REMOTE_CONFIG["telegram_user_id"]
    if allowed_id and user_id != allowed_id:
        print(f"[Telegram] Unauthorized access attempt from ID {user_id}")
        return

    print(f"[Telegram] Command from {user_id}: {message_text}")
    
    # Execute Command
    response = handle_remote_command(message_text)
    
    # Reply
    await update.message.reply_text(f"🤖 **RJ**: {response}")

def run_telegram():
    token = config.REMOTE_CONFIG["telegram_token"]
    if not token:
        print("[Telegram] No token found. Skipping Telegram bot.")
        return

    try:
        app = ApplicationBuilder().token(token).build()
        msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
        app.add_handler(msg_handler)
        
        print(f"[Telegram] Bot Started (Authorized User: {config.REMOTE_CONFIG['telegram_user_id']})")
        app.run_polling()
    except Exception as e:
        print(f"[Telegram] Connection Failed: {e}")
