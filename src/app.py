import logging
from dm import DialogManager
from nlu import NLU

class Chatbot(object):
    def __init__(self, start_message: str):
        nlu = NLU(max_length=64)
        self.dm = DialogManager(nlu=nlu)
        self.start_message = start_message
        self.sessions = {}

    def start(self, uid):
        self.sessions[uid] = None
        return self.start_message

    def chat(self, uid, text) -> str:
        current_intent = self.sessions[uid]
        if not current_intent:
            score, intent = self.dm.classify_intent(text)
            if not intent:
                return '처리할 수 없는 메시지 입니다.'
            logging.info(score, intent.name)
            current_intent = intent
        
        return self.dm.fulfill_intent(current_intent, text)


if __name__ == '__main__':
    bot = Chatbot(start_message='안녕하세요, 꽃팔이 챗봇입니다.')
    uid = 'dongkyl'
    print(bot.start(uid))
    print(bot.chat(uid, '꽃을 사고 싶어'))
    print(bot.chat(uid, '장미'))
    print(bot.chat(uid, '오늘'))
    print(bot.chat(uid, '지금'))