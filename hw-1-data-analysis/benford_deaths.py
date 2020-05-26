import xml.etree.ElementTree as ET
from pprint import pprint
from urllib.request import urlopen
import matplotlib.pyplot as plt

url = 'https://data.gov.ru/opendata/7708234640-threeathreeafiveafiveanine/' \
      'data-20150507T0100-structure-20150507T0100.xml?encoding=UTF-8 '
nmsp = {'message': 'http://www.SDMX.org/resources/SDMXML/schemas/v1_0/message'}
data = urlopen(url).read().decode('utf8')
root = ET.fromstring(data.replace('generic:', ''))
print(ET.fromstring(data).find('*//message:Indicator', nmsp).attrib['name'])
values = root.findall('*//message:ObsValue', nmsp)
digits = {i: sum(val.attrib['value'][0] == str(i) for val in values) for i in range(1, 10)}
total = sum(digits.values())
percents = {i: val/total for i, val in digits.items()}

pprint(digits)
pprint(percents)

plt.bar(digits.keys(), digits.values())
plt.title('Закон Бенфорда')
plt.xlabel('цифра')
plt.ylabel('число смертей')
plt.xticks(range(1, 10))
plt.show()
