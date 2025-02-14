import json
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

# Replace with your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Function to handle Instagram Reels links
async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text

    # Check for Instagram Reels links
    if "instagram.com/reel/" in message_text:
        # Convert to ddinstagram.com link
        expanded_url = message_text.replace("instagram.com", "ddinstagram.com")
        await update.message.reply_text(f"Expanded Instagram Reels link: {expanded_url}")

# Function to handle @all, @everybody, @everyone mentions
async def handle_mentions(update: Update, context):
    message_text = update.message.text.lower()

    # Check for mention keywords
    if "@all" in message_text or "@everybody" in message_text or "@everyone" in message_text:
        # Get all members of the group
        chat_id = update.message.chat_id
        members = await context.bot.get_chat_members(chat_id)

        # Mention all users
        mention_text = " ".join([f"@{member.user.username}" for member in members if member.user.username])
        await update.message.reply_text(f"Mentioning all users: {mention_text}")

# Lambda handler function
def lambda_handler(event, context):
    # Create the Telegram application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mentions))

    # Process the update
    try:
        update = Update.de_json(json.loads(event["body"]), application.bot)
        application.process_update(update)
    except Exception as e:
        print(f"Error processing update: {e}")

    return {
        "statusCode": 200,
        "body": "OK"
    }