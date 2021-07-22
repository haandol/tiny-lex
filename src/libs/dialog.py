from typing import Callable
from .intent import Intent


class DialogManager(object):
    def __init__(self,
                 encoder: Callable[[str], list],
                 intents: list[Intent],
                 intent_threshold: float):
        self.encoder = encoder
        self.intents = intents
        self.intent_threshold = intent_threshold

    def classify_intent(self, text: str) -> tuple[float, Intent]:
        tokens = self.encoder(text)

        max_score = 0
        max_intent = None
        for intent in self.intents:
            score = intent.similarity_score(tokens)
            if self.intent_threshold < score and max_score < score:
                max_score = score
                max_intent = intent

        return max_score, max_intent

    def fulfill_intent(self,
                       intent: Intent,
                       slot_values: dict,
                       text: str) -> tuple[bool, dict, str]:
        return intent.next_prompt(slot_values, text)
