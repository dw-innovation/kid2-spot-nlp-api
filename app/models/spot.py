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

## load base LLM model and tokenizer
transformer_model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)
device = torch.device("cpu")  # Set the device to CPU

# Initialize disk cache and get search endpoint
cache = Cache("tmp")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")

transformer_model = PeftModel.from_pretrained(transformer_model, peft_model_id)
transformer_model.to(device)


# Cache and fetch OpenStreetMap tags
@cache.memoize()
def search_osm_tag(entity):
    PARAMS = {"word": entity, "limit": 1, "detail": False}
    r = requests.get(
        url=SEARCH_ENDPOINT, params=PARAMS, verify=False
    )  # set verify to False to ignore SSL certificate
    return r.json()


# Prepare the input sentence for the model
def prepare_input(sentence: str):
    input_ids = tokenizer(sentence, max_length=1024, return_tensors="pt").input_ids
    return input_ids


# Process the 'area' part of the result
def process_area(area: dict) -> dict:
    if "v" not in area:
        area["v"] = ""
    return area


# Process the 'nodes' part of the result
def process_nodes(nodes: list) -> list:
    # Loop through each node in the list
    for idx, node in enumerate(nodes):
        # Set the type of the node to "nwr"
        node["t"] = "nwr"

        # Initialize "flts" key if not present in node
        if "flts" not in node:
            node["flts"] = []

        # Search for an OSM tag based on the node's name
        osm_result = search_osm_tag(node["n"])
        # Parse the first OSM tag from the search result
        osm_tag = osm_result[0]["osm_tag"].split("=")

        # Update the "flts" key with the new OSM tag
        node["flts"] = [
            {"k": osm_tag[0], "v": osm_tag[1], "op": "=", "n": node["n"]}
        ] + node["flts"]

        # Loop through the rest of the "flts" to update them
        for idy, flt in enumerate(node["flts"][1:]):
            # Set "k" value based on node's name
            flt["k"] = flt["n"]
            # Update the node's filters
            node["flts"][idy + 1] = flt

        # Update the original list with the modified node
        nodes[idx] = node

    return nodes


# Clean up the result string for JSON conversion
def clean_result(result: str) -> str:
    result = result.strip().strip("{").strip("}")
    result = (
        result.replace("'", '"')
        .replace("'", '"')
        .replace('"{ ', "'{ ")
        .replace('} "', "} '")
        .replace('""', '"')
        .replace(', "', ', "')
        .replace("} ", "}")
        .replace("} ]", "}]")
        .replace(": [", ":[")
        .replace("}}]", "}]")
    )

    return result


# Main inference function
def inference(sentence: str) -> str:
    # Prepare input and perform inference
    input_data = prepare_input(sentence=sentence)
    input_data = input_data.to(transformer_model.device)
    outputs = transformer_model.generate(inputs=input_data, max_length=1024)
    result = tokenizer.decode(token_ids=outputs[0], skip_special_tokens=True)

    # Post-process the results
    result = clean_result(result)
    result = json.loads(dirtyjson.loads(result))

    result["a"] = process_area(result["a"])
    result["ns"] = process_nodes(result["ns"])

    return result


# Entry point for script execution
if __name__ == "__main__":
    with torch.inference_mode():
        output = inference(
            sentence="Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels."
        )
