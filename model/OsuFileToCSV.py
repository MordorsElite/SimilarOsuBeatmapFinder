import os
import json
import pandas as pd
import warnings
import re

from tqdm import tqdm
import matplotlib.pyplot as plt
from osu_sr_calculator import calculateStarRating

# Load config
config_file_path = 'config/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Collect .osu files
osu_files = [os.path.join(config['osu_files'], file) 
             for file in os.listdir(config['osu_files']) 
             if file.endswith('.osu')]

hitobject_counts = {0: 0, 1: 0, 3: 0}  # Initialize hit object counts



with open(config['osu_csv_file'], 'w') as csv_file:  # Open CSV file for writing
    csv_file.write('ID,Total Difficulty,Aim Difficulty,Speed Difficulty,#Hitobjects,#Circle,#Slider,#Spinner,Length,Hitobjects\n')  # Write header

    warnings.filterwarnings('ignore')
    for osu_file in tqdm(osu_files):
        try:
            difficulties = calculateStarRating(
                returnAllDifficultyValues=True,
                allCombinations=False,
                verbose=False,
                filepath=osu_file)['nomod']
        except Exception as e:
            print(f"Error processing {osu_file}: {e}")
            continue
        
        with open(osu_file, 'r', encoding='UTF-8') as file:
            file_content = file.read()

            # Split the file content into sections
            sections = re.split(r'\n\n+', file_content.strip())

            # Find the HitObjects section
            hit_objects_section = None
            for section in sections:
                if section.startswith('[HitObjects]'):
                    hit_objects_section = section
                    break


            # If HitObjects section found
            if hit_objects_section:
                # Split the section into lines
                hit_objects_lines = hit_objects_section.strip().split('\n')

                # Count hitobjects per beatmap
                num_hitobjects = len(hit_objects_lines)
                hitobject_counts = {0:0, 1:0, 3:0}  # Reset hit object counts for each beatmap

                # Collect hibtobject information
                hit_objects_string = ""
                for line in hit_objects_lines[1:]:
                    parts = line.split(',')

                    # Count hit object grouped by type
                    hit_object = int(parts[3])
                    if hit_object & 1:              # Circle
                        hitobject_counts[0] += 1
                    elif (hit_object >> 1) & 1:     # Slider
                        hitobject_counts[1] += 1
                    elif (hit_object >> 3) & 1:     # Spinner
                        hitobject_counts[3] += 1
                    
                    # Save the other hit object attribute
                    x = int(parts[0])
                    y = int(parts[1])
                    time_stamp = int(parts[2])
                    hitobject_type = int(parts[3])
                    
                    hit_objects_string += f'{x},{y},{time_stamp},{hitobject_type},'

                hit_objects_string = hit_objects_string[:-1] # Remove last ','

                # Write data to CSV file
                csv_file.write(f"{os.path.basename(osu_file)[:-4]},"
                               f"{difficulties['total']},"
                               f"{difficulties['aim']},"
                               f"{difficulties['speed']},"
                               f"{num_hitobjects},"
                               f"{hitobject_counts[0]},"
                               f"{hitobject_counts[1]},"
                               f"{hitobject_counts[3]},"
                               f"{hit_objects_string}\n")
            else:
                print(osu_file)

print(hitobject_counts)
warnings.resetwarnings()
# Print confirmation message
print("CSV file created successfully!")
