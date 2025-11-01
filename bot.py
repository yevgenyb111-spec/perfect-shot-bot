
import os
from flask import Flask, request
import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=True)

app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📸 Perfect Shot Bot готов!\nПришли видео — выберу лучший кадр 😎")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Обрабатываю видео...")
    # здесь позже добавим выбор кадра
    bot.reply_to(message, "✅ Видео получено! Обработка скоро будет 😊")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://perfect-shot-bot-1.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
