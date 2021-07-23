import os
import sys
import json
import logging
sys.path.append(os.getcwd())
from src.chatbot import Chatbot

logging.basicConfig(level=logging.INFO)

bot = None


def handler(event, context):
    logging.info(json.dumps(event))

    global bot
    if not bot:
        bot = Chatbot(start_message='안녕하세요, 꽃팔이 챗봇입니다.')

    uid = event['uid']
    text = event['text']
    user_slot_values = json.loads(event.get('user_slot_values', '{}'))

    return bot.chat(uid=uid, text=text, user_slot_values=user_slot_values)
