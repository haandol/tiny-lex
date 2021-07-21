import torch
from transformers import (
    PreTrainedTokenizerFast,
    GPT2LMHeadModel,
)

MODEL_NAME = 'skt/kogpt2-base-v2'


class NLU(object):
    def __init__(self, max_length=64):
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(
            MODEL_NAME,
            bos_token='<s>', eos_token='</s>', unk_token='<unk>',
            pad_token='<pad>', mask_token='<mask>') 
        self.model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
        self.max_length = max_length

    def generate_tokens(self, text: str):
        input_ids = self.tokenizer.encode(text)
        gen_ids = self.model.generate(
            torch.tensor([input_ids]),
            max_length=self.max_length,
            repetition_penalty=2.0,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
            bos_token_id=self.tokenizer.bos_token_id,
            use_cache=True
        )
        return gen_ids.tolist()

    def encode(self, text: str):
        return self.tokenizer.encode(text)