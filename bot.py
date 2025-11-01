import os
import telebot
import tempfile
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np

# ✅ Загружаем переменные среды, если есть dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ✅ Читаем токен (Render / .env)
BOT_TOKEN = os.environ.get("7403753745:AAH4-ZoSXWa8858jbV8XE87gA0SZrjQCEa4")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message,
        "📸 *Perfect Shot*\n\nОтправь мне видео, и я выберу лучший кадр 👌",
        parse_mode="Markdown"
    )

def choose_best_frame(video_path):
    clip = VideoFileClip(video_path)

    best_frame = None
    best_score = -1

    for t in np.arange(0, clip.duration, 0.3):  # берём кадр каждые 0.3 сек
        frame = clip.get_frame(t)
        gray = np.mean(frame)  # простая эвристика — яркость картинки
        if gray > best_score:
            best_score = gray
            best_frame = frame

    frame_img = Image.fromarray(best_frame)
    return frame_img

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Обрабатываю видео...")

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(downloaded_file)
        temp_video_path = temp_video.name

    try:
        best_frame = choose_best_frame(temp_video_path)

        result_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        best_frame.save(result_path)

        with open(result_path, "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption="✅ Лучший кадр найден!")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка обработки: {e}")
    finally:
        os.remove(temp_video_path)

# ✅ Запуск
if __name__ == "__main__":
    bot.polling(none_stop=True)
