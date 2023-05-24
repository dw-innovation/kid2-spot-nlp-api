import torch
import numpy as np
from docarray import Document, DocumentArray
from gensim.models import KeyedVectors
import re
from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM)
from peft import PeftModel
import os

peft_model_id = os.getenv("MODELSPATH")+"/t5_tuned"
base_model = os.getenv("MODELSPATH")+"/t5-base"

# # load base LLM model and tokenizer
transformer_model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(base_model)
device = torch.device('cpu')

transformer_model = PeftModel.from_pretrained(transformer_model, peft_model_id)
transformer_model.to(device)

op_tag_model_path = os.getenv("MODELSPATH")+"/wiki.simple.vec"
op_tag_model = KeyedVectors.load_word2vec_format(op_tag_model_path)

da = DocumentArray(
    storage='sqlite', config={'connection': os.getenv("MODELSPATH")+'/op_tags.db', 'table_name': 'keys'}
)


def prepare_input(sentence: str):
    input_ids = tokenizer(sentence, max_length=512,
                          return_tensors="pt").input_ids
    return input_ids


def inference(sentence: str) -> str:
    input_data = prepare_input(sentence=sentence)
    input_data = input_data.to(transformer_model.device)
    outputs = transformer_model.generate(inputs=input_data, max_length=1024)
    result = tokenizer.decode(token_ids=outputs[0], skip_special_tokens=True)
    #
    # Extract the desired information using regex
    matches = re.findall(r'\[\s*(\w+)\s*,\s*(\w+)\s*\]', result)

    nodes = []
    for match in matches:
        if match[1] == 'area':
            nodes.append({'name': match[0], 'type': match[1]})
        else:
            tag = op_tag_model[match[0]]
            if len(tag) > 1:
                wv = op_tag_model[match[0].split(' ')[0]]
            else:
                wv = op_tag_model[match[0]]
            os_tag = da.find(np.array(wv), metric='cosine',
                             limit=1, exclude_self=True)[0]
            nodes.append({'name': os_tag.tags['tag'], 'type': match[1]})

    # TODO: this needs to be changed
    relations = []
    for idx in range(0, len(nodes) - 1):
        relations.append({'from': str(idx), 'to': str(idx + 1), 'weight': 100})

    action = 'search_within'

    return dict(nodes=nodes, relations=relations, action=action)


if __name__ == '__main__':
    with torch.inference_mode():
        output = inference(
            sentence='I am looking for an apartment within 1005 meters of a supermarket within 1037 meters of a pharmacy within 479 meters of a tower')
