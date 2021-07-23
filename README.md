# Tiny Lex

Tiny version of Amazon Lex for Korean chatbot prototype


# Usage

```bash
$ pip install -r requirements.txt

$ cd src
$ python app.py

INFO:root:{'name': 'flower', 'utterances': ['꽃을 사고 싶습니다', '꽃을 사고 싶다', '꽃 내놔', '꽃이 필요해', '플라워가 필요해', '플라워를 사고 싶다'], 'confirm_prompt': '좋습니다. {pickup_date} {pickup_time}에 {kinds} 꽃을 준비해두겠습니다.'}
INFO:root:[BOT]: 안녕하세요, 꽃팔이 챗봇입니다.
INFO:root:[USER]: 꽃을 사고 싶어
INFO:root:0.8072117893407781, flower
WARNING:root:Invalid value for slot [kinds]: {}, 꽃을 사고 싶어
INFO:root:[BOT]: 무슨 종류의 꽃을 사고 싶으신가요?
INFO:root:[USER]: 장미
INFO:root:[BOT]: 몇월 며칠에 장미 을(를) 픽업하실 건가요?
INFO:root:[USER]: 2021년 12월 6일
INFO:root:[BOT]: 2021-12-6 몇시 몇분에 장미 을(를) 픽업하실 건가요?
INFO:root:[USER]: 13시 40분
INFO:root:[BOT]: 좋습니다. 2021-12-6 13:40에 장미 꽃을 준비해두겠습니다.
```