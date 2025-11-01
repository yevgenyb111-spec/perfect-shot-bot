import os
import telebot
from moviepy.editor import VideoFileClip
from PIL import Image

# ✅ Bot token
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ✅ Start command
@bot.message_handler(commands=['start'])
def start(message):
    caption = "🤖 *Perfect Shot Bot*\n\nSend me a video and I will pick the best frame for you! 🎬✨"
    bot.reply_to(message, caption, parse_mode="Markdown")

# ✅ Handle video
@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "🎬 Video received! Processing... Please wait!")

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    video_path = "input.mp4"
    with open(video_path, "wb") as f:
        f.write(downloaded_file)

    clip = VideoFileClip(video_path)
    best_frame_time = clip.duration / 2  
    frame = clip.get_frame(best_frame_time)

    frame_path = "best_frame.png"
    Image.fromarray(frame).save(frame_path)

    with open(frame_path, "rb") as frame_file:
        bot.send_photo(message.chat.id, frame_file, caption="✨ Best frame selected!")

    clip.close()
    os.remove(video_path)
    os.remove(frame_path)

# ✅ Run bot
bot.polling(none_stop=True)
