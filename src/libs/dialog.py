from typing import Callable
from .intent import Intent


class IntentClassifier(object):
    def __init__(self,
                 encoder: Callable[[str], list],
                 threshold: float):
        self.encoder = encoder
        self.threshold = threshold

    def classify(self,
                 intents: list[Intent],
                 text: str) -> tuple[float, Intent]:
        tokens = self.encoder(text)

        max_score = 0
        max_intent = None
        for intent in intents:
            score = intent.similarity_score(tokens)
            if self.threshold < score and max_score < score:
                max_score = score
                max_intent = intent

        return max_score, max_intent


class DialogManager(object):
    def __init__(self,
                 encoder: Callable[[str], list],
                 intents: list[Intent]):
        self.intent_classifier = IntentClassifier(encoder, threshold=0.6)
        self.intents = intents

    def classify_intent(self, text: str) -> tuple[float, Intent]:
        return self.intent_classifier.classify(self.intents, text)

    def fulfill_intent(self,
                       intent: Intent,
                       slot_values: dict,
                       text: str) -> tuple[bool, dict, str]:
        return intent.next_prompt(slot_values, text)
