import datetime
from statistics import mean
from more_itertools import partition
from sport_news_common import *


def report_stats(file_name):
    site_to_hash = {}
    site_to_count = {}
    is_first = True
    with open(file_name) as f:
        for line in f:
            parts = line.split()
            log_time = datetime.datetime.strptime(f'{parts[0]} {parts[1]}', '%Y-%m-%d %H:%M:%S,%f')
            if is_first:
                first = log_time
                is_first = False
            else:
                last = log_time
            site = parts[2]
            hash = parts[3]
            if site not in site_to_hash:
                site_to_count[site] = 0
            elif site_to_hash[site] != hash:
                site_to_count[site] += 1
            site_to_hash[site] = hash

    duration = (last - first).seconds / 3600
    sites_by_uph = [(k, v / duration) for k, v in sorted(site_to_count.items(), key=lambda item: -item[1])]
    news_sites, sport_sites = partition(lambda item: (next(x for x in sites if item[0] == x.name)).is_sport_site, sites_by_uph)
    report(list(sport_sites), True)
    report(list(news_sites), False)


def report(sites2uph, is_sport_sites):
    print('Спортивные новостные сайты:') if is_sport_sites else print('Спортивные рубрики глобальных новостных порталов:')
    print(f'Средний UPH: {mean(map(lambda item: item[1], sites2uph))}\n')
    for site2uph in sites2uph:
        print(f'{site2uph[0]}: {site2uph[1]}')
    print()


report_stats('sport-news.log')
