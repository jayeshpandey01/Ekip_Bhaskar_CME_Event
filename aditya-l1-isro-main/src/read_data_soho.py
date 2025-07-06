import os
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sohoftp.nascom.nasa.gov/sdb/goes/ace/daily/"
LOCAL_ROOT = "ace_daily"

def download_ace_files():
    # Step 1: Get file list from the web directory
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a', href=True)
    txt_files = [link['href'] for link in links if link['href'].endswith('.txt')]

    # Step 2: Create root folder
    os.makedirs(LOCAL_ROOT, exist_ok=True)

    for file in txt_files:
        year = file[:4] if file[:4].isdigit() else "unknown"
        year_dir = os.path.join(LOCAL_ROOT, year)
        os.makedirs(year_dir, exist_ok=True)

        dest_path = os.path.join(year_dir, file)
        file_url = BASE_URL + file

        if os.path.exists(dest_path):
            print(f"Skipping: {file}")
            continue

        print(f"Downloading: {file_url}")
        try:
            r = requests.get(file_url)
            with open(dest_path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print(f"Error downloading {file}: {e}")

    print("✅ All files downloaded and organized.")

if __name__ == "__main__":
    download_ace_files()
