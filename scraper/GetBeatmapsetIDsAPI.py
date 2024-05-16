import asyncio
import json
import time

from ossapi import OssapiAsync, enums, Cursor
from tqdm import tqdm

config_file_path = 'config/config.json'
api_call_delay = 0.0 # in seconds

# Load config
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Initialize async osu! APIv2
client_id = config['client_id']
client_secret = config['client_secret']
api = OssapiAsync(client_id, client_secret)

async def main(beatmapset_ids_file, beatmap_ids_file, game_mode, ranked):
    cursor = Cursor()
    beatmapsets = []
    beatmaps = []
    start_time = time.time()
    page_count = 0

    while True:
        page_count += 1
        time.sleep(api_call_delay)
        # API Call
        beatmapsets_search_result = await api.search_beatmapsets(
            mode=game_mode,
            category=ranked,
            explicit_content=enums.BeatmapsetSearchExplicitContent.SHOW,
            include_converts=False,
            cursor=cursor,
            sort=enums.BeatmapsetSearchSort.DIFFICULTY_ASCENDING
        )
        # Pagination
        cursor = beatmapsets_search_result.cursor

        # Break if no beatmapsets are returned
        if beatmapsets_search_result.beatmapsets is None:
            break

        # Save beatmap ids
        beatmap_count = 0
        for beatmapset in beatmapsets_search_result.beatmapsets:
            beatmapsets.append(beatmapset.id)
            beatmap_count += len(beatmapset.beatmaps)
            for beatmap in beatmapset.beatmaps:
                beatmaps.append(beatmap.id)

        # Periodical temporary save
        if page_count % 20 == 0:
            with open(beatmapset_ids_file, 'w') as file:
                json.dump(beatmapsets, file)

            with open(beatmap_ids_file, 'w') as file:
                json.dump(beatmaps, file)

        # Check for last page
        if cursor is None:
            print(f'Last page has been reached at page {page_count}')
            break

        end_time = time.time()
        print(f'Found page {page_count} with '
              f'{len(beatmapsets_search_result.beatmapsets)} beatmapsets '
              f'and {beatmap_count} individual beatmaps'
              f'in {end_time -  start_time:.3f}s')
        start_time = end_time

    print(f'Total number of Beatmapsets: {len(beatmapsets)}')
    print(f'Total number of Beatmaps: {len(beatmaps)}')

    with open(beatmapset_ids_file, 'w') as file:
        json.dump(beatmapsets, file)

    with open(beatmap_ids_file, 'w') as file:
        json.dump(beatmaps, file)

if __name__ == '__main__':
    base_folder = config['osu_scraping_files']
    asyncio.run(main(f'{base_folder}/beatmapset_ids_api.json', 
                     f'{base_folder}/beatmap_ids_api.json',
                     enums.BeatmapsetSearchMode.OSU,
                     enums.BeatmapsetSearchCategory.RANKED))