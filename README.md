# Tiny Lex

Tiny version of Amazon Lex for Korean chatbot prototype

# Requirements

- Python 3.8

# Installation

```bash
$ pip install -r requirements.txt
```

# Usage

Lex 를 본따 만들었기 때문에 Lex의 구조를 떠올리면 된다. 
프로토타이핑용으로 며칠만에 만든 것이므로, 구조의 단순성이 최우선이다.
실제로 구현할 경우 KoNLPy, NER 또는 FastText 등을 추가로 적용하여 intent classifier 를 개선하거나,
슬롯값 결정시에도 fuzzy mapping 등의 방법을 적용해볼 수 있을 것이다.

여튼, 꽃을 구매하는 시나리오로 챗봇을 만들어 보자

## Add intent

[intent.yml](/config/intent.yml) 파일을 열고 intents 아래에 적절한 인텐트를 입력해준다.

`flower` 라는 이름의 인텐트를 추가해주고 해당 인텐트로 분류될 수 있도록 사용자의 예상 텍스트를 몇개 넣어준다.(최대 10개)

해당 인텐트로 대화가 시작되어서 모든 슬롯 정보가 다 채워지면 사용자에게 `fulfill_prompt` 가 보인다.

`reject_prompt` 는 `confirm` 타입의 슬롯이 존재할때만 넣어주면 된다.

```yaml
intents:
  - name: flower
    utterances:
      - 꽃을 사고 싶습니다
      - 꽃을 사고 싶다
      - 꽃 내놔
      - 꽃이 필요해
      - 플라워가 필요해
      - 플라워를 사고 싶다
    fulfill_prompt: '감사합니다. 주문이 완료되었습니다.'
    reject_prompt: '아쉽군요. 꽃 주문을 취소하겠습니다.'
```

## Add Slot

[slot.yml](/config/slot.yml) 파일을 열고 slots 아래에 적절한 슬롯을 입력해준다.

실제 인텐트가 다이얼로그로 진행되어야 하는지 정의하는 파일이다.

`type` 의 경우 해당 타입이 파이썬 모듈을 통해 정의된 타입이 아닐 경우 (e.g. flower_kinds)
이후 설명할 `slot_types` 에 해당 타입이 정의되어 있어야 한다.

`confirm` 타입은 특별한 타입으로 마지막에 한번 쓰이거나 아예 쓰이지 않을 수 있다.

```yaml
slots:
  - intent_name: flower
    values:
      - name: kinds
        type: flower_kinds
        prompt: "무슨 종류의 꽃을 사고 싶으신가요?"
      - name: pickup_date
        type: date
        prompt: "몇월 며칠에 {kinds} 을(를) 픽업하실 건가요?"
      - name: pickup_time
        type: time
        prompt: "{pickup_date} 몇시 몇분에 {kinds} 을(를) 픽업하실 건가요?"
      - name: confirm
        type: confirm
        prompt: "좋습니다. {pickup_date} {pickup_time}에 {kinds} 꽃을 준비해두면 될까요?"
```

### Add SlotTypes

[slot_type.yml](/config/slot_type.yml) 파일을 열고 slot_types 아래에 적절한 값들을 입력해준다.

`name` 은 앞서 설명한 Slot 에서 지정한 타입의 이름과 동일하다.

```yaml
slot_types:
  - name: flower_kinds
    values:
      - 장미
      - 백합
      - 할미꽃
```

## Test chatbot

chatbot.py 를 모듈형태로 실행하면 바로 테스트 해볼 수 있다.

```bash
$ python -m "src.chatbot"

INFO:root:{'name': 'flower', 'utterances': ['꽃을 사고 싶습니다', '꽃을 사고 싶다', '꽃 내놔', '꽃이 필요해', '플라워가 필요해', '플라워를 사고 싶다'], 'fulfill_prompt': '감사합니다. 주문이 완료되었습니다.', 'reject_prompt': '아쉽군요. 꽃 주문을 취소하겠습니다.'}
INFO:root:[USER][dongkyl]: 꽃을 사고 싶어
INFO:root:0.8072117893407781, Intent flower for 꽃을 사고 싶어
WARNING:root:Invalid value for slot     [kinds]: {}, 꽃을 사고 싶어
INFO:root:[BOT]: 무슨 종류의 꽃을 사고 싶으신가요?
INFO:root:[USER][dongkyl]: 장미
INFO:root:0, None for 장미
INFO:root:user specified intent: Intent flower
INFO:root:[BOT]: 몇월 며칠에 장미 을(를) 픽업하실 건가요?
INFO:root:[USER][dongkyl]: 2021년 12월 6일
INFO:root:0, None for 2021년 12월 6일
INFO:root:user specified intent: Intent flower
INFO:root:[BOT]: 2021-12-6 몇시 몇분에 장미 을(를) 픽업하실 건가요?
INFO:root:[USER][dongkyl]: 13시 50분
INFO:root:0, None for 13시 50분
INFO:root:user specified intent: Intent flower
INFO:root:[BOT]: 좋습니다. 2021-12-6 13:50에 장미 꽃을 준비해두면 될까요?
INFO:root:[USER][dongkyl]: 으악 실수
INFO:root:0, None for 으악 실수
INFO:root:user specified intent: Intent flower
WARNING:root:Invalid value for slot     [confirm]: {'kinds': '장미', 'pickup_date': '2021-12-6', 'pickup_time': '13:50'}, 으악 실수
INFO:root:[BOT]: 좋습니다. 2021-12-6 13:50에 장미 꽃을 준비해두면 될까요?
INFO:root:[USER][dongkyl]: 아니
INFO:root:0, None for 아니
INFO:root:user specified intent: Intent flower
INFO:root:[BOT]: 아쉽군요. 꽃 주문을 취소하겠습니다.
INFO:root:[USER][dongkyl]: 꽃을 사고 싶어
INFO:root:0.8072117893407781, Intent flower for 꽃을 사고 싶어
WARNING:root:Invalid value for slot     [kinds]: {}, 꽃을 사고 싶어
INFO:root:[BOT]: 무슨 종류의 꽃을 사고 싶으신가요?
INFO:root:[USER][dongkyl]: 장미
INFO:root:0, None for 장미
INFO:root:user specified intent: Intent flower
INFO:root:[BOT]: 몇월 며칠에 장미 을(를) 픽업하실 건가요?
INFO:root:[USER][dongkyl]: 꽃을 사고 싶어
INFO:root:0.8072117893407781, Intent flower for 꽃을 사고 싶어
WARNING:root:Invalid value for slot     [kinds]: {}, 꽃을 사고 싶어
INFO:root:[BOT]: 무슨 종류의 꽃을 사고 싶으신가요?
INFO:root:[USER][dongkyl]: 13시 50분
INFO:root:0, None for 13시 50분
INFO:root:user specified intent: Intent flower
WARNING:root:Invalid value for slot     [kinds]: {}, 13시 50분
INFO:root:[BOT]: 무슨 종류의 꽃을 사고 싶으신가요?
```

보이는대로 슬롯을 채우는 도중에 사용자가 인텐트를 변경하려고 하면 기존 슬롯을 비우고 새로운 인텐트를 시작하도록 되어 있다.

## Run on lambda

실행시 굳이 모듈형태로 실행한 것은 원래 AWS Lambda 위에서 실행되도록 만들어놨기 때문이다. (그냥 chatbot.py 를 실행해도 됨)

```bash
$ docker build -t tlex .
$ docker run -p 9000:8080 tlex:latest
time="2021-07-24T07:01:42.822" level=info msg="exec '/var/runtime/bootstrap' (cwd=/app, handler=)"
time="2021-07-24T07:01:56.802" level=info msg="extensionsDisabledByLayer(/opt/disable-extensions-jwigqn8j) -> stat /opt/disable-extensions-jwigqn8j: no such file or directory"
time="2021-07-24T07:01:56.802" level=warning msg="Cannot list external agents" error="open /opt/extensions: no such file or directory"
START RequestId: 6c3d1d10-a01d-49ca-9d9d-35e986fa137c Version: $LATEST
```

3기가 램에서 첫 호출이 30초정도 걸린다.(API GW 타임아웃이랑 거의 겹침)
상대적으로 작은 BERT 모델로 바꾸거나(파인튜닝 필요), 램을 올리거나, NLU 만 별도의 서버(Sagemaker Endpoint, ECS 등) 에서 호출하는 식으로 처리하면 된다.

```bash
$ pip install httpie
$ http post "http://localhost:9000/2015-03-31/functions/function/invocations" uid="1" text="꽃을 사고 싶습니다"

HTTP/1.1 200 OK
Content-Length: 107
Content-Type: text/plain; charset=utf-8
Date: Sat, 24 Jul 2021 07:03:51 GMT

[
    "무슨 종류의 꽃을 사고 싶으신가요?",
    "flower",
    {}
]
```

response 는 `(텍스트, 인텐트 이름, 사용자 슬롯값)` 으로 구성되어 있다.
텍스트만 반환하고 나머지 정도는 서버세션에서 보관해도 서버를 가볍게 유지하는 것이 중요하므로
세션정보의 유지는 클라이언트로 떠넘긴다.