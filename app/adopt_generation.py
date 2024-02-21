import inflect
import os
import pandas as pd
import requests
import sys
from collections.abc import Iterable
from diskcache import Cache
from dotenv import load_dotenv

load_dotenv()
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

cache = Cache("tmp")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
PLURAL_ENGINE = inflect.engine()

load_dotenv()

tag_attributes = pd.read_csv(os.getenv("TAG_DB"))
tag_attributes = tag_attributes[tag_attributes["type"] == "attr"]

print(f"number of tag attributes {len(tag_attributes)}")

ATT_TAG_MAPPING = {}
for tag_att in tag_attributes.to_dict(orient='records'):
    for descriptor in tag_att['descriptors'].split("|"):
        ATT_TAG_MAPPING[descriptor.lower()] = tag_att['tags']


def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def is_nested_list(l):
    try:
        next(x for x in l if isinstance(x, list))

    except StopIteration:
        return False

    return True


@cache.memoize()
def search_osm_tag(entity):
    PARAMS = {"word": entity, "limit": 1, "detail": False}
    r = requests.get(
        url=SEARCH_ENDPOINT, params=PARAMS, verify=False
    )  # set verify to False to ignore SSL certificate
    return r.json()


def apply_rule(text):
    att_tag = None
    # todo: optimize it
    if "restaurant" in text:
        att_tag = {'key': 'cuisine', 'operator': '=', 'value': text.split(" ")[0]}

    return att_tag


def build_filters(node):
    node_name = node["name"]
    osm_results = search_osm_tag(node["name"])
    ent_filters = osm_results[0]["imr"]
    additional_att_tag = None

    processed_filters = []
    if len(ent_filters) > 0:
        if is_nested_list(ent_filters):
            processed_filters.extend(ent_filters[0])
        else:
            processed_filters.extend(ent_filters)

    if len(node_name.split(" ")) == 2:
        additional_att_tag = apply_rule(node_name)

    if "filters" in node:
        node_flts = []

        node_flts.append(processed_filters[0])

        for node_flt in node["filters"]:
            node_flt['key'] = node_flt.pop('name')
            node_flts.append(node_flt)

        processed_filters = [{"and": node_flts}]

    if additional_att_tag:
        processed_filters = [{"and": [processed_filters[0], additional_att_tag]}]

    return processed_filters


def adopt_generation(parsed_result):
    parsed_result['area']['type'] = 'area'
    parsed_result['area']['value'] = parsed_result['area'].pop('name')

    if len(parsed_result['area']['value']) == 0:
        parsed_result['area']['value'] = 'bbox'

    parsed_result['nodes'] = parsed_result.pop('entities')

    processed_nodes = []
    for node in parsed_result['nodes']:
        if 'name' not in node:
            print(f'{node} has not the required name field!')
            continue
        if not PLURAL_ENGINE.singular_noun(node['name']):
            display_name = PLURAL_ENGINE.plural_noun(node["name"])
        else:
            display_name = node['name']

        processed_nodes.append({
            'id': node['id'],
            'type': 'nwr',
            'filters': build_filters(node),
            'name': node['name'],
            'display_name': display_name

        })

    parsed_result['nodes'] = processed_nodes

    if 'relations' in parsed_result:
        parsed_result['edges'] = parsed_result.pop('relations')

        # TODO can we change from "distance" to "value" ???
        processed_edges = []
        for edge in parsed_result['edges']:
            edge['distance'] = edge.pop('value')
            edge['type'] = edge.pop('name')
            processed_edges.append(edge)

        parsed_result['edges'] = processed_edges

    return parsed_result
