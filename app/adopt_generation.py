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
DEFAULT_DISTANCE = os.getenv("DEFAULT_DISTANCE")

load_dotenv()

# todo: move the rules to search engine, a bit messy
osm_tags_and_attr = pd.read_csv(os.getenv("TAG_DB"))

TAG_ATTR = {}
TAG_ATTR_IDS = {}
for tag_att in osm_tags_and_attr[osm_tags_and_attr["type"] == "attr"].to_dict(orient='records'):
    for descriptor in tag_att['descriptors'].split("|"):
        TAG_ATTR[descriptor.lower()] = tag_att['tags']
        TAG_ATTR_IDS[descriptor.lower()] = str(int(tag_att['index']))

# rule 1 - cuisine
cuisine_idx = TAG_ATTR_IDS["cuisine"]
cuisine_group = set()
for osm_tag in osm_tags_and_attr[osm_tags_and_attr["type"] == "core"].to_dict(orient='records'):
    if isinstance(osm_tag['combinations'], float):
        continue
    combinations = set([_comb.strip() for _comb in osm_tag['combinations'].split('|')])
    if cuisine_idx in combinations:
        for descriptor in osm_tag['descriptors'].split("|"):
            cuisine_group.add(descriptor.lower())


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


class AdoptFuncError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


@cache.memoize()
def search_osm_tag(entity):
    PARAMS = {"word": entity, "limit": 1, "detail": False}
    r = requests.get(
        url=SEARCH_ENDPOINT, params=PARAMS, verify=False
    )  # set verify to False to ignore SSL certificate
    return r.json()


# TODO move this methods to search engine in the future
def apply_rule(text):
    att_tag = None
    # todo: optimize it
    splitted_text = text.split(" ")
    if len(cuisine_group.intersection(set(splitted_text))) > 0:
        att_tag = {'key': 'cuisine', 'operator': '=', 'value': splitted_text[0]}

    return att_tag


def build_filters(node):
    node_name = node["name"]
    osm_results = search_osm_tag(node["name"])
    if len(osm_results) == 0:
        return None
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
            if node_flt["name"] not in TAG_ATTR_IDS.keys():
                continue
            node_flt['key'] = node_flt.pop('name')
            if len(node_flt['operator']) ==0:
                node_flt['operator'] = '='
            node_flts.append(node_flt)

        processed_filters = [{"and": node_flts}]

    if additional_att_tag:
        processed_filters = [{"and": [processed_filters[0], additional_att_tag]}]

    and_or_in_filters = False
    for processed_filter in processed_filters:
        if "and" in processed_filter:
            and_or_in_filters = True
            continue
        if "or" in processed_filter:
            and_or_in_filters = True
            continue

    if not and_or_in_filters:
        processed_filters = [{"and": processed_filters}]

    return processed_filters


def adopt_generation(parsed_result):
    try:
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

            node_filters = build_filters(node)

            if node_filters:
                processed_nodes.append({
                    'id': node['id'],
                    'type': 'nwr',
                    'filters': node_filters,
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
                if 'mm' in edge['distance']:
                    edge['distance'] = edge['distance'].replace('mm', '')
                    edge['distance'] = DEFAULT_DISTANCE
                elif 'cm' in edge['distance']:
                    edge['distance'] = edge['distance'].replace('cm', '')
                    edge['distance'] = DEFAULT_DISTANCE
                edge['type'] = edge.pop('name')
                processed_edges.append(edge)

            parsed_result['edges'] = processed_edges

    except (ValueError, IndexError, KeyError, TypeError) as e:
        raise AdoptFuncError(f"Error in Adopt Generation: {e}")

    return parsed_result
