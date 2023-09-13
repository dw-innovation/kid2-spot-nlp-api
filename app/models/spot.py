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
    PARAMS = {"word": entity, "limit": 5, "detail": False}
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
    # Iterate through each node in the list
    for idx, node in enumerate(nodes):
        # Set node type to "nwr"
        node["t"] = "nwr"

        # Initialize "flts" key if not present
        if "flts" not in node:
            node["flts"] = []

        # Initialize entityflts dictionary with "or" key
        entityflts = {"or": []}

        # Search OpenStreetMap tags based on the node name
        osm_results = search_osm_tag(node["n"])

        # Loop through all tags and split them into key and value
        for tag in osm_results:
            osm_result = tag["osm_tag"].split("=")
            # Append the split results to "or" list in entityflts
            entityflts["or"].append({"k": osm_result[0], "op": "=", "v": osm_result[1]})

        # Determine how to set 'filters' based on whether node["flts"] is empty or not
        if node["flts"] == []:
            # If empty, set filters to entityflts
            filters = [entityflts]
        else:
            # Otherwise, append entityflts to existing node["flts"] under "and" key
            filters = [{"and": node["flts"] + [entityflts]}]

        # Update the "flts" field in the node with the new filters
        node["flts"] = filters
        # Update the node in the original list
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
    raw_result = tokenizer.decode(token_ids=outputs[0], skip_special_tokens=True)

    # Post-process the results
    result = clean_result(raw_result)
    result = json.loads(dirtyjson.loads(result))

    result["a"] = process_area(result["a"])
    result["ns"] = process_nodes(result["ns"])

    return {"result": result, "raw": raw_result}


# Entry point for script execution
if __name__ == "__main__":
    with torch.inference_mode():
        output = inference(
            sentence="Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels."
        )
