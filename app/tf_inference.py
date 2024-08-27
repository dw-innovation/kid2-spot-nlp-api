import codecs
import inflect
import os
import re
import requests
import torch
from diskcache import Cache
from dotenv import load_dotenv
from loguru import logger
from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Text2TextGenerationPipeline

logger.add(f"{__name__}.log", rotation="500 MB")

load_dotenv()

peft_model_id = os.getenv("PEFT_MODEL_ID")
base_model = os.getenv("BASE_MODEL")
MAX_LENGTH = int(os.getenv("MAX_LENGTH"))
CUDA_DEVICE = os.getenv("CUDA_DEVICE")

## load base LLM model and tokenizer
transformer_model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)

if CUDA_DEVICE:
    device = torch.device(f"cuda:{cuda_device}" if torch.cuda.is_available() else "cpu")
else:
    device = torch.device("cpu")

transformer_model = PeftModel.from_pretrained(transformer_model, peft_model_id)
transformer_model = transformer_model.merge_and_unload()
transformer_model.eval()

pipeline = Text2TextGenerationPipeline(model=transformer_model, batch_size=16,
                                       tokenizer=tokenizer,
                                       device=device,  # model.device,
                                       clean_up_tokenization_spaces=True)

class ModelException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# Main inference function
def generate(sentence: str) -> str:
    raw_result = None
    if len(sentence) ==0:
        raise ModelException("Input must not be empty.")
    sentence = sentence.lower()
    with torch.inference_mode():
        raw_result = pipeline([sentence], do_sample=False, max_length=MAX_LENGTH, pad_token_id=tokenizer.pad_token_id)
        raw_result = raw_result[0]["generated_text"]
    if len(raw_result) ==0:
        raise ModelException("Model does not generate a text.")
    return raw_result


# Entry point for script execution
if __name__ == "__main__":
    with torch.inference_mode():
        # output = inference(
        #     sentence="Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels."
        # )
        output = generate(
            sentence="Find all cafes closer than 100m to a kiosk in München Straße."
        )
        print(output)
