import json
import multiprocessing
import os
import re
import time
import warnings
from queue import Queue

from osu_sr_calculator import calculateStarRating
from tqdm import tqdm

# Load config
config_file_path = 'config/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

star_rating_error_counter = multiprocessing.Value('i', 0)

def osuToCSV(csv_file_path, osu_file_paths, progress_queue):
    global star_rating_error_counter
    warnings.filterwarnings('ignore')


    with open(csv_file_path, 'w') as csv_file:  # Open CSV file for writing

        hitobject_counts = {0: 0, 1: 0, 3: 0}  # Initialize hit object counts
        for osu_file in osu_file_paths:
            try:
                difficulties = calculateStarRating(
                    returnAllDifficultyValues=True,
                    allCombinations=False,
                    verbose=False,
                    filepath=osu_file)['nomod']
            except Exception as e:
                with star_rating_error_counter.get_lock():
                    star_rating_error_counter.value += 1
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
                    # Reset hit object counts for each beatmap
                    hitobject_counts = {0:0, 1:0, 3:0}  

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
                    progress_queue.put(1)
                else:
                    print(f'No hitobjects in {osu_file}')

def worker(input_queue:Queue, output_queue:Queue, progress_queue, num_batches:int):
    while True:
        new_task = input_queue.get()
        if new_task is not None:
            index, osu_file_batch = new_task
        else:
            break

        temp_file_path = os.path.join(config['temp_files'], f"temp_result_{index}.txt")
        osuToCSV(temp_file_path, osu_file_batch, progress_queue)
        output_queue.put((index, temp_file_path))

        input_queue.task_done()

def tqdm_worker(progress_queue, total):
    pbar = tqdm(total=total, unit=' beatmaps')
    while True:
        update = progress_queue.get()
        if update is None:
            break
        pbar.update(update)
    pbar.close()

def main(batch_size=100):
    start_time = time.time()
    num_cores = multiprocessing.cpu_count()
    input_queue = multiprocessing.JoinableQueue()
    output_queue = multiprocessing.Queue()
    progress_queue = multiprocessing.Queue()
    processes = []

    # Collect .osu files
    osu_files = [os.path.join(config['osu_files'], file) 
                 for file in os.listdir(config['osu_files']) 
                 if file.endswith('.osu')]
    osu_files_100 = [osu_files[i:i + batch_size] 
                     for i in range(0, len(osu_files), batch_size)]
    num_batches = len(osu_files_100)

    print(f'Processing {len(osu_files)} beatmaps in {num_batches} '
          f'batches using {num_cores} cores\n')

    # Add .osu file list batches to queue
    for i, batch in enumerate(osu_files_100):
        input_queue.put((i, batch))
    
    # Start tqdm progress bar
    tqdm_process = multiprocessing.Process(target=tqdm_worker, 
        args=(progress_queue, len(osu_files)))
    tqdm_process.start()

    for i in range(num_cores):
        process = multiprocessing.Process(target=worker, 
            args=(input_queue, output_queue, progress_queue, num_batches))
        process.start()
        processes.append(process)

    input_queue.join()

    for _ in range(num_cores):
        input_queue.put(None)

    progress_queue.put(None)
    tqdm_process.join()

    for process in processes:
        process.join()

    temp_files = {}
    while not output_queue.empty():
        index, temp_file = output_queue.get()
        temp_files.update({index: temp_file})

    print(f'\nCombining {len(temp_files)} temp files:\n')

    with open(config['osu_csv_file'], 'w') as main_file:
        main_file.write('ID,Total Difficulty,Aim Difficulty,Speed Difficulty,'
                        '#Hitobjects,#Circle,#Slider,#Spinner,Length,Hitobjects\n')
        for i in tqdm(range(num_batches), unit=' files'):
            with open(temp_files[i], 'r') as temp:
                main_file.write(temp.read())
            os.remove(temp_files[i])
    
    warnings.resetwarnings()

    total_time = time.time() - start_time
    print(f'\nProcessed {len(osu_files)} beatmaps in {total_time:.3f}s '
          f'({star_rating_error_counter.value} ignored)')

if __name__ == '__main__':
    main(batch_size=100)
