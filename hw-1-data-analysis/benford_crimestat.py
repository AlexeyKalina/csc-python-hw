import xml.etree.ElementTree as ET
from pprint import pprint
from urllib.request import urlopen
import matplotlib.pyplot as plt

url = 'http://crimestat.ru/loadXml/20554052'
data = urlopen(url).read().decode('utf8')
root = ET.fromstring(data)
values = root.findall('indicatorData/row/value')
print(ET.fromstring(data).find('indicatorData').attrib['name'])
digits = {i: sum(val.text[0] == str(i) for val in values) for i in range(1, 10)}
total = sum(digits.values())
percents = {i: val/total for i, val in digits.items()}

pprint(digits)
pprint(percents)

plt.bar(digits.keys(), digits.values())
plt.title('Закон Бенфорда')
plt.xlabel('цифра')
plt.ylabel('число преступлений')
plt.xticks(range(1, 10))
plt.show()
