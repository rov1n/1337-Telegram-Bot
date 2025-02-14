from telegram import Update, Contact, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging, os, sqlite3, html
import config  # Import config file

# import datetime

myBotToken = config.LEXI_TOKEN
# Adjust path for deployment environment
db_path = os.path.join(os.path.dirname(__file__), 'users.db')

# cooldown_duration = datetime.timedelta(minutes=2)
# last_use_time = None  # Initialize last use time

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

def add_or_update_user_details(user_id, first_name, last_name, username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (user_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            username=excluded.username
    ''', (user_id, first_name, last_name, username))
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

async def get_user_details_from_api(bot, user_id):
    user = await bot.get_chat(user_id)
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username
    }

# Initialize the database
init_db()

# Function to handle Instagram Reels links and store user details
# Function to handle Instagram Reels links and store user details
async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or ""
    username = update.message.from_user.username or ""
    # Store or update user details in SQLite
    add_or_update_user_details(user_id, first_name, last_name, username)
    # Check for Instagram Reels links
    if "instagram.com/" in message_text:
        # Convert to ddinstagram.com link
        expanded_url = message_text.replace("instagram.com", "ddinstagram.com")
        await update.message.reply_text(f"Expanded Instagram Reels link: \n{expanded_url}")
    elif "x.com/" in message_text:
        # Convert to Twitter.com link
        expanded_url = message_text.replace("x.com", "fxtwitter.com")
        await update.message.reply_text(f"Expanded Twitter link: \n{expanded_url}")


# With usernames
async def mention_all(update: Update, context):
    chat_id = update.message.chat_id
    bot = context.bot
    try:
        mention_message = "Attention everyone!\n\n"
        user_ids = get_user_ids()
        for user_id in user_ids:
            first_name, last_name, username = await get_user_name(bot, chat_id, int(user_id))
            if username:
                mention_message += f"[@{html.escape(username)}](tg://user?id={user_id})\n"
            else:
                full_name = f"{first_name}".strip()  # Ensure there are no extra spaces
                mention_message += f"[{full_name}](tg://user?id={user_id})\n"
        await update.message.reply_text(mention_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error fetching group members: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the list of users.")

'''
#--------------New addition-----------
async def get_user_details_from_api(bot, user_id):
    user = await bot.get_chat(user_id)
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username
    }

async def handle_contact(update: Update, context):
    contact: Contact = update.message.contact
    user_id = contact.user_id
    first_name = contact.first_name
    last_name = contact.last_name or ""
    phone_number = contact.phone_number
    vcard = contact.vcard or ""
    
    # Retrieve the user's username using the user_id
    user_details = await get_user_details_from_api(context.bot, user_id)
    username = user_details.get('username', "")

    # Store or update user details in SQLite
    add_or_update_user_details(user_id, first_name, last_name, username)

    await update.message.reply_text(f"User ID: {user_id}\nName: {first_name} {last_name}\nPhone: {phone_number}\nUsername: {username}")

async def fetch_user_ids_command(update: Update, context):
        user_ids = get_user_ids()
        user_details_list = []
        for user_id in user_ids:
            first_name, last_name, username = get_user_details(user_id)
            user_details_list.append(f"{user_id} - {first_name} {last_name} (@{username})")
        user_details_str = "\n".join(user_details_list)
        await update.message.reply_text(f"Stored User Details:\n{user_details_str}")

'''
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


    # #temp
    # application.add_handler(CommandHandler("fetch", fetch_user_ids_command))
    # application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
