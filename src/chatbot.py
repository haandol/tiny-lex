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

    def _get_current_intent(self,
                            text: str,
                            intent_name: str) -> Tuple[bool, Intent]:
        is_new = False
        score, intent = self.dm.classify_intent(text)
        logging.info(f'{score}, {intent} for {text}')

        if intent:
            is_new = True
            return is_new, intent
        else:
            intent = self.dm.get_intent_by_name(intent_name)
            logging.info(f'user specified intent: {intent}')
        return is_new, intent

    def chat(self,
             uid: str,
             text: str,
             intent_name: str = None,
             user_slot_values: dict = None) -> Tuple[str, str, dict]:
        logging.info(f'[USER][{uid}]: {text}')

        is_new, intent = self._get_current_intent(text, intent_name)
        if not intent:
            return f'처리할 수 없는 메시지입니다: [{text}]'

        # if new intent is identified, start over fulfilling slots
        if is_new:
            user_slot_values = None

        is_fulfilled, new_slot_values, prompt = self.dm.fulfill_intent(
            intent, user_slot_values, text
        )

        if user_slot_values:
            user_slot_values.update(new_slot_values)
        else:
            user_slot_values = new_slot_values

        response = prompt.format(**user_slot_values)
        if is_fulfilled:
            # TODO: confirm or reject
            pass

        return response, intent.name, user_slot_values


if __name__ == '__main__':
    bot = Chatbot(start_message='안녕하세요, 꽃팔이 챗봇입니다.')
    uid = 'dongkyl'
    resp, intent_name, slot_values = bot.chat(uid, '꽃을 사고 싶어')
    logging.info(f"[BOT]: {resp}")
    resp, intent_name, slot_values = bot.chat(uid, '장미', intent_name, slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, intent_name, slot_values = bot.chat(uid, '2021년 12월 6일', intent_name, slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, intent_name, slot_values = bot.chat(uid, '13시 50분', intent_name, slot_values)
    logging.info(f"[BOT]: {resp}")

    resp, intent_name, slot_values = bot.chat(uid, '꽃을 사고 싶어')
    logging.info(f"[BOT]: {resp}")
    resp, intent_name, slot_values = bot.chat(uid, '장미', intent_name, slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, intent_name, slot_values = bot.chat(uid, '꽃을 사고 싶어', intent_name, slot_values)
    logging.info(f"[BOT]: {resp}")
    resp, intent_name, slot_values = bot.chat(uid, '13시 50분', intent_name, slot_values)
    logging.info(f"[BOT]: {resp}")
