import os
import telebot
from PIL import Image
from moviepy.editor import VideoFileClip
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)  # просто healthcheck для Render

@bot.message_handler(commands=['start'])
def start(message):
    caption = "🤖 *Perfect Shot Bot*\n\nSend me a video and I will pick the best frame."
    try:
        with open("logo.png", "rb") as f:
            bot.send_photo(message.chat.id, f, caption=caption, parse_mode="Markdown")
    except FileNotFoundError:
        bot.reply_to(message, caption, parse_mode="Markdown")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "🎬 Video received! Processing... Please wait.")
    file_info = bot.get_file(message.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    video_path = "input.mp4"
    with open(video_path, "wb") as f:
        f.write(downloaded)

    # Берём середину
    clip = VideoFileClip(video_path)
    t = clip.duration / 2
    frame = clip.get_frame(t)
    frame_img = Image.fromarray(frame)
    frame_path = "best_frame.png"
    frame_img.save(frame_path)
    clip.close()
    os.remove(video_path)

    with open(frame_path, "rb") as f:
        bot.send_photo(message.chat.id, f, caption="✨ Best frame")
    os.remove(frame_path)

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

if __name__ == "__main__":
    # В polling нет холодного старта вебхука — надёжнее на Free
    bot.remove_webhook()
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
