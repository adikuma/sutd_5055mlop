import json
from playwright.sync_api import sync_playwright
from readability import Document as ReadabilityDocument
from bs4 import BeautifulSoup
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from urllib.parse import urlparse
import time
import logging
import os
import re
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_JSON_FILE = "data.json"
OUTPUT_FOLDER = "markdown"
OUTPUT_JSON_FILE = os.path.join(OUTPUT_FOLDER, "markdown_data.json") 
DELAY_BETWEEN_REQUESTS = 15
LLM_TIMEOUT = 70 
PLAYWRIGHT_TIMEOUT = 60000

if not os.getenv("OPENAI_API_KEY"):
    logging.error("FATAL ERROR: OPENAI_API_KEY environment variable not set.")
    exit(1)

class MarkdownContent(BaseModel):
    markdown_output: str = Field(description="The main content extracted from the HTML, formatted as Markdown.")

def sanitize_filename(filename):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    sanitized = sanitized.replace(" ", "_")
    return sanitized[:200]

if not os.path.exists(INPUT_JSON_FILE):
    logging.error(f"Input file '{INPUT_JSON_FILE}' not found.")
    data = []
else:
    try:
        with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Loaded {len(data)} links from {INPUT_JSON_FILE}")
    except Exception as e:
        logging.error(f"An unexpected error occurred loading {INPUT_JSON_FILE}: {e}")
        data = []

if not os.path.exists(OUTPUT_FOLDER):
    logging.info(f"Creating output folder '{OUTPUT_FOLDER}'...")
    os.makedirs(OUTPUT_FOLDER)

processed_files_count = 0
output_data = [] #storage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, request_timeout=LLM_TIMEOUT)
structured_llm = llm.with_structured_output(MarkdownContent)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert assistant converting FULL HTML content to Markdown for use in a university chatbot knowledge base. "
            "Your task is to extract the main textual content from the provided FULL HTML document and format it as clean, well-structured Markdown. "
            "Focus on the primary information conveyed on the page, **aggressively omitting boilerplate** like navigation menus, headers, footers, script tags, style tags, and irrelevant sidebars. "
            "**Crucially, ensure you preserve important details relevant for a chatbot, such as:**\n"
            "*   **Specific dates** (e.g., application deadlines, event dates, term start/end dates)\n"
            "*   **Lists** (e.g., course names, module codes, programme requirements, faculty names, event schedules)\n"
            "*   **Key facts and figures** (e.g., admission criteria, fees, contact information)\n"
            "*   **Procedures and steps** (e.g., application process, appeal process)\n"
            "Preserve key structural elements like headings (using #), lists (* or 1.), and paragraphs using standard Markdown syntax. "
            "Do not add any commentary, introduction, or conclusion before or after the Markdown content. "
            "Return ONLY the Markdown content itself, ensuring all critical details mentioned above are retained accurately.",
        ),
        ("human", "Please process the following FULL HTML document:\n\n```html\n{html_snippet}\n```"),
    ]
)

llm_chain = prompt | structured_llm

logging.info("Initializing Playwright")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        logging.info("Playwright initialized")

        for index, item in enumerate(data):
            title = item.get("title", "No Title Provided")
            url = item.get("url")
            description = item.get("description", "")
            content_markdown = "" 

            if not url:
                logging.warning(f"Skipping item {index + 1}/{len(data)}: Missing URL.")
                item['markdown'] = ""
                output_data.append(item) 
                continue

            logging.info(f"Processing {index + 1}/{len(data)}: {title} ({url})")
            try:
                page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
                html_content = page.content()

                try:
                    readable_doc = ReadabilityDocument(html_content)
                    page_title = title if title != "No Title Provided" else readable_doc.short_title()
                except Exception:
                    page_title = title if title != "No Title Provided" else "Title Extraction Failed"


                if not html_content:
                     logging.warning(f"Warning: No HTML content fetched for {url}. Skipping LLM processing.")
                     item['markdown'] = "" 
                     output_data.append(item) 
                     time.sleep(DELAY_BETWEEN_REQUESTS)
                     continue

                logging.info(f"  Sending RAW HTML content (length: {len(html_content)}) to LLM for processing...")
                try:
                    structured_response = llm_chain.invoke({"html_snippet": html_content})
                    content_markdown = structured_response.markdown_output

                    if not content_markdown or not content_markdown.strip():
                        logging.warning(f"Warning: LLM returned empty or whitespace-only content for {url}. Skipping file save.")
                        content_markdown = ""

                except Exception as llm_error:
                    if "context_length_exceeded" in str(llm_error).lower():
                         logging.error(f"  LLM processing failed for {url}: Context Length Exceeded. Raw HTML likely too large.")
                    else:
                         logging.error(f"  LLM processing failed for {url}: {llm_error}")
                    content_markdown = ""

                if content_markdown:
                    safe_filename = sanitize_filename(page_title) + ".md"
                    output_filepath = os.path.join(OUTPUT_FOLDER, safe_filename)
                    escaped_description = description.replace('"', '\\"')
                    metadata_header = (
                        f"---\n"
                        f"source: {url}\n"
                        f"title: {page_title}\n"
                        f"description: \"{escaped_description}\"\n"
                        f"---\n\n"
                    )
                    full_markdown = metadata_header + content_markdown

                    try:
                        with open(output_filepath, "w", encoding="utf-8") as md_file:
                            md_file.write(full_markdown)
                        logging.info(f"  Successfully saved Markdown to: {output_filepath}")
                        processed_files_count += 1
                    except Exception as file_error:
                         logging.error(f"  Failed to write file {output_filepath}: {file_error}")
                         content_markdown = "" 

                item['markdown'] = content_markdown
                output_data.append(item) 

            except Exception as page_processing_error:
                logging.error(f"  Error processing page {url}: {page_processing_error}", exc_info=False)
                item['markdown'] = "" 
                output_data.append(item) 
            finally:
                logging.info(f"  Waiting for {DELAY_BETWEEN_REQUESTS} second(s)...")
                time.sleep(DELAY_BETWEEN_REQUESTS)

        logging.info("Closing Playwright browser...")
        browser.close()

except Exception as playwright_error:
     logging.error(f"Failed to initialize or run Playwright: {playwright_error}", exc_info=True)

if output_data:
    logging.info(f"Saving {len(output_data)} items (with added 'markdown' field) to {OUTPUT_JSON_FILE}...")
    try:
        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f_out:
            json.dump(output_data, f_out, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved combined data to {OUTPUT_JSON_FILE}.")
    except Exception as e:
        logging.error(f"Failed to save combined data to JSON file: {e}", exc_info=True)
else:
    logging.warning("No data was processed or available to save to combined JSON.")


logging.info("\nProcessing Complete")
