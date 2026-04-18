import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter

URL = "https://en.wikipedia.org/wiki/List_of_Falcon_9_first-stage_boosters"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

STATUS_OPTIONS = [
    "Expended",
    "Destroyed",
    "Lost at sea",
    "Returned to service",
    "Retired",
    "Under refurbishment",
    "Inactive",
    "Awaiting assignment",
    "Awaiting Launch",
    "At Port of Long Beach",
    "At Port Canaveral",
    "Never completed",
    "Unknown"
]


def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def clean_text(text):
    text = re.sub(r"\[[^\]]*\]", "", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_date(date_str):
    date_str = clean_text(date_str)

    formats = [
        "%B %d, %Y",
        "%d %B %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return date_str


def is_date_string(text):
    text = clean_text(text)
    patterns = [
        r"^[A-Z][a-z]+ \d{1,2}, \d{4}$",
        r"^\d{1,2} [A-Z][a-z]+ \d{4}$"
    ]
    return any(re.match(p, text) for p in patterns)


def parse_turnaround(text, block_type):
    text = clean_text(text)

    if block_type in {"1", "1.1"}:
        return 0

    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


def extract_pad(text):
    text = clean_text(text)
    match = re.search(r"\((.*?)\)", text)
    return match.group(1).strip() if match else text


def extract_landing(text):
    text = clean_text(text)

    if text.lower() == "no attempt":
        return "No attempt"

    match = re.search(r"\((.*?)\)", text)
    if match:
        return match.group(1).strip()

    return text


def extract_status(text):
    text = clean_text(text)
    for status in STATUS_OPTIONS:
        if text.startswith(status):
            return status
    return text


def block_from_raw(raw):
    raw = clean_text(raw).lower()

    if "1.1" in raw:
        return "1.1"
    if "1.0" in raw or "v1.0" in raw:
        return "1"
    if "ft" in raw or "b4" in raw or "block 4" in raw:
        return "4"
    if "b5" in raw or "block 5" in raw:
        return "5"

    return raw


def valid_flight_number(text):
    text = clean_text(text)
    return text.startswith("F9-") or text.startswith("FH-")


def extract_records(soup):
    tables = soup.find_all("table", class_="wikitable")
    records = []

    for table_index, table in enumerate(tables):
        rows = table.find_all("tr")

        current_engine = None
        current_block = None

        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            values = [clean_text(cell.get_text(" ", strip=True)) for cell in cells]
            if not values:
                continue

            # -------------------------------
            # Table 0: Block 1 / 1.1
            # [engine, version, date, flight_no, payload, launch, landing, status]
            # -------------------------------
            if table_index == 0:
                if len(values) >= 8 and values[0].startswith("B"):
                    engine = values[0]
                    block = block_from_raw(values[1])
                    date = normalize_date(values[2])
                    flight_no = values[3]

                    if not valid_flight_number(flight_no):
                        continue
                    if not is_date_string(values[2]):
                        continue

                    flight_type = "FH" if flight_no.startswith("FH") else "F9"
                    launch_pad = extract_pad(values[5])
                    landing = extract_landing(values[6])
                    turnaround = 0
                    status = extract_status(values[7])

                    records.append([
                        engine,
                        block,
                        flight_no,
                        flight_type,
                        date,
                        launch_pad,
                        landing,
                        turnaround,
                        status
                    ])

            # -------------------------------
            # Table 1: Block 4
            # [engine, type, date, flight_no, turnaround, payload, launch, landing, status]
            # -------------------------------
            elif table_index == 1:
                if len(values) >= 9 and values[0].startswith("B"):
                    engine = values[0]
                    block = block_from_raw(values[1])
                    date = normalize_date(values[2])
                    flight_no = values[3]

                    if not valid_flight_number(flight_no):
                        continue
                    if not is_date_string(values[2]):
                        continue

                    flight_type = "FH" if flight_no.startswith("FH") else "F9"
                    turnaround = parse_turnaround(values[4], block)
                    launch_pad = extract_pad(values[6])
                    landing = extract_landing(values[7])
                    status = extract_status(values[8])

                    records.append([
                        engine,
                        block,
                        flight_no,
                        flight_type,
                        date,
                        launch_pad,
                        landing,
                        turnaround,
                        status
                    ])

            # -------------------------------
            # Tables 2 and 3: Block 5
            # Full row:
            # [engine, role, launches, date, flight_no, turnaround, payload, launch, landing, status]
            #
            # Continuation row:
            # [date, flight_no, turnaround, payload, launch, landing, status]
            # -------------------------------
            elif table_index in (2, 3):
                # Full row
                if len(values) >= 10 and values[0].startswith("B"):
                    current_engine = values[0]
                    current_block = "5"

                    engine = current_engine
                    block = current_block
                    raw_date = values[3]
                    date = normalize_date(raw_date)
                    flight_no = values[4]

                    if not valid_flight_number(flight_no):
                        continue
                    if not is_date_string(raw_date):
                        continue

                    flight_type = "FH" if flight_no.startswith("FH") else "F9"
                    turnaround = parse_turnaround(values[5], block)
                    launch_pad = extract_pad(values[7])
                    landing = extract_landing(values[8])
                    status = extract_status(values[9])

                    records.append([
                        engine,
                        block,
                        flight_no,
                        flight_type,
                        date,
                        launch_pad,
                        landing,
                        turnaround,
                        status
                    ])

                # Continuation row
                elif (
                    current_engine is not None
                    and len(values) >= 7
                    and is_date_string(values[0])
                    and valid_flight_number(values[1])
                ):
                    engine = current_engine
                    block = current_block
                    raw_date = values[0]
                    date = normalize_date(raw_date)
                    flight_no = values[1]
                    flight_type = "FH" if flight_no.startswith("FH") else "F9"
                    turnaround = parse_turnaround(values[2], block)
                    launch_pad = extract_pad(values[4])
                    landing = extract_landing(values[5])
                    status = extract_status(values[6])

                    records.append([
                        engine,
                        block,
                        flight_no,
                        flight_type,
                        date,
                        launch_pad,
                        landing,
                        turnaround,
                        status
                    ])

    return records


def add_launch_counts(records):
    counts = Counter(record[0] for record in records)
    for record in records:
        record.append(counts[record[0]])
    return records


def print_csv(records):
    for record in records:
        print(",".join(str(x) for x in record))


def main():
    html = fetch_page(URL)
    soup = BeautifulSoup(html, "lxml")

    records = extract_records(soup)
    records = add_launch_counts(records)
    print_csv(records)


if __name__ == "__main__":
    main()
