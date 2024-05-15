import os
import requests
import json
from tqdm import tqdm
from time import sleep

config_file_path = 'config/config.json'
api_call_delay = 0

# Load config
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Create output folder if it doesn't exist
if not os.path.exists(config['osu_files']):
    os.makedirs(config['osu_files'])

# Load Beatmap IDs
with open(config['beatmap_id_file']) as beatmap_id_file:
    beatmap_ids = json.load(beatmap_id_file)

success_counter = 0
error_counter = 0

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

# Download .osu files for all beatmap IDs
for beatmap_id in tqdm(beatmap_ids, desc="Processing", unit="Beatmap"):
    sleep(api_call_delay)
    if download_osu_file(beatmap_id):
        success_counter += 1
    else: 
        error_counter += 1

print(f'Success: {success_counter}, Error: {error_counter}')
