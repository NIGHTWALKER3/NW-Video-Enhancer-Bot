import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from moviepy.editor import VideoFileClip
from PIL import Image

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # <-- BOT TOKEN COMES FROM GITHUB SECRETS


# -------------------------
# START COMMAND
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Use:\n"
        "📸 /photo – Enhance Photos\n"
        "🎥 /video – Enhance Videos"
    )


# -------------------------
# PHOTO ENHANCE COMMAND
# -------------------------
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "photo"
    keyboard = [
        [InlineKeyboardButton("📸 Send Photo", callback_data="send_photo")]
    ]
    await update.message.reply_text(
        "Upload the photo you want to enhance.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# -------------------------
# VIDEO ENHANCE COMMAND
# -------------------------
async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "video"
    keyboard = [
        [
            InlineKeyboardButton("360p", callback_data="360"),
            InlineKeyboardButton("480p", callback_data="480")
        ],
        [
            InlineKeyboardButton("720p", callback_data="720"),
            InlineKeyboardButton("1080p", callback_data="1080")
        ]
    ]
    await update.message.reply_text(
        "Choose video quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# -------------------------
# BUTTON HANDLER
# -------------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # VIDEO QUALITY SELECTED
    if query.data in ["360", "480", "720", "1080"]:
        context.user_data["quality"] = query.data
        await query.edit_message_text("🎥 Now send the video...")
        return

    # PHOTO
    if query.data == "send_photo":
        await query.edit_message_text("📸 Send your photo now.")
        return


# -------------------------
# PROCESS PHOTO
# -------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "photo":
        return

    file = await update.message.photo[-1].get_file()
    path = "photo.jpg"
    await file.download_to_drive(path)

    img = Image.open(path)
    img = img.resize((img.width * 2, img.height * 2))  # Simple enhancement
    enhanced_path = "enhanced_photo.jpg"
    img.save(enhanced_path)

    await update.message.reply_photo(photo=open(enhanced_path, "rb"))
    os.remove(path)
    os.remove(enhanced_path)


# -------------------------
# PROCESS VIDEO
# -------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "video":
        return

    quality = context.user_data.get("quality")
    file = await update.message.video.get_file()
    path = "input.mp4"
    await file.download_to_drive(path)

    clip = VideoFileClip(path)

    sizes = {
        "360": 360,
        "480": 480,
        "720": 720,
        "1080": 1080
    }

    target_h = sizes.get(quality, 720)
    w = int((clip.w / clip.h) * target_h)

    clip_resized = clip.resize((w, target_h))
    output = "enhanced_video.mp4"
    clip_resized.write_videofile(output)

    await update.message.reply_video(video=open(output, "rb"))

    clip.close()
    os.remove(path)
    os.remove(output)


# -------------------------
# MAIN
# -------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("photo", photo))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    app.run_polling()


if __name__ == "__main__":
    main()
