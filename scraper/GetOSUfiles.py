import os
import requests
import json
from tqdm import tqdm
from time import sleep

# Load config
config_file_path = 'config/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Function to download .osu file for a given beatmap ID
def download_osu_file(beatmap_id):
    url = f"https://osu.ppy.sh/osu/{beatmap_id}"
    response = requests.get(url)
    if response.status_code == 200:
        file_name = f"{beatmap_id}.osu"
        file_path = os.path.join(config['osu_files'], file_name)
        with open(file_path, "wb") as file:
            file.write(response.content)
        return True
    return False

def downloader_loop(beatmap_ids, start_index=None, 
                    end_index=None, api_call_delay=0.0):
    success_counter = 0
    error_counter = 0

    if end_index is not None:
        beatmap_ids[:end_index]
    if start_index is not None:
        beatmap_ids[start_index:]

    # Download .osu files for all beatmap IDs
    for beatmap_id in tqdm(beatmap_ids, unit=" Beatmap"):
        sleep(api_call_delay)
        if download_osu_file(beatmap_id):
            success_counter += 1
        else: 
            error_counter += 1

    print(f'Success: {success_counter}, Error: {error_counter}')

if __name__ == '__main__':
    api_call_delay = 0
    #beatmap_ids = config['beatmap_id_file']
    beatmap_ids = 'data/examples/all_ranked_beatmap_ids_2024_05_15.json'

    # Create output folder if it doesn't exist
    if not os.path.exists(config['osu_files']):
        os.makedirs(config['osu_files'])

    # Load Beatmap IDs
    with open(beatmap_ids) as beatmap_id_file:
        beatmap_ids = json.load(beatmap_id_file)
    beatmap_ids.sort()

    downloader_loop(beatmap_ids)
    
    print(f'{len(beatmap_ids)} Beatmap-IDs loaded\n')

