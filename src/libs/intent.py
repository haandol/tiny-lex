import io
import yaml
import logging
from typing import Any, Callable


class SlotType(object):
    def __init__(self, name: str, values: list):
        self.name = name
        self.values = values

    @staticmethod
    def load_slot_types(path: str) -> dict:
        slot_types = {}
        for config in yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)['slot_types']:
            name = config['name']
            values = config['values']
            slot_types[name] = SlotType(name, values)
        return slot_types


class Slot(object):
    def __init__(self, name: str, prompt: str, slot_type: SlotType):
        self.name = name
        self.prompt = prompt
        self.slot_type = slot_type

    def is_valid(self, v: Any) -> bool:
        if v not in self.slot_type.values:
            return False
        return True

    @staticmethod
    def load_slots(slot_types: dict, path: str) -> dict:
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


class Intent(object):
    def __init__(self, name: str, utterances: list, tokens, slots: list, confirm_prompt: str):
        self.name = name
        self.utterances = utterances
        self.confirm_prompt = confirm_prompt
        self.slots = slots
        self.tokens = tokens

    def next_prompt(self, user_slot_value: dict, text: str) -> tuple[bool, dict, str]:
        is_fulfilled = False
        slot_value = user_slot_value.copy()
        for slot in self.slots:
            if slot.name not in slot_value:
                logging.info(f'{slot_value}, {text}')
                if slot.is_valid(text):
                    slot_value.update({slot.name: text})
                else:
                    logging.warn(f'Invalid value for slot: {slot_value}, {text}')
                    return is_fulfilled, slot_value, slot.prompt
        else:
            is_fulfilled = True
        return is_fulfilled, slot_value, self.confirm_prompt

    def is_completed(self) -> bool:
        return all([slot.is_completed() for slot in self.slots])

    @staticmethod
    def load_intents(slots, path: str, tokenizer: Callable[[str], list]) -> list:
        intents = []
        for config in yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)['intents']:
            logging.info(config)
            name = config['name']
            utterances = config['utterances']
            confirm_prompt = config['confirm_prompt']

            tokens = [tokenizer(utterance) for utterance in utterances]
            intent = Intent(name, utterances=utterances, tokens=tokens,
                            slots=slots[name], confirm_prompt=confirm_prompt)
            intents.append(intent)
        return intents