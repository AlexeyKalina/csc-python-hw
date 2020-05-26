import itertools
import sys
from collections import Counter
from pymongo import MongoClient


class Museum:
    def __init__(self, id, name, address):
        self.id = id
        self.name = name
        self.address = address


class Exhibit:
    def __init__(self, name, description, type, museum_id):
        self.name = name
        self.description = description
        self.type = type
        self.museum_id = museum_id


class DataLayer:
    def __init__(self):
        self._db = MongoClient().csc

    def load_museums(self):
        return map(lambda x: Museum(x['id'], x['name'], x['addressString']),
                   self._db.museums.find({}))

    def find_exhibits(self, query):
        return map(lambda x: Exhibit(x['data']['name'],
                                     x['data'].get('description', ''),
                                     x['data'].get('typology', {'name': 'unknown'})['name'],
                                     x['data']['museum']['id']),
                   self._db.exhibits.find({"$text": {"$search": query}}))


class Suggestion:
    def __init__(self, museum, in_cur_city):
        self.museum = museum
        self.in_cur_city = in_cur_city
        self.exhibits = list()


class Suggester:
    def __init__(self, cur_city):
        self.cur_city = cur_city
        self.data_layer = DataLayer()
        self.museums = {museum.id: museum for museum in self.data_layer.load_museums()}

    def suggest(self, query):
        suggestions = dict()
        for exhibit in self.data_layer.find_exhibits(query):
            self._add_exhibit(exhibit, suggestions)
        return suggestions.values()

    def _add_exhibit(self, exhibit, suggestions):
        if exhibit.museum_id not in self.museums:
            return
        if exhibit.museum_id not in suggestions:
            museum = self.museums[exhibit.museum_id]
            in_cur_city = self.cur_city in museum.address
            suggestions[exhibit.museum_id] = Suggestion(museum, in_cur_city)
        suggestions[exhibit.museum_id].exhibits.append(exhibit)


class Printer:
    def __init__(self):
        sys.stdout.write('Введите ваш город: ')
        cur_city = sys.stdin.readline().strip()
        self.suggester = Suggester(cur_city)

    def suggest(self):
        sys.stdout.write('\nВведите запрос: ')
        query = sys.stdin.readline().strip()
        suggestions = self.suggester.suggest(query)
        print("\nСамые подходящие в вашем городе:")
        self._print(filter(lambda x: x.in_cur_city, suggestions))
        print("\nСамые подходящие в других городах:")
        self._print(filter(lambda x: not x.in_cur_city, suggestions))

    def _print(self, suggestions):
        for i, suggestion in enumerate(itertools.islice(sorted(suggestions, key=lambda x: -len(x.exhibits)), 5)):
            print(f"{i+1}. {suggestion.museum.name}")
            print(f"\tАдрес: {suggestion.museum.address}")
            print(f"\tСоответствующие экспонаты ({len(suggestion.exhibits)}):")
            types = Counter(map(lambda x: x.type, suggestion.exhibits))
            for j, type2count in enumerate(types.most_common()):
                print(f"\t\t{j+1}. {type2count[0]} ({type2count[1]})")


printer = Printer()
while True:
    printer.suggest()
