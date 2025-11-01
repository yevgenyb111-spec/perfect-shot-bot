
import os
from flask import Flask, request
import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# 📸 Send welcome & logo on /start
@bot.message_handler(commands=['start'])
def start(message):
    logo_path = "logo.png"  # make sure logo is in repo
    caption = "🤖 *Perfect Shot Bot*\n\n📽️ Send me a short video & I will pick the best frame!"
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            bot.send_photo(message.chat.id, f, caption=caption, parse_mode="Markdown")
    else:
        bot.reply_to(message, caption)

# 🎬 Handle incoming video
@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "✅ Video received! Processing... Please wait ⏳")

    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded = bot.download_file(file_info.file_path)

        input_video_path = "input.mp4"
        output_image_path = "best_frame.png"

        with open(input_video_path, "wb") as f:
            f.write(downloaded)

        clip = VideoFileClip(input_video_path)
        frames = []
        duration = clip.duration
        step = duration / 10  # analyze 10 frames

        for i in range(10):
            t = i * step
            frame = clip.get_frame(t)
            frames.append(frame)

        # Pick sharpest frame
        import cv2
        import numpy as np

        best_score = -1
        best_frame = None

        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            score = cv2.Laplacian(gray, cv2.CV_64F).var()
            if score > best_score:
                best_score = score
                best_frame = frame

        best_frame_bgr = cv2.cvtColor(best_frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_image_path, best_frame_bgr)

        with open(output_image_path, "rb") as f:
            bot.send_photo(message.chat.id, f, caption="✨ Best frame found!")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error processing video:\n`{e}`", parse_mode="Markdown")

# Flask webhook endpoint
@app.route("/", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    # Set webhook if missing
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=5000)
