import json
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from enum import Enum
from urllib.request import build_opener, HTTPCookieProcessor


class Direction(Enum):
    UP = 0,
    DOWN = 1,
    NO = 2

    @staticmethod
    def resolve(yesterday, today):
        return Direction.UP if today > yesterday else Direction.DOWN


class NumberType(Enum):
    DIFF = 0,
    EXACT = 1


class WordType(Enum):
    ACTION = 0,
    NUMBER = 1,
    CURRENCY = 2
    DEFAULT = 3


class CurrencyType(Enum):
    DOLLAR = 0,
    EURO = 1


class CurrencyInfo:
    def __init__(self, type, yesterday, today):
        self.type = type
        self.yesterday = yesterday
        self.today = today

    def diff(self):
        return int(abs(self.today - self.yesterday) * 100)


class News:
    def __init__(self, patterns, dollar_info, euro_info, words_settings):
        self.patterns = patterns
        self.dollar_info = dollar_info
        self.euro_info = euro_info
        self.words_settings = words_settings
        self.number_type = random.choice([NumberType.DIFF, NumberType.EXACT])
        self.variants_props = dict()

    def _process_action(self, currency_info, word, word_settings):
        actual = filter(lambda v: (v['direction'] in [
            Direction.resolve(currency_info.yesterday, currency_info.today).name,
            Direction.NO.name]) and v['type'] == self.number_type.name,
                        word_settings['variants'])
        variant = random.choice(list(actual))
        self.variants_props[word] = variant
        return variant['text']

    def _process_number(self, currency_info, *_):
        return f'{currency_info.today} рублей' if self.number_type == NumberType.EXACT else \
            f'{currency_info.diff()} копейки'

    def _process_currency(self, currency_info, word, word_settings):
        variants = filter(lambda v: v['type'] == currency_info.type.name, word_settings['variants'])
        return random.choice(list(variants))['text']

    def _process_default(self, info, word, word_settings):
        if word_settings['optional'] and bool(random.getrandbits(1)):
            return ''
        variants = word_settings['variants']
        return random.choice(variants)

    def _process_prop(self, word):
        parts = word.split(':')
        name = parts[0]
        prop = parts[1]
        return self.variants_props[name][prop]

    def _process_word(self, word, currency_info):
        if ':' in word:
            return self._process_prop(word)
        else:
            word_settings = self.words_settings[word]
            process = {
                WordType.ACTION.name: self._process_action,
                WordType.NUMBER.name: self._process_number,
                WordType.CURRENCY.name: self._process_currency,
                WordType.DEFAULT.name: self._process_default
            }
            return process[word_settings['type']](currency_info, word, word_settings)

    def _generate_sentence(self, pattern, currency_info):
        self.number_type = random.choice([NumberType.DIFF, NumberType.EXACT])
        sentence = ''
        for word in pattern.split(' '):
            result = self._process_word(word, currency_info)
            if result != '':
                sentence += f'{result} '
        return f'{sentence[0].upper()}{sentence.strip()[1:]}.'

    def generate_title(self):
        pattern = random.choice(self.patterns)
        return self._generate_sentence(pattern, self.dollar_info)

    def generate_text(self, ending):
        sentences = []
        for currency in [self.dollar_info, self.euro_info]:
            pattern = random.choice(self.patterns)
            sentences.append(self._generate_sentence(pattern, currency))
        sentences.append(random.choice(ending))
        return ' '.join(sentences)


class Reporter:
    def __init__(self, settings_path='patterns.json'):
        with open(settings_path, 'r') as file:
            self._settings = json.load(file)

    @staticmethod
    def _load_data(yesterday, today, currency):
        date_format = '%d/%m/%Y'
        values = []
        date2 = today.strftime(date_format)
        opener = build_opener(HTTPCookieProcessor())
        while len(values) != 2:
            date1 = yesterday.strftime(date_format)
            url = f'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date1}&date_req2={date2}&VAL_NM_RQ={currency}'
            data = opener.open(url).read().decode('utf8')
            values = ET.fromstring(data).findall('*//Value')
            yesterday = yesterday - timedelta(1)
        to_float = lambda s: float(s.replace(',', '.'))
        return to_float(values[0].text), to_float(values[1].text)

    def generate_news(self, count):
        today = datetime.now()
        yesterday = today - timedelta(3)
        dollar_info = CurrencyInfo(CurrencyType.DOLLAR, *self._load_data(yesterday, today, 'R01235'))
        euro_info = CurrencyInfo(CurrencyType.EURO, *self._load_data(yesterday, today, 'R01239'))
        for i in range(0, count):
            news = News(self._settings['patterns'], dollar_info, euro_info, self._settings['dict'])
            print(f'{i+1}. {news.generate_title()}')
            print(f'\t{news.generate_text(self._settings["ending"])}')


Reporter().generate_news(10)
