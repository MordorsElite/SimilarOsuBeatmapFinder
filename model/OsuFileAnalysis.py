import os
import json
import pandas
import warnings

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

beatmap_lengths = []
hitobjects_per_beatmap = []
hitobject_positions_x = []
hitobject_positions_y = []

warnings.filterwarnings('ignore')
star_ratings_aim = []
star_ratings_speed = []
star_ratings_total = []


for osu_file in tqdm(osu_files[:200]):

    difficulties = calculateStarRating(
        returnAllDifficultyValues=True,
        allCombinations=False,
        verbose=False,
        filepath=osu_file)['nomod']
    
    star_ratings_aim.append(difficulties['aim'])
    star_ratings_speed.append(difficulties['speed'])
    star_ratings_total.append(difficulties['total'])
    
    with open(osu_file, 'r', encoding='UTF-8') as file:
        file_content = file.read()

        # Split the file content into sections
        sections = file_content.strip().split('\n\n')

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
            hitobjects_per_beatmap.append(len(hit_objects_lines))

            # Get the last line
            last_line = hit_objects_lines[-1]
            
            # Split the last line by comma
            parts = last_line.split(',')
            
            # Extract the third argument
            third_argument = parts[2]

            # Add to list
            beatmap_lengths.append(int(third_argument))

            for line in hit_objects_lines[1:]:
                parts = line.split(',')
                x = int(parts[0])
                y = int(parts[1])
                if 0 <= x <= 512 and 0 <= y <= 384:  # Limit to specified range
                    hitobject_positions_x.append(x)
                    hitobject_positions_y.append(y) 

warnings.resetwarnings()

# to CSV of form: id (filename), total_diff, aim_diff, speed_diff, #hitobjects, #circle, #slider, #spinner, length, Hitobjects[x, y, timing, type]
########## TO DO ###########

# Plot data
plt.figure(figsize=(18, 6))

plt.subplot(1, 3, 1)
plt.hist(beatmap_lengths, bins=range(0, 300000, 3000), color='skyblue', edgecolor='black')
plt.xlabel('Beatmap Length')
plt.ylabel('Frequency')
plt.title('Distribution of Beatmap Lengths')
plt.xlim(0, 300000)

plt.subplot(1, 3, 2)
plt.hist(hitobjects_per_beatmap, bins=range(0, 2501, 50), color='salmon', edgecolor='black')
plt.xlabel('Number of Hitobjects per Beatmap')
plt.ylabel('Frequency')
plt.title('Distribution of Hitobjects per Beatmap')
plt.xlim(0, 2500)

plt.subplot(1, 3, 3)
plt.hist2d(hitobject_positions_x, hitobject_positions_y, bins=(50, 50), cmap='plasma')
plt.colorbar(label='Frequency')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.title('Heatmap of Hitobject Positions')

plt.tight_layout()
plt.show()

print(f'Average beatmap length: {sum(beatmap_lengths) / len(beatmap_lengths):.3f}')
print(f'Average hitobjects per beatmap: {sum(hitobjects_per_beatmap) / len(hitobjects_per_beatmap)}')






plt.figure(figsize=(18, 6))

plt.subplot(1, 3, 1)
plt.hist(star_ratings_aim, bins=100, color='gold', edgecolor='black')
plt.xlabel('Star Ratings')
plt.ylabel('Frequency')
plt.title('Distribution of Star Ratings AIM')

plt.subplot(1, 3, 2)
plt.hist(star_ratings_speed, bins=100, color='gold', edgecolor='black')
plt.xlabel('Star Ratings')
plt.ylabel('Frequency')
plt.title('Distribution of Star Ratings SPEED')

plt.subplot(1, 3, 3)
plt.hist(star_ratings_total, bins=100, color='gold', edgecolor='black')
plt.xlabel('Star Ratings')
plt.ylabel('Frequency')
plt.title('Distribution of Star Ratings TOTAL')

plt.tight_layout()
plt.show()