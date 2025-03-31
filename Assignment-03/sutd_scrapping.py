import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# Define the output directory for storing scraped content
OUTPUT_DIR = "./zomato_technology"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# List of Zomato blog URLs to scrape
URLS = [
    "https://blog.zomato.com/apache-flink-journey-zomato-from-inception-to-innovation",
    "https://blog.zomato.com/introducing-pos-developer-platform-simplifying-integration-with-easy-to-use-tools",
    # Add more URLs here...
]
# Function to download files (e.g., images) from a URL
def download_file(url, output_path):
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
# Function to save HTML content to a file
def save_html(content, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
# Function to extract text content (markdown) from HTML
def extract_markdown(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()
    return text
# Function to create a folder for each page based on its title
def create_page_folder(title):
    folder_name = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_')
    folder_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
# Function to scrape an individual page
def scrape_page(url, session):
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.string if soup.title else "Untitled"
        page_folder = create_page_folder(title)
        # Save HTML
        html_path = os.path.join(page_folder, "page.html")
        save_html(str(soup), html_path)
        # Save markdown
        markdown_path = os.path.join(page_folder, "page.md")
        markdown_content = extract_markdown(response.content)
        save_html(markdown_content, markdown_path)
        # Download and save images
        images = soup.find_all("img")
        for i, img in enumerate(images):
            img_url = img.get("src")
            if img_url:
                img_url = urljoin(url, img_url)
                img_name = f"image_{i}.jpg"
                img_path = os.path.join(page_folder, img_name)
                download_file(img_url, img_path)
    else:
        print(f"Failed to scrape {url}: {response.status_code}")
# Function to scrape all URLs in the list
def scrape_all_urls(urls):
    session = requests.Session()
    for url in urls:
        print(f"Scraping: {url}")
        scrape_page(url, session)
# Main function to start the scraping process
if __name__ == "__main__":
    scrape_all_urls(URLS)