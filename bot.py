
import telebot
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import face_recognition
import numpy as np

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

def score_frame(frame):
    rgb = frame[:, :, ::-1]
    faces = face_recognition.face_locations(rgb)
    
    if len(faces) == 0:
        return 0
    
    face_encodings = face_recognition.face_encodings(rgb, faces)
    sharpness = np.mean(np.abs(np.gradient(frame.astype("float"))))
    
    return sharpness * len(face_encodings)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🤖 *Perfect Shot Bot*\n"
        "Send me a video and I'll choose your best frame 📸✨",
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Processing your video... please wait")

    file_info = bot.get_file(message.video.file_id)
    file_path = file_info.file_path
    downloaded = bot.download_file(file_path)

    video_name = "input_video.mp4"
    with open(video_name, 'wb') as new_file:
        new_file.write(downloaded)

    clip = VideoFileClip(video_name)
    frames = []
    
    for t in np.linspace(0, clip.duration, num=20):
        frame = clip.get_frame(t)
        score = score_frame(frame)
        frames.append((score, frame))

    best = max(frames, key=lambda x: x[0])

    best_img = Image.fromarray(best[1])
    result_path = "best_frame.jpg"
    best_img.save(result_path)

    with open(result_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="✅ Best frame found!")

    clip.close()
    os.remove(video_name)
    os.remove(result_path)

bot.polling()
