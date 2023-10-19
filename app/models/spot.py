import torch
import requests
from diskcache import Cache
import json
import dirtyjson
import os
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

logger.add(f"{__name__}.log", rotation="500 MB")

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
        area["v"] = [-90, -180, 90, 180]
    area["value"] = area.pop("v")
    area["type"] = area.pop("t")

    return area


# Process 'edges', change the minimized results
def process_edges(edges: list) -> list:
    for idx, edge in enumerate(edges):
        edge["type"] = edge.pop("t")
        edge["source"] = edge.pop("src")
        edge["target"] = edge.pop("tgt")
        edge["distance"] = edge.pop("dist")
        edges[idx] = edge

    return edges


# Process the 'nodes' part of the result
def process_nodes(nodes: list) -> list:
    # Iterate through each node in the list
    for idx, node in enumerate(nodes):
        # Set node type to "nwr"
        node["type"] = "nwr"

        # Initialize "flts" key if not present
        if "flts" not in node:
            node["flts"] = []

        node["filters"] = node.pop("flts")

        node["name"] = node.pop("n")

        # Search OpenStreetMap tags based on the node name
        osm_results = search_osm_tag(node["name"])

        if len(osm_results) == 0:
            logger.error(f"No OSM Tags found {node['name']}")
            continue

        entityfilters = osm_results[0]["imr"]
        node["filters"] = replace_keys_recursive(node["filters"])

        # Determine how to set 'filters' based on whether node["filters"] is empty or not
        if node["filters"] == []:
            # If empty, set filters to entityfilters
            filters = entityfilters
        else:
            # Otherwise, append entityfilters to existing node["filters"] under "and" key
            filters = [{"and": node["filters"] + entityfilters}]

        # Update the "flts" field in the node with the new filters
        node["filters"] = filters
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

    # Process and delete "a" if present
    if "a" in result:
        result["area"] = process_area(result["a"])
        del result["a"]

    # Process and delete "ns" if present
    if "ns" in result:
        result["nodes"] = process_nodes(result["ns"])
        del result["ns"]

    # Process and delete "es" if present
    if "es" in result:
        result["edges"] = process_edges(result["es"])
        del result["es"]

    return {"result": result, "raw": raw_result}


def replace_keys_recursive(filters):
    new_filters = []
    for filter_item in filters:
        new_item = {}
        for k, v in filter_item.items():
            if k == "k":
                new_k = "key"
            elif k == "v":
                new_k = "value"
            elif k == "op":
                new_k = "operator"
            elif k == "n":
                new_k = "name"
            else:
                new_k = k

            if isinstance(v, list):
                new_item[new_k] = replace_keys_recursive(v)
            else:
                new_item[new_k] = v

        new_filters.append(new_item)
    return new_filters


# Entry point for script execution
if __name__ == "__main__":
    with torch.inference_mode():
        output = inference(
            sentence="Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels."
        )
