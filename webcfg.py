import json
import re
import requests
from requests.exceptions import RequestException

__all__ = [
    "get_config_from_web",
    "get_config",
    "save_config",
    "get_config"
]

CLOUD_CONFIG_PATH = "cloudcfg.json"
URL = "https://cdn.jsdelivr.net/gh/c15412/Cealing-Host@main/Cealing-Host.json"


def ext_dict(dic: dict, key: str , arr: list):
    if key in dic:
        dic[key].extend(arr)
    else:
        dic[key] = arr

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
        return None
    
    if js is None:
        return None

    mapper = {}
    resolver = {}
    for array in js:
        if array[1] == "":
            # for website in array[0]:
            #     resolver.append(f"MAP {website} {array[2]}")
            ext_dict(resolver, array[2], array[0])
            continue

        ext_dict(mapper, array[1], array[0])

        ext_dict(resolver, array[2], [array[1]])

    return mapper, resolver

def get_config(file=CLOUD_CONFIG_PATH):
    js = None
    try:
        with open(file, 'r') as f:
            js = json.load(f)
    except FileNotFoundError:
        return [], []
    else:
        mapper = js["mapper"]
        resolver = js["resolver"]
        return mapper, resolver

def save_config(mapper: dict, resolver: dict, file=CLOUD_CONFIG_PATH):
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

def get_config_from_web() -> tuple:
    mapper, resolver = get_config()
    if not mapper and not resolver:
        mapper, resolver = _get_config_from_web()
        if mapper is None or resolver is None:
            return [], []
        save_config(mapper, resolver)
    return mapper, resolver

if __name__ == "__main__":
    print(get_config_from_web())
