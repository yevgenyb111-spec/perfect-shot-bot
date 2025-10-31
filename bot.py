import telebot
import requests
import os

TOKEN = "7403753745:AAH4-ZoSXWa8858jbV8XE87gA0SZrjQCEa4"
COLAB_PROCESS_URL = "https://your-colab-url/run"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "📸 *Perfect Shot*\n\n"
        "Отправь мне видео, и я выберу лучший кадр 👌",
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "⏳ Обрабатываю видео...")

    file_info = bot.get_file(message.video.file_id)
    file = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}")

    file_path = "input.mp4"
    with open(file_path, "wb") as f:
        f.write(file.content)

    files = {"file": open(file_path, "rb")}
    response = requests.post(COLAB_PROCESS_URL, files=files)

    if response.status_code == 200:
        with open("output.png", "wb") as f:
            f.write(response.content)
        bot.send_photo(message.chat.id, open("output.png", "rb"), caption="✅ Лучший кадр!")
    else:
        bot.reply_to(message, "❌ Ошибка сервера. Попробуйте позже.")

    os.remove(file_path)
    if os.path.exists("output.png"):
        os.remove("output.png")

bot.infinity_polling()
