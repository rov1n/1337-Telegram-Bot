from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
import config

# Functions to handle file operations for user IDs
def read_user_ids(file_path='user_ids.txt'):
    try:
        with open(file_path, 'r') as file:
            user_ids = {int(line.strip()) for line in file}
    except FileNotFoundError:
        user_ids = set()
    return user_ids

def write_user_id(user_id, file_path='user_ids.txt'):
    user_ids = read_user_ids(file_path)
    user_ids.add(user_id)
    with open(file_path, 'w') as file:
        for uid in user_ids:
            file.write(f"{uid}\n")

# Function to handle Instagram Reels links and store user IDs
async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text
    user_id = update.message.from_user.id

    # Store user ID in the text file
    write_user_id(user_id)

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
        user_ids = read_user_ids()
        for user_id in user_ids:
            member = await bot.get_chat_member(chat_id, user_id)
            mention_message += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
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

    # Create the Telegram application
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
    application.add_handler(CommandHandler("everyone", mention_all))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
