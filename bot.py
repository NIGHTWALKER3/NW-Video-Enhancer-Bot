import os
from PIL import Image, ImageFilter
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ----------------------------------------------------------
# ADD YOUR BOT TOKEN HERE
# ----------------------------------------------------------
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"


# ----------------------------------------------------------
# /start
# ----------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the NW Enhancer Bot!\n\n"
        "Commands:\n"
        "/photo - Enhance Photo\n"
        "/video - Enhance Video\n"
    )


# ----------------------------------------------------------
# /photo command
# ----------------------------------------------------------
async def photo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "photo"
    await update.message.reply_text(
        "📸 Please send the *photo as a File* (Document).\n"
        "After that, choose quality."
    )


# ----------------------------------------------------------
# /video command
# ----------------------------------------------------------
async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "video"

    keyboard = [
        [InlineKeyboardButton("360p", callback_data="vid_360")],
        [InlineKeyboardButton("720p", callback_data="vid_720")],
        [InlineKeyboardButton("1080p", callback_data="vid_1080")],
    ]

    await update.message.reply_text(
        "🎥 Choose video quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ----------------------------------------------------------
# ASK PHOTO QUALITY
# ----------------------------------------------------------
async def ask_photo_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("360p", callback_data="img_360")],
        [InlineKeyboardButton("720p", callback_data="img_720")],
        [InlineKeyboardButton("1080p", callback_data="img_1080")],
    ]

    await update.message.reply_text(
        "📸 Choose photo quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ----------------------------------------------------------
# RECEIVE PHOTO AS FILE (DOCUMENT)
# ----------------------------------------------------------
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "photo":
        return

    # Save the Telegram file object
    context.user_data["photo_file"] = await update.message.document.get_file()

    # Ask for quality selection
    await ask_photo_quality(update, context)


# ----------------------------------------------------------
# PROCESS PHOTO (Enhance)
# ----------------------------------------------------------
async def process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, quality_value):
    tg_file = context.user_data.get("photo_file")

    if tg_file is None:
        await update.callback_query.edit_message_text("❌ Please send photo again as File.")
        return

    path = "input.jpg"
    await tg_file.download_to_drive(path)

    img = Image.open(path)

    aspect = img.width / img.height
    new_height = quality_value
    new_width = int(aspect * new_height)

    # Resize
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Enhancement Levels
    img_light = img_resized
    img_medium = img_resized.filter(ImageFilter.SHARPEN)
    img_strong = img_resized.filter(ImageFilter.DETAIL)

    # Save
    img_light.save("light.jpg")
    img_medium.save("medium.jpg")
    img_strong.save("strong.jpg")

    await update.callback_query.edit_message_text("✨ Enhanced versions ready!")

    # Send all versions
    await update.callback_query.message.reply_document(open("light.jpg", "rb"), caption="Light Enhanced")
    await update.callback_query.message.reply_document(open("medium.jpg", "rb"), caption="Medium Enhanced")
    await update.callback_query.message.reply_document(open("strong.jpg", "rb"), caption="Strong Enhanced")

    # Cleanup
    os.remove("light.jpg")
    os.remove("medium.jpg")
    os.remove("strong.jpg")
    os.remove(path)


# ----------------------------------------------------------
# CALLBACK BUTTON HANDLER
# ----------------------------------------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # PHOTO QUALITY HANDLER
    if data.startswith("img_"):
        quality = int(data.replace("img_", ""))
        await process_photo(update, context, quality)

    # (VIDEO NOT IMPLEMENTED YET — ONLY MESSAGE)
    elif data.startswith("vid_"):
        await query.edit_message_text("🎥 Video enhancement coming soon!")


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("photo", photo_cmd))
    app.add_handler(CommandHandler("video", video_cmd))

    # PHOTO as file
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    # If user sends normal photo
    app.add_handler(MessageHandler(filters.PHOTO, lambda u, c: u.message.reply_text(
        "⚠️ Please send the photo as *File* (Document)."
    )))

    # If user sends video without command
    app.add_handler(MessageHandler(filters.VIDEO, lambda u, c: u.message.reply_text(
        "Use /video to choose quality first."
    )))

    # Buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
