import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from enhancer import enhance_photo, enhance_video  # Your AI enhancer functions

load_dotenv()  # Load .env for API key

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ----- Commands -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /enhance_photo or /enhance_video")

async def enhance_photo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("720p", callback_data="photo_720")],
        [InlineKeyboardButton("1080p", callback_data="photo_1080")],
        [InlineKeyboardButton("4K", callback_data="photo_4k")]
    ]
    await update.message.reply_text("Select photo quality:", reply_markup=InlineKeyboardMarkup(keyboard))

async def enhance_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("720p", callback_data="video_720")],
        [InlineKeyboardButton("1080p", callback_data="video_1080")],
        [InlineKeyboardButton("4K", callback_data="video_4k")]
    ]
    await update.message.reply_text("Select video quality:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if "photo" in data:
        quality = data.split("_")[1]
        # Here call your enhance_photo function
        await query.edit_message_text(f"Enhancing photo at {quality} quality...")
        # result = enhance_photo(file, quality)
        # send result back to user
    elif "video" in data:
        quality = data.split("_")[1]
        await query.edit_message_text(f"Enhancing video at {quality} quality...")
        # result = enhance_video(file, quality)

# ----- Main -----
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("enhance_photo", enhance_photo_command))
app.add_handler(CommandHandler("enhance_video", enhance_video_command))
app.add_handler(CallbackQueryHandler(button))

# Run bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run_polling())
