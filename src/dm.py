import io
import yaml
import logging
from sklearn.metrics.pairwise import cosine_similarity


class InvalidSlotValue(Exception):
    pass


class SlotType(object):
    def __init__(self, name: str, values: list):
        self.name = name
        self.values = values


class Slot(object):
    def __init__(self, name: str, prompt: str, slot_type: SlotType):
        self.name = name
        self.prompt = prompt
        self.slot_type = slot_type

    def is_valid(self, v):
        if v not in self.slot_type.values:
            raise InvalidSlotValue()
        self._value = v


class Intent(object):
    def __init__(self, name: str, utterances: list, tokens, slots: list, confirm_prompt: str):
        self.name = name
        self.utterances = utterances
        self.confirm_prompt = confirm_prompt
        self.slots = slots
        self.tokens = tokens

    def next_prompt(self, user_slot_value, text: str):
        is_fulfilled = False
        slot_value = user_slot_value.copy()
        for slot in self.slots:
            if slot.name not in slot_value:
                logging.info(f'{slot_value}, {text}')
                try:
                    slot.is_valid(text)
                    slot_value.update({slot.name: text})
                except InvalidSlotValue:
                    logging.warn(f'{slot_value}, {text}')
                    return is_fulfilled, slot_value, slot.prompt
        else:
            is_fulfilled = True
        return is_fulfilled, slot_value, self.confirm_prompt

    def is_completed(self):
        return all([slot.is_completed() for slot in self.slots])


class DialogManager(object):
    def __init__(self, nlu, intent_threshold=0.6):
        self.nlu = nlu
        self.intent_threshold = intent_threshold

        slot_types = self.load_slot_types('../config/slot_type.yml')
        slots = self.load_slots(slot_types, '../config/slot.yml')
        self.intents = self.load_intents(slots, '../config/intent.yml')

    def load_slot_types(self, path: str):
        slot_types = {}
        for config in yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)['slot_types']:
            name = config['name']
            values = config['values']
            slot_types[name] = SlotType(name, values)
        return slot_types

    def load_slots(self, slot_types, path: str):
        slots = {}
        for config in yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)['slots']:
            intent_name = config['name']
            slots[intent_name] = []
            for slot_value in config['values']:
                name = slot_value['name']
                slot_type = slot_value['type']
                prompt = slot_value['prompt']
                slots[intent_name].append(Slot(name, prompt, slot_types[slot_type]))
        return slots

    def load_intents(self, slots, path: str):
        intents = []
        for config in yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)['intents']:
            print(config)
            name = config['name']
            utterances = config['utterances']
            confirm_prompt = config['confirm_prompt']

            tokens = [
                self.nlu.generate_tokens(utterance)
                for utterance in utterances
            ]
            intent = Intent(name, utterances=utterances, tokens=tokens,
                            slots=slots[name], confirm_prompt=confirm_prompt)
            intents.append(intent)
        return intents

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