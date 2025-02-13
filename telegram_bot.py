from telegram import Update
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import config


# Function to handle Instagram Reels links
async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text

    # Check for Instagram Reels links
    if "instagram.com/reel/" in message_text:
        # Convert to ddinstagram.com link
        expanded_url = message_text.replace("instagram.com", "ddinstagram.com")
        await update.message.reply_text(f"Expanded Instagram Reels link: {expanded_url}")
    elif "x.com/" in message_text:
        # Convert to Twitter.com link
        expanded_url = message_text.replace("x.com", "fxtwitter.com")
        await update.message.reply_text(f"Expanded Twitter link: {expanded_url}")

# # Function to handle @all, @everybody, @everyone mentions
# async def handle_mentions(update: Update, context):
#     message_text = update.message.text.lower()

#     # Check for mention keywords
#     if "@all" in message_text or "@everybody" in message_text or "@everyone" in message_text:
#         # Get all members of the group
#         chat_id = update.message.chat_id
#         try:
#             members = await context.bot.get_chat_members(chat_id)
#             # Mention all users
#             mention_text = " ".join([f"@{member.user.username}" for member in members if member.user.username])
#             await update.message.reply_text(f"Mentioning all users: {mention_text}")
#         except Exception as e:
#             print(f"Error fetching group members: {e}")
#             await update.message.reply_text("Sorry, I couldn't fetch the list of users.")


# Function to handle the /everyone command
async def mention_all(update: Update, context):
    chat_id = update.message.chat_id
    bot = context.bot
    try:
        # Get all administrators of the group
        admins = await bot.get_chat_administrators(chat_id)
        mention_message = "Attention everyone!\n\n"
        for admin in admins:
            user = admin.user
            mention_message += f"[{user.first_name}](tg://user?id={user.id}) "
        await update.message.reply_text(mention_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error fetching group members: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the list of users.")


# Main function to run the bot locally
def main():
    # Create the Telegram application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mentions))
    application.add_handler(CommandHandler("everyone", mention_all))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()