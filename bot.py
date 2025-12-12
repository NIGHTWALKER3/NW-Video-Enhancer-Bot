import os
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from enhancer import enhance_video

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Welcome to AI Video Enhancer Bot\n\n"
        "/fix – Fix blurry\n"
        "/4k – Upscale to 4K\n"
        "/restore – Restore old footage\n\n"
        "Send a video after choosing a command."
    )

user_mode = {}

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode[update.effective_user.id] = "fix"
    await update.message.reply_text("✔ Send the video to fix blur.")

async def upscale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode[update.effective_user.id] = "4k"
    await update.message.reply_text("✔ Send the video to upscale to 4K.")

async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode[update.effective_user.id] = "restore"
    await update.message.reply_text("✔ Send the video to restore.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = user_mode.get(user_id, None)

    if mode is None:
        await update.message.reply_text("❗ Choose a mode first: /fix /4k /restore")
        return

    video = await update.message.video.get_file()

    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as input_file:
        await video.download_to_drive(input_file.name)
        output_path = enhance_video(input_file.name, mode)

        await update.message.reply_document(open(output_path, "rb"))
        os.remove(output_path)

application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("fix", fix))
application.add_handler(CommandHandler("4k", upscale))
application.add_handler(CommandHandler("restore", restore))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))

if __name__ == "__main__":
    application.run_polling()