import asyncio
import json
from time import sleep

from ossapi import OssapiAsync
from tqdm import tqdm

config_file_path = 'config/config.json'
api_call_delay = 0.25

# Load config
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Initialize async osu! APIv2
client_id = config['client_id']
client_secret = config['client_secret']
api = OssapiAsync(client_id, client_secret)

# Load BeatmapSET IDs
beatmapset_ids = []
with open(config['beatmapset_id_file']) as beatmapset_id_file:
    for line in beatmapset_id_file:
        beatmapset_ids.append(int(line.strip()))

# Get Beatmap IDs
beatmap_ids = set()
async def main():
    for i, beatmapset_id in enumerate(tqdm(beatmapset_ids, desc="Processing", unit="Beatmapset")):
        sleep(api_call_delay)
        if i % 100 == 0:
            with open(config['beatmap_id_file_temp'], 'w') as temp_save:
                json.dump(list(beatmap_ids), temp_save)
        beatmapset = await api.beatmapset(beatmapset_id=beatmapset_id)
        #print(f'BMS {beatmapset_id}: {len(beatmapset.beatmaps)}')
        for beatmap in beatmapset.beatmaps:
            #print(f'BM {beatmap.id}: {beatmap.mode_int}')
            if beatmap.mode_int in config['gamemodes']:
                beatmap_ids.add(beatmap.id)   
asyncio.run(main())
            
# Save collected Beatmap IDs
with open(config['beatmap_id_file'], "w") as beatmap_id_file:
    for beatmap_id in beatmap_ids:
        beatmap_id_file.write(str(beatmap_id) + "\n")
        
with open(config['beatmap_id_file_temp'], 'w') as temp_save:
    json.dump(list(beatmap_ids), temp_save)
