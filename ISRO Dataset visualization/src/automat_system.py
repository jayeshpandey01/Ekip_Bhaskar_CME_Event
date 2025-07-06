import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# --- Configurations ---
BASE_URL = "https://pradan.issdc.gov.in/al1/protected/browse.xhtml?id=suit"
LOCAL_DIR = "fits_images"
CSV_FILE = "fits_image_log.csv"
USER_AGENT = "Mozilla/5.0"

# --- Ensure directory exists ---
os.makedirs(LOCAL_DIR, exist_ok=True)

# --- Initialize existing image set from directory ---
existing_files = set(os.listdir(LOCAL_DIR))

# --- Load existing CSV if exists ---
if os.path.exists(CSV_FILE):
    existing_df = pd.read_csv(CSV_FILE)
    downloaded_files = set(existing_df['filename'])
else:
    existing_df = pd.DataFrame(columns=['filename', 'url', 'date_downloaded'])
    downloaded_files = set()

# --- Request the page ---
headers = {"User-Agent": USER_AGENT}
response = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# --- Extract .fits links ---
new_entries = []
for a_tag in soup.find_all("a", href=True):
    href = a_tag["href"]
    if href.endswith(".fits"):
        fits_url = urljoin(BASE_URL, href)
        filename = href.split("/")[-1]

        # Skip if already downloaded
        if filename in existing_files or filename in downloaded_files:
            continue

        print(f"Downloading: {filename}")
        try:
            file_data = requests.get(fits_url, stream=True)
            file_path = os.path.join(LOCAL_DIR, filename)
            with open(file_path, "wb") as f:
                for chunk in file_data.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Add entry to CSV data
            new_entries.append({
                "filename": filename,
                "url": fits_url,
                "date_downloaded": datetime.now().isoformat()
            })

        except Exception as e:
            print(f"Failed to download {filename}: {e}")

# --- Append to or create CSV ---
if new_entries:
    new_df = pd.DataFrame(new_entries)
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
    final_df.to_csv(CSV_FILE, index=False)
    print(f"\n✅ CSV updated with {len(new_entries)} new entries.")
else:
    print("\n📁 No new files to download. Everything is up to date.")
