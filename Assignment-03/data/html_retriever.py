import logging
import json
import requests
import os

logging.basicConfig(level=logging.INFO)

data_list = []
INPUT_JSON_FILE = "data.json"
OUTPUT_DIR = "html"
OUTPUT_JSON_FILE = "html/html_data.json"
if os.path.exists(OUTPUT_DIR):
    logging.warning(f"Directory {OUTPUT_DIR} already exists")
else:
    os.mkdir(OUTPUT_DIR)

logging.info(f"Retrieving data from {INPUT_JSON_FILE}")
with open(INPUT_JSON_FILE, "r") as f:
    data_list = json.load(f)
    
for data in data_list:
    url = data["url"]
    reqs = requests.get(url)
    logging.debug(f"Retrieving {url}")
    title = data["title"]
    data["html"] = reqs.text
    if f"{title}.html" in os.listdir(OUTPUT_DIR):
        continue
    with open(f"{OUTPUT_DIR}/{title}.html",  "w") as f:
        f.write(reqs.text)

    logging.info(f"Saved {title}.html")

logging.info(f"Length of data: {len(data_list)}")
data_json = json.dumps(data_list, indent=4)
with open(OUTPUT_JSON_FILE, "w") as f:
    f.write(data_json)
        