from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
import config  # Import config file
from firebase_config import db  # Import Firebase config

# Function to add user details to Firestore
def add_user_details(user_id, first_name, last_name, username):
    doc_ref = db.collection('users').document(str(user_id))
    doc_ref.set({
        'first_name': first_name,
        'last_name': last_name,
        'username': username
    })

# Function to get all user IDs from Firestore
def get_user_ids():
    docs = db.collection('users').stream()
    return [doc.id for doc in docs]

# Function to fetch user's name
async def get_user_name(bot: Bot, chat_id: int, user_id: int):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        first_name = member.user.first_name
        last_name = member.user.last_name or ""
        username = member.user.username or ""
        return first_name, last_name, username
    except Exception as e:
        print(f"Error fetching user name: {e}")
        return None, None, None

# Function to handle Instagram Reels links and store user details
async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or ""
    username = update.message.from_user.username or ""

    # Store user details in Firestore
    add_user_details(user_id, first_name, last_name, username)

    # Check for Instagram Reels links
    if "instagram.com/reel/" in message_text:
        # Convert to ddinstagram.com link
        expanded_url = message_text.replace("instagram.com", "ddinstagram.com")
        await update.message.reply_text(f"Expanded Instagram Reels link: {expanded_url}")
    elif "x.com/" in message_text:
        # Convert to Twitter.com link
        expanded_url = message_text.replace("x.com", "fxtwitter.com")
        await update.message.reply_text(f"Expanded Twitter link: {expanded_url}")

# Function to handle the /everyone command
async def mention_all(update: Update, context):
    chat_id = update.message.chat_id
    bot = context.bot
    try:
        mention_message = "Attention everyone!\n\n"
        user_ids = get_user_ids()
        for user_id in user_ids:
            first_name, last_name, username = await get_user_name(bot, chat_id, int(user_id))
            if first_name:
                mention_message += f"\n[{first_name} {last_name}](tg://user?id={user_id}) "
        await update.message.reply_text(mention_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error fetching group members: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the list of users.")

# Main function to run the bot locally
def main():
    # Enable logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Create the Telegram application using the token from config
    application = Application.builder().token(config.TEST_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
    application.add_handler(CommandHandler("everyone", mention_all))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
