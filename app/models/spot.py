import torch
import requests
from diskcache import Cache
import json
import dirtyjson
import os

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

peft_model_id = os.getenv("PEFT_MODEL_ID")
base_model = os.getenv("BASE_MODEL")

# # load base LLM model and tokenizer
transformer_model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)
device = torch.device("cpu")

transformer_model = PeftModel.from_pretrained(transformer_model, peft_model_id)
transformer_model.to(device)


def prepare_input(sentence: str):
    input_ids = tokenizer(sentence, max_length=1024, return_tensors="pt").input_ids
    return input_ids


cache = Cache("tmp")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")


@cache.memoize()
def search_osm_tag(entity):
    PARAMS = {"word": entity, "limit": 1, "detail": False}
    r = requests.get(url=SEARCH_ENDPOINT, params=PARAMS, verify=False)
    return r.json()


def inference(sentence: str) -> str:
    input_data = prepare_input(sentence=sentence)
    input_data = input_data.to(transformer_model.device)
    outputs = transformer_model.generate(inputs=input_data, max_length=1024)
    result = tokenizer.decode(token_ids=outputs[0], skip_special_tokens=True)

    result = result.strip().strip("{").strip("}")
    result = result.replace("'", '"')
    result = result.replace("'", '"')
    result = result.replace('"{ ', "'{ ")
    result = result.replace('} "', "} '")
    result = result.replace('""', '"')
    result = result.replace(', "', ', "')
    result = result.replace("} ", "}")
    result = result.replace("} ]", "}]")
    result = result.replace(": [", ":[")
    result = result.replace("}}]", "}]")
    result = json.loads(dirtyjson.loads(result))

    area = result["a"]
    if "v" not in area:
        result["a"]["v"] = ""

    nodes = result["ns"]

    for idx, node in enumerate(nodes):
        node["t"] = "nwr"

        if "flts" not in node:
            node["flts"] = []

        osm_result = search_osm_tag(node["n"])
        osm_tag = osm_result[0]["osm_tag"].split("=")

        node["flts"] = [
            {"k": osm_tag[0], "v": osm_tag[1], "op": "=", "n": node["n"]}
        ] + node["flts"]

        for idy, flt in enumerate(node["flts"][1:]):
            flt["k"] = flt["n"]

            node["flts"][idy + 1] = flt

        nodes[idx] = node

    result["ns"] = nodes

    return result


if __name__ == "__main__":
    with torch.inference_mode():
        output = inference(
            sentence="Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels."
        )
