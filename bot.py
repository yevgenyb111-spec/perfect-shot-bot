
import telebot
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("7403753745:AAH4-ZoSXWa8858jbV8XE87gA0SZrjQCEa4")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "📸 Perfect Shot\n\nОтправь мне видео, и я выберу лучший кадр 👌")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Обрабатываю видео...")

    file_info = bot.get_file(message.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    video_path = "video.mp4"
    with open(video_path, "wb") as new_file:
        new_file.write(downloaded)

    # Создаем папку для кадров
    frames_dir = "frames"
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    # Извлекаем кадры через FFmpeg
    subprocess.call(f"ffmpeg -i {video_path} {frames_dir}/frame_%03d.jpg", shell=True)

    # Выбираем "лучший" кадр — пока просто берём средний
    files = sorted(os.listdir(frames_dir))
    if not files:
        bot.reply_to(message, "❌ Не удалось извлечь кадры")
        return

    best_frame = os.path.join(frames_dir, files[len(files)//2])

    # Отправляем фото пользователю
    with open(best_frame, "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption="✅ Лучший кадр")

    os.remove(video_path)

bot.infinity_polling()
