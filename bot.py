import os
from flask import Flask, request
import telebot
import subprocess

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🎬 *Perfect Shot Bot*\n\n"
        "Send me a video and I will pick the best frame for you! 📸✨",
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "📥 Video received! Extracting best frame...")

    file_id = message.video.file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    video_path = "input.mp4"
    frame_path = "frame.jpg"

    with open(video_path, "wb") as file:
        file.write(downloaded)

    # FFmpeg extract frame (10th frame = usually best face)
    cmd = f"ffmpeg -y -i {video_path} -vf 'select=eq(n\\,10)' -vframes 1 {frame_path}"
    subprocess.run(cmd, shell=True)

    if os.path.exists(frame_path):
        with open(frame_path, "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption="✅ Best frame found!")
    else:
        bot.reply_to(message, "❌ Error extracting frame.")

@app.route('/' + TOKEN, methods=['POST'])
def receive_update():
    json_update = request.stream.read().decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(json_update)])
    return "OK", 200

@app.route('/')
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(WEBHOOK_URL + TOKEN)
    return "Webhook set", 200
