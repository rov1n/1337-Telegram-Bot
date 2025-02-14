from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging, os, sqlite3, html
import config  # Import config file


myBotToken = config.TEST_BOT_TOKEN
# Adjust path for deployment environment
db_path = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user_details(user_id, first_name, last_name, username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)',
              (user_id, first_name, last_name, username))
    conn.commit()
    conn.close()

def get_user_ids():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return user_ids

def get_user_details(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT first_name, last_name, username FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

async def get_user_name(bot: Bot, chat_id: int, user_id: int):
    user_details = get_user_details(user_id)
    if user_details:
        first_name, last_name, username = user_details
        return first_name, last_name, username
    return None, None, None

# Initialize the database
init_db()

# Function to handle Instagram Reels links and store user details
async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or ""
    username = update.message.from_user.username or ""

    # Store user details in SQLite
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
# async def mention_all(update: Update, context):
#     chat_id = update.message.chat_id
#     bot = context.bot
#     try:
#         mention_message = "Attention everyone!\n\n"
#         user_ids = get_user_ids()
#         for user_id in user_ids:
#             first_name, last_name, username = await get_user_name(bot, chat_id, user_id)
#             if first_name:
#                 mention_message += f"[{first_name} {last_name}](tg://user?id={user_id})\n"
#         await update.message.reply_text(mention_message, parse_mode="Markdown")
#     except Exception as e:
#         print(f"Error fetching group members: {e}")
#         await update.message.reply_text("Sorry, I couldn't fetch the list of users.")


# With usernames
async def mention_all(update: Update, context):
    chat_id = update.message.chat_id
    bot = context.bot
    try:
        mention_message = "Attention everyone!\n\n"
        user_ids = get_user_ids()
        for user_id in user_ids:
            first_name, last_name, username = await get_user_name(bot, int(chat_id), int(user_id))
            # if first_name:
            #     mention_message += f"\n[{first_name}](tg://user?id={user_id}) "
            if username:
                mention_message += f"[@{html.escape(username)}](tg://user?id={user_id})\n"
            else:
                mention_message += f"[{html.escape(first_name)}](tg://user?id={user_id})\n"
        await update.message.reply_text(mention_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error fetching group members: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the list of users.")

# Function to kick a user from the chat
async def kick_user(bot: Bot, chat_id: int, user_id: int):
    try:
        await bot.kick_chat_member(chat_id, user_id)
        return True
    except Exception as e:
        print(f"Error kicking user {user_id}: {e}")
        return False

# Example command to kick a user
async def kick_command(update: Update, context):
    chat_id = update.message.chat_id
    user_id = int(context.args[0])
    bot = context.bot
    success = await kick_user(bot, chat_id, user_id)
    if success:
        await update.message.reply_text(f"User {user_id} has been kicked from the chat.")
    else:
        await update.message.reply_text(f"Failed to kick user {user_id}.")

# Main function to run the bot locally
def main():
    # Enable logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Create the Telegram application using the token from config
    application = Application.builder().token(myBotToken).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
    application.add_handler(CommandHandler("everyone", mention_all))
    application.add_handler(CommandHandler("kick", kick_command))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
