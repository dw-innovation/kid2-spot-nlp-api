import torch
import numpy as np
from docarray import Document, DocumentArray
from gensim.models import KeyedVectors
import json
import dirtyjson

from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM)
from peft import PeftModel

peft_model_id = "model/t5_tuned"
base_model = "model/t5-base"

# # load base LLM model and tokenizer
transformer_model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)
device = torch.device('cpu')

transformer_model = PeftModel.from_pretrained(transformer_model, peft_model_id)
transformer_model.to(device)

op_tag_model_path = "model/wiki.simple.vec"
op_tag_model = KeyedVectors.load_word2vec_format(op_tag_model_path)

da = DocumentArray(
    storage='sqlite', config={'connection': 'model/op_tags.db', 'table_name': 'keys'}
)


def prepare_input(sentence: str):
    input_ids = tokenizer(sentence, max_length=512, return_tensors="pt").input_ids
    return input_ids


def inference(sentence: str) -> str:
    input_data = prepare_input(sentence=sentence)
    input_data = input_data.to(transformer_model.device)
    outputs = transformer_model.generate(inputs=input_data, max_length=1024)
    result = tokenizer.decode(token_ids=outputs[0], skip_special_tokens=True)

    # Remove extra characters
    result = result.strip().strip("{").strip("}")
    result = result.replace("'", "\"")
    result = result.replace("'", "\"")
    result = result.replace("\"{ ", "\'{ ")
    result = result.replace("} \"", "} \'")
    result = result.replace("\"\"", "\"")

    # Remove trailing whitespace
    result = result.strip()

    # Load JSON data as a Python object

    result = json.loads(dirtyjson.loads(result))

    nodes = []
    for node in result['nodes']:
        if node['type'] == 'object':
            splits = node['label'].split()
            word = splits[0] if len(splits) >= 2 else node['label']

            try:
                wv = op_tag_model[word]
            except KeyError:
                wv = np.random(300, 1)

            os_tag = da.find(np.array(wv), metric='cosine', limit=1, exclude_self=True)[0]

            nodes.append({'name': os_tag.tags['tag'], 'type': node['type'], 'props': node['props']})

        else:
            nodes.append({'name': node['label'], 'type': node['type']})

    response_relations = result['edges']

    edges = []
    for response_relation in response_relations:
        edges.append({'from': response_relation['from'],
                      'to': response_relation['to'],
                      'weight': response_relation['weight']})

    action = result['action']

    return dict(nodes=nodes, relations=edges, action=action)


if __name__ == '__main__':
    with torch.inference_mode():
        output = inference(
            sentence='Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels.')
