import concurrent
import hashlib
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import urlopen
from lxml import html
from sport_news_common import *


def process_site(site):
    data = urlopen(site.url).read().decode(encoding=site.encoding)
    tree = html.fromstring(data)
    elements = tree.xpath(site.xpath)
    if len(elements) > 0:
        content = ' '.join(elements[0].text_content().split())
        h = hashlib.md5()
        h.update(content.encode('utf8'))
        return h.hexdigest()
    else:
        raise RuntimeError("No elements found by xpath")


def collect_logs(file_name):
    logging.basicConfig(filename=file_name, level=logging.INFO, format='%(asctime)s %(message)s')
    with ThreadPoolExecutor(len(sites)) as executor:
        while True:
            future_to_site = {executor.submit(process_site, site): site for site in sites}
            for future in concurrent.futures.as_completed(future_to_site):
                site = future_to_site[future]
                try:
                    result = future.result()
                except Exception as exc:
                    print(f'{site.name} generated an exception: {exc}')
                else:
                    logging.info(f'{site.name} {result}')
            time.sleep(60)


collect_logs('sport-news.log')
