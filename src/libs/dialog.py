import os
from .intent import Slot, SlotType, Intent
from sklearn.metrics.pairwise import cosine_similarity


class DialogManager(object):
    def __init__(self, nlu, intent_threshold=0.6):
        self.nlu = nlu
        self.intent_threshold = intent_threshold

        slot_types = SlotType.load_slot_types(os.path.join(os.getcwd(), '..', 'config', 'slot_type.yml'))
        slots = Slot.load_slots(slot_types, os.path.join(os.getcwd(), '..', 'config', 'slot.yml'))
        self.intents = Intent.load_intents(slots, os.path.join(os.getcwd(), '..', 'config', 'intent.yml'), self.nlu.generate_tokens)

    def classify_intent(self, text):
        tokens = self.nlu.generate_tokens(text)

        max_score = -9999
        max_intent = None
        for intent in self.intents:
            for intent_tokens in intent.tokens:
                score = cosine_similarity(tokens, intent_tokens)[0][0]
                if self.intent_threshold < score and max_score < score:
                    max_score = score
                    max_intent = intent

        return max_score, max_intent

    def fulfill_intent(self, intent: Intent, slot_values, text: str):
        return intent.next_prompt(slot_values, text)