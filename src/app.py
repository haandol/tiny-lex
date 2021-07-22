import os
import logging
from libs.dialog import DialogManager
from libs.intent import Intent, Slot, SlotType
from libs.nlu import NLU

CONFIG_PATH = os.path.join(os.getcwd(), '..', 'config')


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
            intent_threshold=0.6
        )
        self.start_message = start_message
        self.user_intents = {}
        self.user_slot_values = {}

    def _init_user_session(self, uid: str) -> None:
        self.user_intents[uid] = None
        self.user_slot_values[uid] = {}

    def start(self, uid: str) -> str:
        self._init_user_session(uid)
        return self.start_message

    def _get_user_intent(self, uid: str, text: str) -> Intent:
        intent = self.user_intents[uid]
        if intent:
            return intent

        score, intent = self.dm.classify_intent(text)
        if not intent:
            return None
        logging.info(score, intent.name)
        self.user_intents[uid] = intent
        return intent
 
    def chat(self, uid: str, text: str) -> str:
        print(f'[USER]: {text}')
        intent = self._get_user_intent(uid, text)
        if not intent:
            return f'처리할 수 없는 메시지입니다: [{text}]'
        is_fulfilled, new_slot_values, prompt = self.dm.fulfill_intent(
            intent, self.user_slot_values[uid], text
        )
        self.user_slot_values[uid].update(new_slot_values)
        logging.info(text, new_slot_values, self.user_slot_values[uid])
        response = prompt.format(**self.user_slot_values[uid])
        if is_fulfilled:
            self._init_user_session(uid)
        logging.info(is_fulfilled, new_slot_values, prompt)
        return response


if __name__ == '__main__':
    bot = Chatbot(start_message='안녕하세요, 꽃팔이 챗봇입니다.')
    uid = 'dongkyl'
    print(f"[BOT]: {bot.start(uid)}")
    print(f"[BOT]: {bot.chat(uid, '꽃을 사고 싶어')}")
    print(f"[BOT]: {bot.chat(uid, '장미')}")
    print(f"[BOT]: {bot.chat(uid, '2021년 12월 6일')}")
    print(f"[BOT]: {bot.chat(uid, '13시 40분')}")