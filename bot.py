import os
from flask import Flask, request
import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

# ✅ Env variables
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ Start command
@bot.message_handler(commands=['start'])
def start(message):
    logo_path = "logo.png"
    caption = "🤖 *Perfect Shot Bot*\n\nSend me a video and I will pick the best frame 📸"

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as logo:
            bot.send_photo(message.chat.id, logo, caption=caption, parse_mode="Markdown")
    else:
        bot.reply_to(message, caption, parse_mode="Markdown")


# ✅ Handle video
@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "🎬 Video received! Processing... Please wait ⏳")

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    video_path = "input.mp4"
    with open(video_path, "wb") as f:
        f.write(downloaded_file)

    # ✅ Extract middle frame
    clip = VideoFileClip(video_path)
    best_frame_time = clip.duration / 2

    frame = clip.get_frame(best_frame_time)
    frame_path = "best_frame.png"
    Image.fromarray(frame).save(frame_path)

    # ✅ Send back frame
    with open(frame_path, "rb") as frame_file:
        bot.send_photo(message.chat.id, frame_file, caption="✨ Best frame extracted!")

    clip.close()
    os.remove(video_path)
    os.remove(frame_path)


# ✅ Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    return "Wrong content", 403


# ✅ Render health check
@app.route('/', methods=['GET'])
def home():
    return "Perfect Shot Bot ✅"


# ✅ Start server
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=5000)
