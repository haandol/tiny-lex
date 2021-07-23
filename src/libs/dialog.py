from typing import Callable, Tuple
from .intent import Intent


class IntentClassifier(object):
    def __init__(self,
                 encoder: Callable[[str], list],
                 threshold: float):
        self.encoder = encoder
        self.threshold = threshold

    def classify(self,
                 intents: dict,
                 text: str) -> Tuple[float, Intent]:
        tokens = self.encoder(text)

        max_score = 0
        max_intent = None
        for intent in intents.values():
            score = intent.similarity_score(tokens)
            if self.threshold < score and max_score < score:
                max_score = score
                max_intent = intent

        return max_score, max_intent


class DialogManager(object):
    def __init__(self,
                 encoder: Callable[[str], list],
                 intents: dict):
        self.intent_classifier = IntentClassifier(encoder, threshold=0.8)
        self.intents = intents

    def get_intent_by_name(self, name: str) -> Intent:
        return self.intents.get(name, None)

    def classify_intent(self, text: str) -> Tuple[float, Intent]:
        return self.intent_classifier.classify(self.intents, text)

    def fulfill_intent(self,
                       intent: Intent,
                       user_slot_values: dict,
                       text: str) -> Tuple[bool, dict, str]:
        return intent.next_prompt(user_slot_values, text)
