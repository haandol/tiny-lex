import io
import yaml
import logging
from typing import Any, Callable, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from .slot_types import (
    date_type_validator, time_type_validator,
    confirm_type_validator
)

UTTERANCE_LIMIT = 10
CONFIRM_SLOT_NAME = 'confirm'
BUILTIN_SLOT_TYPES = {
    'date': date_type_validator,
    'time': time_type_validator,
    CONFIRM_SLOT_NAME: confirm_type_validator,
}


def default_validator(values: list) -> Callable:
    def validator(v: Any):
        if v in values:
            return v
        else:
            return None
    return validator


class SlotType(object):
    def __init__(self, name: str, validator: Callable[[Any], bool]):
        self.name = name
        self.validate = validator

    @staticmethod
    def load_slot_types(path: str) -> dict:
        slot_types = {}
        config_data = yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)
        for config in config_data['slot_types']:
            name = config['name']
            values = config['values']
            slot_types[name] = SlotType(name, default_validator(values))
        # built-in slot types
        for k, v in BUILTIN_SLOT_TYPES.items():
            slot_types[k] = SlotType(k, v)
        return slot_types


class Slot(object):
    def __init__(self, name: str, prompt: str, slot_type: SlotType):
        self.name = name
        self.prompt = prompt
        self.slot_type = slot_type

    def validate(self, v: Any) -> Any:
        return self.slot_type.validate(v)

    @staticmethod
    def load_slots(slot_types: dict, path: str) -> dict:
        slots = {}
        config_data = yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)
        for config in config_data['slots']:
            intent_name = config['intent_name']
            slots[intent_name] = []
            for slot_value in config['values']:
                name = slot_value['name']
                slot_type = slot_value['type']
                prompt = slot_value['prompt']
                slot = Slot(name, prompt, slot_types[slot_type])
                slots[intent_name].append(slot)
        return slots


class Intent(object):
    def __init__(self,
                 name: str,
                 utterances: list,
                 tokens: list,
                 slots: list,
                 fulfill_prompt: str,
                 reject_prompt: str = None):
        self.name = name
        self.utterances = utterances
        self.tokens = tokens
        self.slots = slots
        self.fulfill_prompt = fulfill_prompt
        self.reject_prompt = reject_prompt

    def next_prompt(self,
                    user_slot_values: dict,
                    text: str) -> Tuple[bool, dict, str]:
        is_fulfilled = False

        slot_value = {} if not user_slot_values else user_slot_values.copy()
        for i, slot in enumerate(self.slots):
            if slot.name not in slot_value:
                valid_value = slot.validate(text)
                if valid_value:
                    slot_value.update({slot.name: valid_value})
                    if i < len(self.slots)-1:
                        return is_fulfilled, slot_value, self.slots[i+1].prompt
                elif valid_value == False and slot.name == CONFIRM_SLOT_NAME:
                    # special slot
                    slot_value.update({slot.name: valid_value})
                else:
                    logging.warning(f'Invalid value for slot \
    [{slot.name}]: {slot_value}, {text}')
                    return is_fulfilled, slot_value, slot.prompt
        else:
            is_fulfilled = True

        is_confirmed = slot_value.get(CONFIRM_SLOT_NAME, is_fulfilled)
        return (
            is_fulfilled,
            slot_value,
            self.fulfill_prompt if is_confirmed else self.reject_prompt
        )

    def is_completed(self) -> bool:
        return all([slot.is_completed() for slot in self.slots])

    def similarity_score(self, tokens: list) -> float:
        return max([
            cosine_similarity(tokens, intent_tokens)[0][0]
            for intent_tokens in self.tokens
        ])
    
    def __str__(self):
        return f'Intent {self.name}'

    @staticmethod
    def load_intents(slots: List[Slot],
                     path: str,
                     tokenizer: Callable[[str], list]) -> dict:
        intents = {}
        config_data = yaml.load(io.open(path, 'r'), Loader=yaml.FullLoader)
        for config in config_data['intents']:
            logging.info(config)
            name = config['name']
            utterances = config['utterances'][:UTTERANCE_LIMIT]
            fulfill_prompt = config['fulfill_prompt']
            reject_prompt = config['reject_prompt']

            tokens = [tokenizer(utterance) for utterance in utterances]
            intent = Intent(name,
                            utterances=utterances,
                            tokens=tokens,
                            slots=slots[name],
                            fulfill_prompt=fulfill_prompt,
                            reject_prompt=reject_prompt)
            intents[name] = intent
        return intents
