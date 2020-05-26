import requests
from lxml import html
from standard_module import BaseModule, CommandInfo, CommandType


class WebModule(BaseModule):
    def __init__(self):
        super().__init__('web')
        self.commands = {
            'xpath': CommandInfo('xpath', CommandType.CALCULATION, self._xpath, 2),
            'xpath_one': CommandInfo('xpath_one', CommandType.CALCULATION, self._xpath_one, 2),
            'load': CommandInfo('load', CommandType.CALCULATION, self._load, 1),
            'content': CommandInfo('content', CommandType.CALCULATION, self._content, 1)
        }

    def _load(self, url):
        r = requests.get(url)
        return r.text

    def _xpath(self, path, text):
        tree = html.fromstring(text)
        elements = tree.xpath(path)
        return elements.__iter__()

    def _xpath_one(self, path, element):
        if isinstance(element, str):
            element = html.fromstring(element)
        elements = element.xpath(path)
        return elements[0]

    def _content(self, element):
        return ' '.join(element.text_content().split())