import telebot
from pytube import YouTube
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config # Import your config file

API_TOKEN = config.TEST_BOT_TOKEN
bot = telebot.TeleBot(API_TOKEN)
# Store user choices in a dictionary
user_choices = {}

# Function to handle YouTube links
@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
def handle_message(message):
    url = message.text
    user_choices[message.chat.id] = url  # Store the URL for the user

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    btn1 = telebot.types.KeyboardButton('Download Video')
    btn2 = telebot.types.KeyboardButton('Download Audio')
    markup.add(btn1, btn2)
    
    bot.reply_to(message, "Choose the format to download:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Download Video', 'Download Audio'])
def handle_download(message):
    url = user_choices.get(message.chat.id)  # Retrieve the stored URL
    if not url:
        bot.send_message(message.chat.id, "Error: No URL found.")
        return
    
    try:
        yt = YouTube(url)
    except exceptions.AgeRestrictedError:
        bot.send_message(message.chat.id, "Error: Age-restricted content.")
        return
    except exceptions.LiveStreamError:
        bot.send_message(message.chat.id, "Error: Live stream content cannot be downloaded.")
        return
    except exceptions.VideoUnavailable:
        bot.send_message(message.chat.id, "Error: Video unavailable.")
        return
    except exceptions.PytubeError:
        bot.send_message(message.chat.id, "Error: An error occurred while processing the video.")
        return

    if message.text == 'Download Video':
        try:
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path='downloads/', filename='video.mp4')
            bot.send_message(message.chat.id, "Video downloaded successfully!")
            bot.send_document(message.chat.id, open('downloads/video.mp4', 'rb'))
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {str(e)}")
    elif message.text == 'Download Audio':
        try:
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(output_path='downloads/', filename='audio.mp3')
            bot.send_message(message.chat.id, "Audio downloaded successfully!")
            bot.send_document(message.chat.id, open('downloads/audio.mp3', 'rb'))
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {str(e)}")

bot.polling()