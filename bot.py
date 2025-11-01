import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📸 Perfect Shot\n\nОтправь мне видео, и я выберу лучший кадр 👌")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Обрабатываю видео...")

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    video_path = "input.mp4"
    with open(video_path, 'wb') as f:
        f.write(downloaded_file)

    clip = VideoFileClip(video_path)

    # кадр из середины видео
    frame_time = clip.duration / 2
    frame = clip.get_frame(frame_time)

    frame_image = Image.fromarray(frame)
    frame_path = "best_frame.jpg"
    frame_image.save(frame_path)

    clip.close()

    with open(frame_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="✅ Лучший кадр найден!")

    os.remove(video_path)
    os.remove(frame_path)

print("Bot started")
bot.polling(none_stop=True)
