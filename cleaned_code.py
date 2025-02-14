from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import logging, os, sqlite3, html
import config  # Import config file
from pytube import YouTube  # Import YouTube library
import telebot

myBotToken = config.BOT_TOKEN
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

# Function to handle YouTube video downloads
async def handle_youtube_links_other(update: Update, context):
    bot = telebot.TeleBot(myBotToken)
    message_text = update.message.text
    if "youtube.com" in message_text or "youtu.be" in message_text:
        await update.message.reply_text("Which format would you like to download?\n1. Video (MP4)\n2. Audio (MP3)")

        # Handle the user's choice
        @bot.message_handler(func=lambda msg: msg.text in ['1', '2'])
        def handle_format_choice(msg):
            url = message_text
            yt = YouTube(url)
            if msg.text == '1':
                stream = yt.streams.get_highest_resolution()
                stream.download(output_path='downloads/', filename='video.mp4')
                bot.send_message(msg.chat.id, "Video downloaded successfully!")
                bot.send_document(msg.chat.id, open('downloads/video.mp4', 'rb'))
            elif msg.text == '2':
                stream = yt.streams.filter(only_audio=True).first()
                stream.download(output_path='downloads/', filename='audio.mp3')
                bot.send_message(msg.chat.id, "Audio downloaded successfully!")
                bot.send_document(msg.chat.id, open('downloads/audio.mp3', 'rb'))

#

#--------------------------------------------------
# Download YT videos

# Initialize the bot
bot = telebot.TeleBot(myBotToken)

# Function to handle YouTube video downloads
async def handle_youtube_links(update: Update, context):
    message_text = update.message.text
    if "youtube.com" in message_text or "youtu.be" in message_text:
        yt = YouTube(message_text)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        buttons = [[InlineKeyboardButton(f"{stream.resolution}", callback_data=f"download|{stream.itag}") for stream in streams]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Choose a resolution to download:", reply_markup=reply_markup)

# Function to download video
async def download_video(update: Update, context):
    query = update.callback_query
    data = query.data.split('|')
    if data[0] == 'download':
        itag = data[1]
        yt = YouTube(query.message.text)
        stream = yt.streams.get_by_itag(itag)
        stream.download(output_path='downloads/', filename='video.mp4')
        await query.message.reply_text("Video downloaded successfully!")
        await context.bot.send_document(query.message.chat_id, open('downloads/video.mp4', 'rb'))
        await query.answer()


#--------------------------------
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_links))
    application.add_handler(CallbackQueryHandler(download_video))
    application.add_handler(CommandHandler("everyone", mention_all))

    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
9