import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("8266819825:AAGAD9pJCBxf5wF6aD_E9azZjWsJmNmSvEw") 

waiting_users = []
active_chats = {}

# Allow only English characters
def is_english(text):
    return bool(re.fullmatch(r"[A-Za-z0-9\s.,!?'\"]+", text))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello 👋\n"
        "This is an English-only stranger chat bot.\n\n"
        "Commands:\n"
        "/next - Find a stranger\n"
        "/stop - Leave chat"
    )

async def next_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in active_chats:
        partner = active_chats.pop(user_id)
        active_chats.pop(partner, None)
        await context.bot.send_message(partner, "❌ Chat ended.")

    if waiting_users:
        partner = waiting_users.pop(0)
        active_chats[user_id] = partner
        active_chats[partner] = user_id

        await context.bot.send_message(user_id, "✅ Connected to a stranger.")
        await context.bot.send_message(partner, "✅ Connected to a stranger.")
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for a stranger...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in active_chats:
        partner = active_chats.pop(user_id)
        active_chats.pop(partner, None)
        await context.bot.send_message(partner, "❌ The other user left.")

    if user_id in waiting_users:
        waiting_users.remove(user_id)

    await update.message.reply_text("🚫 You left the chat.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if not is_english(text):
        await update.message.reply_text(
            "⚠️ English only.\n"
            "Please send messages in English."
        )
        return

    if user_id in active_chats:
        partner = active_chats[user_id]
        await context.bot.send_message(partner, text)
    else:
        await update.message.reply_text("ℹ️ Type /next to start chatting.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("next", next_chat))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 English-only Stranger Bot is running...")
app.run_polling(drop_pending_updates=True)
