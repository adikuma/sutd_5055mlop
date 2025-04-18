import json
import os
import urllib.parse
import graphviz 
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_JSON_FILE = "data.json"
OUTPUT_FOLDER = "visualization"
OUTPUT_FILENAME_BASE = "url_tree" 

if not os.path.exists(OUTPUT_FOLDER):
    logging.info(f"Creating output folder '{OUTPUT_FOLDER}'...")
    os.makedirs(OUTPUT_FOLDER)

if not os.path.exists(INPUT_JSON_FILE):
    logging.error(f"Input JSON file '{INPUT_JSON_FILE}' not found.")
    exit(1)

try:
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    logging.info(f"Loaded {len(data)} items from {INPUT_JSON_FILE}")
except Exception as e:
    logging.error(f"An unexpected error occurred loading {INPUT_JSON_FILE}: {e}")
    exit(1)

logging.info("Building URL tree graph...")
dot = graphviz.Digraph(comment='SUTD URL Structure', graph_attr={'rankdir': 'TB'}) # TB = Top-to-Bottom

added_nodes = set()

for item in data:
    url = item.get("url")
    if not url:
        continue

    try:
        parsed_url = urllib.parse.urlparse(url)
        path_components = [comp for comp in parsed_url.path.split('/') if comp]

        parent_node_id = parsed_url.netloc 

        if parent_node_id not in added_nodes:
             dot.node(parent_node_id, label=parsed_url.netloc, shape='box')
             added_nodes.add(parent_node_id)

        current_path_segments = []
        for i, component in enumerate(path_components):
            current_path_segments.append(component)
            node_id = parent_node_id + "/" + "/".join(current_path_segments)

            if node_id not in added_nodes:
                dot.node(node_id, label=component)
                added_nodes.add(node_id)

            if parent_node_id:
                 dot.edge(parent_node_id, node_id)

            parent_node_id = node_id

    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}")


output_path_base = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME_BASE)
logging.info(f"Rendering graph to {output_path_base}.[png|svg]...")

try:
    dot.render(output_path_base, view=False, format='png', cleanup=True)
    dot.render(output_path_base, view=False, format='svg', cleanup=True)
    logging.info(f"Successfully saved graph files:")
    logging.info(f"  - {output_path_base}.png")
    logging.info(f"  - {output_path_base}.svg")

except graphviz.backend.execute.ExecutableNotFound:
     logging.error("Graphviz executable not found. Please ensure Graphviz is installed and its 'bin' directory is in your system's PATH.")
except Exception as e:
    logging.error(f"Failed to render or save graph: {e}")

logging.info("\n--- Tree Generation Complete ---")

