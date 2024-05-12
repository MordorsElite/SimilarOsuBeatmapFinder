from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import json

config_file_path = 'config/config.json'
scroll_sleep_time = 1.0

# Load config
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Set up the WebDriver
driver = webdriver.Chrome()  # Or specify the path to your WebDriver executable

# Open the website
driver.get("https://osu.ppy.sh/beatmapsets")

# Initialize set of beatmapset ids
beatmapset_ids = set()

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
        time.sleep(scroll_sleep_time)  # Adjust sleep time as needed

        # Find items
        items = driver.find_elements(By.XPATH, "//div[@class='beatmapsets__item']")

        # Collect all ids
        for item in items:
            beatmapset_id_match = re.search(r'/beatmapsets/(\d+)', 
                item.get_attribute('outerHTML'))
            beatmapset_id = beatmapset_id_match.group(1)
            beatmapset_ids.add(beatmapset_id)

        # Make temporary backup in case of crash
        if scroll_counter % 100 == 0:
            with open(config['beatmapset_id_file'], 'w') as beatmapset_id_file:
                json.dump(list(beatmapset_ids), beatmapset_id_file)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Scroll to the bottom of the page to load all items
scroll_to_bottom()
    
# Collect all IDs in ids.txt
with open(config['beatmapset_id_file'], 'w') as beatmapset_id_file:
    beatmapset_ids = list(beatmapset_ids).sort()
    json.dump(beatmapset_ids, beatmapset_id_file)

# Close the browser
driver.quit()
