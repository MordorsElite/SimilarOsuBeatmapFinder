from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import json

json_file_path = "scraper/items.json"
ids_file_path = "scraper/ids.txt"

sleep_time = 3

# Set up the WebDriver
driver = webdriver.Chrome()  # Or specify the path to your WebDriver executable

# Open the website
driver.get("https://osu.ppy.sh/beatmapsets")


ids = set()

# Define a function to scroll to the bottom of the page
def scroll_to_bottom():
    scroll_counter = 0
    total_item_count = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_counter += 1

        # Wait for new content to load
        time.sleep(sleep_time)  # Adjust sleep time as needed

        # Find items
        items = driver.find_elements(By.XPATH, "//div[@class='beatmapsets__item']")

        # Add whole items to json file
        with open(json_file_path, 'a') as json_file:
            for i, item in enumerate(items):
                if i == 0:
                    #print(item.get_attribute('outerHTML'))
                    pass
                total_item_count += 1
                json.dump({f'item_{total_item_count}': item.get_attribute('outerHTML')}, json_file)
                json_file.write('\n')

        # Collect all ids
        for item in items:
            beatmapset_id_match = re.search(r'/beatmapsets/(\d+)', item.get_attribute('outerHTML'))
            beatmapset_id = beatmapset_id_match.group(1)
            ids.add(beatmapset_id)

        if scroll_counter % 100 == 0:
            print(f'Found ids: {len(ids)}: {list(ids)[:10]}...')

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Scroll to the bottom of the page to load all items
scroll_to_bottom()
    
# Collect all IDs in ids.txt
with open(ids_file_path, 'w') as id_file:
    for id in ids:
        id_file.write(id + "\n")

## Convert items.json to a valid json format
# Read the file line by line
with open(json_file_path, 'r') as f:
    lines = f.readlines()

# Initialize an empty list to store JSON objects
json_list = []

# Iterate over each line and treat it as a JSON object
for line in lines:
    json_obj = json.loads(line)
    json_list.append(json_obj)

# Dump the list of JSON objects into a valid JSON format
with open(json_file_path, 'w') as f:
    json.dump(json_list, f, indent=4)


# Close the browser
driver.quit()
