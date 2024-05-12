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
with open(config['beatmapset_id_file'], 'r') as beatmapset_id_file:
    for line in beatmapset_id_file:
        beatmapset_ids.append(int(line.strip()))

# Get Beatmap IDs
beatmap_ids = set()
async def main():
    for i, beatmapset_id in enumerate(tqdm(beatmapset_ids, 
        desc="Processing", unit="Beatmapset")):

        # Optional delay to reduce api calls per second
        sleep(api_call_delay)

        # Make temporary save in case of a crash
        if i % 100 == 0:
            with open(config['beatmap_id_file'], 'w') as beatmap_id_file:
                json.dump(list(beatmap_ids), beatmap_id_file)

        # Get Beatmaps from Beatmapset
        beatmapset = await api.beatmapset(beatmapset_id=beatmapset_id)
        for beatmap in beatmapset.beatmaps:
            if beatmap.mode_int in config['gamemodes']:
                beatmap_ids.add(beatmap.id)   
asyncio.run(main())
            
# Save collected Beatmap IDs
with open(config['beatmap_id_file'], 'w') as beatmap_id_file:
    beatmap_ids = list(beatmap_ids).sort()
    json.dump(beatmap_ids, beatmap_id_file)
