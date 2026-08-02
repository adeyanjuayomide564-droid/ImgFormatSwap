import os
import logging
from io import BytesIO
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

# Supported formats
SUPPORTED_FORMATS = {
    "JPEG": "JPEG",
    "PNG": "PNG", 
    "WEBP": "WEBP",
    "BMP": "BMP",
    "TIFF": "TIFF",
    "GIF": "GIF",
    "PDF": "PDF"
}

# User sessions to store the current image
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "I am **ImgFormatSwapBot**, your image format converter.\n\n"
        "📸 **How to use me:**\n"
        "1. Send me any image (JPG, PNG, WEBP, etc.)\n"
        "2. Choose the format you want to convert to\n"
        "3. I'll send back the converted image!\n\n"
        "🔹 **Supported formats:** JPEG, PNG, WEBP, BMP, TIFF, GIF, PDF\n\n"
        "Simply send me an image to get started! 🚀"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    help_text = (
        "🆘 **How to use this bot:**\n\n"
        "1️⃣ Send me any image (as a photo or file)\n"
        "2️⃣ I'll show you a list of formats\n"
        "3️⃣ Click on the format you want\n"
        "4️⃣ I'll send back the converted image!\n\n"
        "**Supported formats:**\n"
        "🖼 JPEG, 📸 PNG, 🌐 WEBP, 🖨 BMP, 📄 TIFF, 🎞 GIF, 📕 PDF\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/about - About this bot\n\n"
        "Send me an image to get started! 🚀"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about message."""
    about_text = (
        "🤖 **ImgFormatSwapBot**\n\n"
        "A simple and powerful image format converter for Telegram.\n\n"
        "**Features:**\n"
        "✅ Convert images to multiple formats\n"
        "✅ Support for photos and documents\n"
        "✅ High quality output (95% quality for JPEG)\n"
        "✅ Animated GIF support\n"
        "✅ PDF conversion\n\n"
        "**Technology:**\n"
        "🔹 Python 3.11+\n"
        "🔹 python-telegram-bot v20.0+\n"
        "🔹 Pillow (PIL) for image processing\n"
        "🔹 Deployed on Railway\n\n"
        "Enjoy converting! 🎨"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming images and show format selection."""
    user_id = update.effective_user.id
    
    try:
        # Get the image file
        photo = update.message.photo[-1]  # Get highest quality image
        file = await photo.get_file()
        
        # Download image
        image_bytes = await file.download_as_bytearray()
        
        # Store in session
        user_sessions[user_id] = {
            "image_bytes": image_bytes,
            "original_format": "Unknown"
        }
        
        # Create inline keyboard with format options
        keyboard = [
            [
                InlineKeyboardButton("🖼 JPEG", callback_data="JPEG"),
                InlineKeyboardButton("📸 PNG", callback_data="PNG"),
                InlineKeyboardButton("🌐 WEBP", callback_data="WEBP")
            ],
            [
                InlineKeyboardButton("🖨 BMP", callback_data="BMP"),
                InlineKeyboardButton("📄 TIFF", callback_data="TIFF"),
                InlineKeyboardButton("🎞 GIF", callback_data="GIF")
            ],
            [
                InlineKeyboardButton("📕 PDF", callback_data="PDF")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ Image received!\n\n"
            "**Choose the format you want to convert to:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error handling image: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't process your image. Please try again with a different image."
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image documents (non-photo image files)."""
    user_id = update.effective_user.id
    document = update.message.document
    
    try:
        # Check if it's an image
        mime_type = document.mime_type if document.mime_type else ""
        if not mime_type.startswith("image/"):
            await update.message.reply_text("❌ Please send an image file.")
            return
        
        # Download the document
        file = await document.get_file()
        image_bytes = await file.download_as_bytearray()
        
        # Store in session
        user_sessions[user_id] = {
            "image_bytes": image_bytes,
            "original_format": document.file_name.split(".")[-1].upper() if document.file_name else "Unknown"
        }
        
        # Show format selection
        keyboard = [
            [
                InlineKeyboardButton("🖼 JPEG", callback_data="JPEG"),
                InlineKeyboardButton("📸 PNG", callback_data="PNG"),
                InlineKeyboardButton("🌐 WEBP", callback_data="WEBP")
            ],
            [
                InlineKeyboardButton("🖨 BMP", callback_data="BMP"),
                InlineKeyboardButton("📄 TIFF", callback_data="TIFF"),
                InlineKeyboardButton("🎞 GIF", callback_data="GIF")
            ],
            [
                InlineKeyboardButton("📕 PDF", callback_data="PDF")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ Document received!\n\n"
            "**Choose the format you want to convert to:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't process your document. Please try again with a different image."
        )

async def handle_format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the format selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    format_choice = query.data
    
    if format_choice == "cancel":
        if user_id in user_sessions:
            del user_sessions[user_id]
        await query.edit_message_text("❌ Conversion cancelled. Send me another image when you're ready!")
        return
    
    # Get stored image
    if user_id not in user_sessions:
        await query.edit_message_text("❌ Session expired. Please send the image again.")
        return
    
    session_data = user_sessions[user_id]
    image_bytes = session_data["image_bytes"]
    
    try:
        # Show processing message
        await query.edit_message_text(f"🔄 Converting to {format_choice}... Please wait.")
        
        # Open image with PIL
        image = Image.open(BytesIO(image_bytes))
        
        # Handle GIF specially
        if format_choice == "GIF" and getattr(image, 'is_animated', False):
            # Save as animated GIF
            output = BytesIO()
            image.save(output, format="GIF", save_all=True, loop=0)
            output.seek(0)
        else:
            # Convert to RGB if needed (for JPEG, PDF)
            if format_choice in ["JPEG", "PDF"] and image.mode in ["RGBA", "P"]:
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[3] if len(image.split()) > 3 else None)
                else:
                    background.paste(image)
                image = background
            
            # Save converted image
            output = BytesIO()
            if format_choice == "PDF":
                # For PDF, save as a single-page PDF
                image.save(output, format="PDF", resolution=100.0)
            else:
                # Use optimize=True for better compression
                image.save(output, format=format_choice, quality=95, optimize=True)
            output.seek(0)
        
        # Send the converted image
        file_extension = format_choice.lower()
        file_name = f"converted.{file_extension}"
        
        if format_choice == "PDF":
            await query.message.reply_document(
                document=output,
                filename=file_name,
                caption=f"✅ Successfully converted to **{format_choice}**!",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_photo(
                photo=output,
                caption=f"✅ Successfully converted to **{format_choice}**!",
                parse_mode="Markdown"
            )
        
        # Clean up session
        if user_id in user_sessions:
            del user_sessions[user_id]
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        await query.message.reply_text(
            f"❌ Sorry, I couldn't convert this image to {format_choice}.\n"
            f"Error: {str(e)}\n\n"
            "Please try again with a different image or format."
        )
        if user_id in user_sessions:
            del user_sessions[user_id]

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        
        # Add message handlers
        application.add_handler(MessageHandler(filters.PHOTO, handle_image))
        application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(handle_format_selection))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("🤖 Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("🤖 Bot stopped.")
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
