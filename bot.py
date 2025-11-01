import os
import telebot
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    return "Bot alive", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a video and I will pick the best frame! 🎬✨")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(os.getenv("WEBHOOK_URL"))
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
