import json
import csv
from tqdm import tqdm

# Load config
config_file_path = 'config/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Cuts down number of hit_objects without padding
def extract_hit_objects(input_csv_path:str, output_csv_path:str, 
                        num_hit_objects:int) -> None:
    with open(input_csv_path, 'r') as input_file, \
        open(output_csv_path, 'w', newline='') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)
        for row in tqdm(reader):
            # Extract general information
            general_info = row[:5]
            
            # Extract hit objects
            hit_objects = row[5:]
            
            # Determine how many hit objects to keep
            hit_objects_to_keep = min(len(hit_objects) // 4, num_hit_objects)
            
            # Construct new row
            new_row = general_info + hit_objects[:hit_objects_to_keep * 4]
            
            # Write new row to output CSV
            writer.writerow(new_row)


# Sets exact number of required hitobjects for each beatmap 
# and pads with '-1,-1,-1,-1' if neccessary
def extract_hit_objects_with_padding(input_csv_path:str, output_csv_path:str, 
                                     num_hit_objects:int, num_beatmaps:int=-1):
    with open(input_csv_path, 'r') as input_file, \
        open(output_csv_path, 'w', newline='') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)
        for i, row in tqdm(enumerate(reader, start=0)):
            # Stops CSV once num_beatmaps has been reached
            if num_beatmaps > 0 and i > num_beatmaps:
                break
            # Extract general information
            general_info = row[:8]
            
            # Extract hit objects
            hit_objects = row[8:]
            
            # Determine how many hit objects to keep
            hit_objects_to_keep = min(len(hit_objects) // 4, num_hit_objects)
            
            # Pad hit objects if fewer than num_hit_objects
            padded_hit_objects = hit_objects[:hit_objects_to_keep * 4] + \
                (['-1'] * (num_hit_objects - hit_objects_to_keep) * 4)

            # Skip label row
            if i == 0:
                padded_hit_objects = []
            
            # Construct new row
            new_row = general_info + padded_hit_objects
            
            # Write new row to output CSV
            writer.writerow(new_row)


# Function to check if any of the hit-object parameters are negative (irrelevant)
def check_negative_hit_objects(input_csv_path:str) -> None:
    with open(input_csv_path, 'r') as input_file:
        reader = csv.reader(input_file)
        for i, row in tqdm(enumerate(reader, start=1)):
            if i == 1:
                continue
            # Extract hit objects
            hit_objects = row[5:]
            for j, value in enumerate(hit_objects, start=1):
                # Check if value is negative
                if int(value) < 0:
                    print(f"Negative hit object value found in row {i}, column {j}: {value}")




if __name__ == '__main__':
    num_beatmaps = -1
    num_hit_objects = 504  # Set the desired number of hit objects per line
    input_csv_path = config['osu_csv_file']
    base_data_path = config['osu_data']
    output_csv_path = f'{base_data_path}/osu_data_{num_beatmaps}bm_{num_hit_objects}hitobj_padded.csv'

    #extract_hit_objects(input_csv_path, output_csv_path, num_hit_objects)
    #check_negative_hit_objects(input_csv_path)
    extract_hit_objects_with_padding(input_csv_path, output_csv_path, num_hit_objects, num_beatmaps)
