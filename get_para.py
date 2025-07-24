import json
import re
import requests
from requests.exceptions import RequestException


PARA_JSON = "para.json"
URL = "https://cdn.jsdelivr.net/gh/c15412/Cealing-Host@main/Cealing-Host.json"


def store2dict(dic: dict, key: str , arr: list):
    if key in dic:
        dic[key].extend(arr)
    else:
        dic[key] = arr
    
    # for debug
    # print(f"keys: {arr}  ->\n vals: {key}")

def _get_config_from_web(url=None):
    if url is None:
        url = URL
    js = None
    try:
        response = requests.get(url)
        response.raise_for_status()
        js = response.json()
        # print("Config fetched successfully.", js)
    except RequestException as e:
        print(f"Error fetching config: {e}")
        return None, None
    
    if js is None:
        return None, None

    mapper = {}
    resolver = {}
    for array in js:
        if not array[1]:
            store2dict(resolver, array[2], array[0])
            continue
        store2dict(mapper, array[1], array[0])
        store2dict(resolver, array[2], [array[1]])

    return mapper, resolver

def get_config(file=PARA_JSON):
    js = None
    try:
        with open(file, 'r') as f:
            js = json.load(f)
    except FileNotFoundError:
        return {}, {}
    else:
        mapper = js["mapper"]
        resolver = js["resolver"]
        return mapper, resolver

def save_config(mapper: dict, resolver: dict, file=PARA_JSON):
    js = {
        "mapper": mapper,
        "resolver": resolver
    }
    try:
        with open(file, 'w') as f:
            json.dump(js, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
        return None

def get_config_from_web(uri = None) -> tuple:
    mapper, resolver = get_config()
    if (not mapper and not resolver) or uri:
        mapper, resolver = _get_config_from_web(uri)
        if mapper is None or resolver is None:
            return {}, {}
        save_config(mapper, resolver)
    return mapper, resolver

if __name__ == "__main__":
    print(get_config_from_web())
