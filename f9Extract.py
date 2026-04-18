# f9Extract.py file

import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_Falcon_9_first-stage_boosters"

def fetch_page(url):
    response = requests.get(url)
    return response.text

def main():
    html = fetch_page(URL)
    soup = BeautifulSoup(html, "lxml")

    # Find all tables
    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables")

if __name__ == "__main__":
    main()
