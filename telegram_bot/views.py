from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from threading import Thread
import json

from config import TG_TOKEN
from .bot import TgBotHandler


class CommandReceiveView(View):
    def post(self, request, bot_token):

        if bot_token != TG_TOKEN:
            return HttpResponseForbidden('Invalid token')

        try:
            data = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            chat_id = data['message']['chat']['id']
            cmd = data['message'].get('text')
            tg_bot = TgBotHandler(chat_id)

            commands = {
                '/parse': tg_bot.parse_users_handler,
                '/like': tg_bot.like_handler,
            }

            func = commands.get(cmd.split()[0].lower())
            if func:
                tg_bot.send_message(chat_id, 'Function was activated')
                t = Thread(target=func, args=(chat_id,))
                t.start()
            else:
                tg_bot.send_message(chat_id, 'I do not understand you!')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
