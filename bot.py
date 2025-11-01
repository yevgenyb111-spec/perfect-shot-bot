
from flask import Flask, request
import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import os

# Получаем токен из переменной среды Render
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "📸 Perfect Shot\n\n"
        "Отправь мне видео, и я выберу лучший кадр 👌"
    )

# Обработка видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Обрабатываю видео...")

    # Скачиваем файл
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    video_path = "video.mp4"
    frame_path = "best_frame.jpg"

    # Сохраняем видео
    with open(video_path, "wb") as new_file:
        new_file.write(downloaded_file)

    # Извлекаем кадр из середины
    clip = VideoFileClip(video_path)
    frame = clip.get_frame(clip.duration / 2)
    img = Image.fromarray(frame)
    img.save(frame_path)

    # Отправляем фото обратно
    with open(frame_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption="✅ Лучший кадр готов!")

# Webhook обработчик
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Просто проверка, что сервер запущен
@app.route('/')
def index():
    return "Bot is running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
