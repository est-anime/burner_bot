import os
import telebot
from moviepy.editor import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import requests
from tempfile import NamedTemporaryFile

TOKEN = '6422706778:AAEkiNY4Qo65d3tZWfRYYlkeHVaLA3FnleU'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome to Video Encoder! Send video to burn subtitles.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.send_message(message.chat.id, "Received a video. Now please send the subtitle file (in .srt or .ass format) for burning into the video.")
    # Store the received video message and user chat ID for later use
    bot.register_next_step_handler(message, process_subtitle)

def process_subtitle(message):
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        subtitle_extension = message.document.file_name.split('.')[-1].lower()
        if subtitle_extension not in ['srt', 'ass']:
            bot.send_message(message.chat.id, "Invalid subtitle file format. Please send a .srt or .ass file.")
        else:
            bot.send_message(message.chat.id, "Processing... This may take some time.")
            start_time = time.time()
            video_path = download_file(file_path)
            subtitle_path = download_file(file_path)
            video_with_subtitles = burn_subtitles(video_path, subtitle_path)
            end_time = time.time()
            processing_time = end_time - start_time
            bot.send_message(message.chat.id, f"Processing time: {processing_time:.2f} seconds")
            bot.send_video(message.chat.id, open(video_with_subtitles, 'rb'))

def download_file(file_path):
    file_info = bot.get_file(file_path)
    response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_path))
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(response.content)
        return temp_file.name

def burn_subtitles(video_path, subtitle_path):
    video = VideoFileClip(video_path)
    subtitles = SubtitlesClip(subtitle_path)
    final_video = video.set_subtitles(subtitles)
    output_path = 'output_video.mp4'
    final_video.write_videofile(output_path)
    return output_path

if __name__ == '__main__':
    bot.polling(none_stop=True)
