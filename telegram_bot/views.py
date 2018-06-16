from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from telebot.types import Update
from telegram_bot import bot
from instagram_bot.views import *


class CommandReceiveView(CreateAPIView):
    def post(self, request, *args, **kwargs):

        if len(request.data) == 0:
            return Response({'error': 'no data'}, status=HTTP_400_BAD_REQUEST)

        update = Update.de_json(request.data)
        bot.process_new_updates([update])

        return Response({'status': 'OK'}, status=HTTP_200_OK)


@bot.message_handler(commands=['start'])
def start(message):
    test = InstaBot(1)
