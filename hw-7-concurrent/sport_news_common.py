import json
from dataclasses import dataclass


@dataclass
class NewsSite:
    name: str
    url: str
    xpath: str
    encoding: str
    is_sport_site: bool


with open('sites.json', 'r') as file:
    sites = json.load(file, object_hook=lambda dct: NewsSite(dct['name'], dct['url'], dct['xpath'], dct['encoding'], dct['is_sport_site']))