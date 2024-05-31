import json
import os
import shutil

from tqdm import tqdm

# Load config
config_file_path = 'config/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

v14_counter = 0
non_v14_counter = 0

osu_files_dir = config['osu_files']
osu_file_paths = os.listdir(osu_files_dir)
not_v14_dir = os.path.join(osu_files_dir, "not_v14")

# Create the "not_v14" subfolder if it doesn't exist
if not os.path.exists(not_v14_dir):
    os.makedirs(not_v14_dir)

print(osu_file_paths[:10])

for i, osu_file_name in enumerate(tqdm(osu_file_paths)):
    osu_file_path = os.path.join(osu_files_dir, osu_file_name)
    if not os.path.isfile(osu_file_path):
        continue
    with open(osu_file_path, 'r', encoding='UTF-8') as osu_file:
        try:
            first_line = osu_file.readline().strip()
        except Exception as e:
            print(f'Error for {osu_file_name}: {e}')
        if first_line == config['required_file_version']:
            v14_counter += 1
        else:
            non_v14_counter += 1
            # Close the file before moving
            osu_file.close()
            # Move the file to the "not_v14" subfolder
            shutil.move(os.path.join(osu_files_dir, osu_file_name), 
                        os.path.join(not_v14_dir, osu_file_name))

print(f'v14: {v14_counter}, not v14: {non_v14_counter}')