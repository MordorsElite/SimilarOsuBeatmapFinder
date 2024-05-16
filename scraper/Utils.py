import asyncio
import json
from time import sleep

from ossapi import OssapiAsync
from tqdm import tqdm

config_file_path = 'config/config.json'

# Load config
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

def ids_json_difference(ids_file_include, ids_file_exclude, 
                        ids_file_difference):
    with open(ids_file_include, 'r') as include_file:
        include_ids = json.load(include_file)

    with open(ids_file_exclude, 'r') as exclude_file:
        exclude_ids = json.load(exclude_file)

    include_set = set(include_ids)
    exclude_set = set(exclude_ids)

    difference = include_set - exclude_set

    print(f'include_set: {len(include_set)}')
    print(f'exclude_set: {len(exclude_set)}')
    print(f'difference: {len(difference)} '
          f'({len(include_set) - len(exclude_set)})')

    with open(ids_file_difference, 'w') as difference_file:
        json.dump(list(difference), difference_file)

if __name__ == '__main__':
    ids_json_difference(
        'data/scraping_files/beatmapset_ids_api.json',
        'data/scraping_files/beatmapset_ids.json',
        'data/scraping_files/beatmapset_difference_ids.json')