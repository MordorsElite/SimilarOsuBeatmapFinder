from ossapi import ossapiv2_async
import json

config_file_path = 'config/config.json'

with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

client_id = config['client_id']
client_secret = config['client_secret']