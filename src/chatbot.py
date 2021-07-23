import os
import logging
from typing import Tuple
from .libs.dialog import DialogManager
from .libs.intent import Intent, Slot, SlotType
from .libs.nlu import NLU

logging.basicConfig(level=logging.INFO)
CONFIG_PATH = os.path.join(os.getcwd(), 'config')


class Chatbot(object):
    def __init__(self, start_message: str):
        self.nlu = NLU(max_length=64)
        slot_types = SlotType.load_slot_types(
            os.path.join(CONFIG_PATH, 'slot_type.yml')
        )
        slots = Slot.load_slots(
            slot_types,
            os.path.join(CONFIG_PATH, 'slot.yml')
        )
        intents = Intent.load_intents(
            slots,
            os.path.join(CONFIG_PATH, 'intent.yml'),
            self.nlu.encode
        )

        self.dm = DialogManager(
            encoder=self.nlu.encode,
            intents=intents,
        )
        self.start_message = start_message
        self.user_intents = {}

    def _init_user_session(self, uid: str) -> None:
        self.user_intents[uid] = None

    def _get_current_intent(self, uid: str, text: str) -> Intent:
        score, intent = self.dm.classify_intent(text)
        if intent:
            logging.info(f'{score}, {intent.name}')
            self.user_intents[uid] = intent
        else:
            logging.warning(f'no intent for {uid} - {text}')
            intent = self.user_intents[uid]
        return intent

    def chat(self,
             uid: str,
             text: str,
             user_slot_values: dict = None) -> Tuple[str, dict]:
        logging.info(f'[USER][{uid}]: {text}')

        if uid not in self.user_intents:
            logging.info(f'init user intent for {uid}')
            self._init_user_session(uid)

        intent = self._get_current_intent(uid, text)
        if not intent:
            return f'처리할 수 없는 메시지입니다: [{text}]'

        is_fulfilled, new_slot_values, prompt = self.dm.fulfill_intent(
            intent, user_slot_values, text
        )

        if user_slot_values:
            user_slot_values.update(new_slot_values)
        else:
            user_slot_values = new_slot_values

        response = prompt.format(**user_slot_values)
        if is_fulfilled:
            self._init_user_session(uid)

        return response, user_slot_values


if __name__ == '__main__':
    bot = Chatbot(start_message='안녕하세요, 꽃팔이 챗봇입니다.')
    uid = 'dongkyl'
    resp, slot_values = bot.chat(uid, '꽃을 사고 싶어')
    logging.info(f"[BOT]: {resp}")
    resp, slot_values = bot.chat(uid, '장미', slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, slot_values = bot.chat(uid, '2021년 12월 6일', slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, slot_values = bot.chat(uid, '13시 50분', slot_values)
    logging.info(f"[BOT]: {resp}")

    resp, slot_values = bot.chat(uid, '꽃을 사고 싶어')
    logging.info(f"[BOT]: {resp}")
    resp, slot_values = bot.chat(uid, '장미', slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, slot_values = bot.chat(uid, '꽃을 사고 싶어', slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, slot_values = bot.chat(uid, '13시 50분', slot_values)
    logging.info(f"[BOT]: {resp}")
