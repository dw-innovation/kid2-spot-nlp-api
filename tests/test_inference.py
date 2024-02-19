import os
import requests
import sys
import inflect
from dotenv import load_dotenv
from diskcache import Cache
from app.tf_inference import generate
from app.adopt_generation import adopt_generation
from collections.abc import Iterable

load_dotenv()
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

cache = Cache("tmp")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")

print(SEARCH_ENDPOINT)

SINGULAR_TO_PLURAL_CONVERTER = inflect.engine()


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


if __name__ == '__main__':
    input_sentence = "Find me all bars in cologne."
    output = generate(input_sentence)
    print(output)
    output['result'] = adopt_generation(output['result'])