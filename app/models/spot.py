import torch
import inflect
import re
import requests
from diskcache import Cache
import json
import dirtyjson
import os
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Text2TextGenerationPipeline
from peft import PeftModel
from dotenv import load_dotenv

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

# Initialize disk cache and get search endpoint
cache = Cache("tmp")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")

transformer_model = PeftModel.from_pretrained(transformer_model, peft_model_id)
transformer_model = transformer_model.merge_and_unload()
transformer_model.eval()

pipeline = Text2TextGenerationPipeline(model=transformer_model, batch_size=16,
                                       tokenizer=tokenizer,
                                       device=device,  # model.device,
                                       clean_up_tokenization_spaces=True)

plural_converter = inflect.engine()

# Cache and fetch OpenStreetMap tags
@cache.memoize()
def search_osm_tag(entity):
    PARAMS = {"word": entity, "limit": 5, "detail": False}
    r = requests.get(
        url=SEARCH_ENDPOINT, params=PARAMS, verify=False
    )  # set verify to False to ignore SSL certificate
    return r.json()


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
        node["display_name"] = plural_converter.plural_noun(node["name"])

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


# Main inference function
def inference(sentence: str) -> str:
    # Prepare input and perform inference
    sentence = sentence.lower()
    raw_result = pipeline([sentence], do_sample=False, max_length=MAX_LENGTH, pad_token_id=tokenizer.pad_token_id)
    raw_result = raw_result[0]["generated_text"]

    # Post-process the results
    try:
        result = json.loads(dirtyjson.loads(raw_result))
    except json.decoder.JSONDecodeError as e:
        result = fix_json(raw_result)

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


# Clean up the result string for JSON conversion
def fix_json(text, decoder=json.JSONDecoder()):
    fixed_data = {}
    pos = 0
    while True:
        match = text.find('{', pos)

        if match == -1:
            break
        try:
            sub_text = text[match:]
            if "\"a\":" in sub_text:
                start_index = sub_text.find('\"a\":')
                end_index = sub_text.find('\"es\":')
                input_text = sub_text[start_index + len('\"a\":'):end_index]
                area_obj = dirtyjson.loads(input_text)
                if area_obj["t"] != "bbox":
                    fixed_data["a"] = {"t": area_obj["t"], "v": area_obj["v"]}
                else:
                    fixed_data["a"] = {"t": area_obj["t"]}
            if "\"es\"" in sub_text:
                start_index = sub_text.find('\"es\":')
                end_index = sub_text.find('\"ns\":')
                input_text = sub_text[start_index + len('\"es\":'):end_index]
                es_objs = dirtyjson.loads(input_text)

                fixed_data["es"] = []
                for es_obj in es_objs:
                    fixed_data["es"].append({"src": es_obj["src"],
                                             "tgt": es_obj["tgt"],
                                             "t": es_obj["t"],
                                             "dist": es_obj["dist"]
                                             })
            if "\"ns\"" in sub_text:
                start_index = sub_text.find('\"ns\":')
                end_index = sub_text.rfind('}')
                input_text = sub_text[start_index + len('\"ns\":'):end_index]
                input_text = input_text.replace("}} ]", "}]")
                ns_objs = dirtyjson.loads(input_text)
                fixed_data["ns"] = []
                for ns_obj in ns_objs:
                    fixed_ns_obj = {}
                    fixed_ns_obj["id"] = ns_obj["id"]
                    fixed_ns_obj["n"] = ns_obj["n"]
                    flts = []
                    if "flts" in ns_obj:
                        for flt in ns_obj["flts"]:
                            flts.append(
                                {"n": flt["n"],
                                 "op": flt["op"],
                                 "v": flt["v"],
                                 "k": flt["k"]
                                 }
                            )
                    if len(flts) > 0:
                        fixed_ns_obj["flts"] = flts

                    fixed_data["ns"].append(fixed_ns_obj)
            result, index = decoder.raw_decode(text[match:])
            pos = match + index
        except ValueError:
            pos = match + 1

    return fixed_data


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

        print(output)