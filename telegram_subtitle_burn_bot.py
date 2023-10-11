import os
import telebot
from moviepy.editor import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import requests
from tempfile import NamedTemporaryFile

# Your Telegram bot token
TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Command to start the bot
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome to Video Encoder! Send a video to burn subtitles.")

def download_file(file_path, chat_id):
    file_info = bot.get_file(file_path)
    if not file_info:
        bot.send_message(chat_id, "Error: File not found or unavailable.")
        return None

    response = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}')
    if response.status_code != 200:
        bot.send_message(chat_id, f"Error: Failed to download the file. Status code: {response.status_code}")
        return None

    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(response.content)
        return temp_file.name

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.send_message(message.chat.id, "Received a video. Now please send the subtitle file (in .srt or .ass format) for burning into the video.")
    # Store the received video message and user chat ID for later use
    bot.register_next_step_handler(message, process_subtitle)

def process_subtitle(message):
    chat_id = message.chat.id
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_path = download_file(file_id, chat_id)
        if not file_path:
            return
        subtitle_extension = message.document.file_name.split('.')[-1].lower()
        if subtitle_extension not in ['srt', 'ass']:
            bot.send_message(chat_id, "Invalid subtitle file format. Please send a .srt or .ass file.")
        else:
            bot.send_message(chat_id, "Processing... This may take some time.")
            video_path = download_file(file_id, chat_id)
            if not video_path:
                return

            video_with_subtitles = burn_subtitles(video_path, file_path, chat_id)

            if video_with_subtitles:
                bot.send_message(chat_id, "Processing complete. Sending the video...")
                bot.send_video(chat_id, open(video_with_subtitles, 'rb'))
            else:
                bot.send_message(chat_id, "An error occurred during processing.")

def burn_subtitles(video_path, subtitle_path, chat_id):
    try:
        video = VideoFileClip(video_path)
    except Exception as e:
        bot.send_message(chat_id, f"Error opening the video file: {str(e)}")
        return None

    subtitles = SubtitlesClip(subtitle_path)
    
    try:
        final_video = video.set_subtitles(subtitles)
    except Exception as e:
        bot.send_message(chat_id, f"Error adding subtitles: {str(e)}")
        return None

    output_path = 'output_video.mp4'
    try:
        final_video.write_videofile(output_path)
    except Exception as e:
        bot.send_message(chat_id, f"Error writing the final video: {str(e)}")
        return None

    return output_path

if __name__ == '__main__':
    bot.polling(none_stop=True)
