import telebot
import time
from instabot.settings import HOST, TG_TOKEN


bot = telebot.TeleBot(TG_TOKEN, threaded=False)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://{}/bot/{}".format(HOST, TG_TOKEN))
