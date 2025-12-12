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

BOT_TOKEN = os.getenv("BOT_TOKEN")


# -------------------------
# START
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📸 /photo – Enhance Photo\n"
        "🎥 /video – Enhance Video"
    )


# -------------------------
# PHOTO COMMAND
# -------------------------
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "photo"

    keyboard = [
        [
            InlineKeyboardButton("360p", callback_data="p360"),
            InlineKeyboardButton("720p", callback_data="p720"),
        ],
        [
            InlineKeyboardButton("1080p", callback_data="p1080")
        ]
    ]

    await update.message.reply_text(
        "Choose quality for photo enhancement:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# -------------------------
# VIDEO COMMAND
# -------------------------
async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "video"

    keyboard = [
        [
            InlineKeyboardButton("360p", callback_data="v360"),
            InlineKeyboardButton("480p", callback_data="v480")
        ],
        [
            InlineKeyboardButton("720p", callback_data="v720"),
            InlineKeyboardButton("1080p", callback_data="v1080")
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

    data = query.data

    # PHOTO QUALITY SELECT
    if data.startswith("p"):
        context.user_data["photo_quality"] = int(data.replace("p", ""))
        await query.edit_message_text("📸 Now send the photo…")
        return

    # VIDEO QUALITY SELECT
    if data.startswith("v"):
        context.user_data["video_quality"] = int(data.replace("v", ""))
        await query.edit_message_text("🎥 Now send the video…")
        return


# -------------------------
# PROCESS PHOTO
# -------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "photo":
        return

    quality = context.user_data.get("photo_quality", 720)

    file = await update.message.photo[-1].get_file()
    path = "input_photo.jpg"
    await file.download_to_drive(path)

    img = Image.open(path)

    # Resize according to quality
    aspect = img.width / img.height
    new_height = quality
    new_width = int(aspect * new_height)

    img = img.resize((new_width, new_height))

    output = "enhanced_photo.jpg"
    img.save(output)

    await update.message.reply_photo(photo=open(output, "rb"))

    os.remove(path)
    os.remove(output)


# -------------------------
# PROCESS VIDEO
# -------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "video":
        return

    quality = context.user_data.get("video_quality", 720)

    file = await update.message.video.get_file()
    path = "input_video.mp4"
    await file.download_to_drive(path)

    clip = VideoFileClip(path)

    aspect = clip.w / clip.h
    new_height = quality
    new_width = int(aspect * new_height)

    clip_resized = clip.resize((new_width, new_height))
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
