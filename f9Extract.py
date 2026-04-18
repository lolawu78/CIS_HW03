# f9Extract.py file

import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_Falcon_9_first-stage_boosters"

def fetch_page(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text

def main():
    html = fetch_page(URL)
    soup = BeautifulSoup(html, "lxml")

    tables = soup.find_all("table", class_="wikitable")
    print(f"Found {len(tables)} wikitable tables\n")

    for table_index, table in enumerate(tables):
        print(f"=== TABLE {table_index} ===")
        rows = table.find_all("tr")

        for row_index, row in enumerate(rows[:5]):  # only first 5 rows for testing
            cells = row.find_all(["th", "td"])
            values = [cell.get_text(" ", strip=True) for cell in cells]
            print(f"Row {row_index}: {values}")

        print()

if __name__ == "__main__":
    main()
