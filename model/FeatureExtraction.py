import os
import json

config_file_path = 'config/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

osu_files = [file for file in os.listdir(config['osu_files']) if file.endswith('.osu')]

print(len(osu_files))
