# Project Summary
# CIS4340 HW03

## Overview

This project extracts SpaceX Falcon 9 and Falcon Heavy booster launch data from Wikipedia. The goal is to collect launch records for Block 1, 1.1, 4, and 5 boosters, clean the data, and generate multiple reports based on the extracted dataset.

The final dataset includes one row per launch with the following fields:
engine number, block type, flight number, flight type, launch date, launch pad, landing location, turnaround time, status, and total number of launches.

---

## Selected Scraper

For the regular scraper, I selected **Beautiful Soup** instead of Scrapy.

Beautiful Soup was chosen because:
- The project only requires scraping a single Wikipedia page
- It is easier to debug and control compared to Scrapy
- It allows direct parsing of HTML tables
- It is faster to develop for structured table data

---

## Steps Used for Web Scraping

1. Used the `requests` library to download the Wikipedia page.
2. Added browser headers to avoid a 403 Forbidden error.
3. Parsed the HTML using Beautiful Soup.
4. Identified the relevant tables for Block 1/1.1, Block 4, and Block 5 boosters.
5. Extracted rows from each table and cleaned the text by removing citations and extra whitespace.
6. Handled different table formats:
   - Block 1/1.1 tables have a simpler structure
   - Block 4 tables include turnaround time
   - Block 5 tables include continuation rows for multiple launches
7. Implemented logic to track the current booster and correctly handle continuation rows.
8. Converted all dates into `YYYY-MM-DD` format.
9. Set turnaround time to 0 for Block 1 and 1.1 boosters as allowed.
10. Counted total launches per engine using Python’s `Counter`.
11. Saved the final dataset to `Blocks.csv`.

---

## ScrapeGraphAI Prompts

Prompt 1:
Extract all SpaceX Falcon 9 first-stage booster launch records from the Wikipedia page.

Prompt 2:
Return the following fields for each launch:
engine number, block type, flight number, flight type, launch date (YYYY-MM-DD), launch pad, landing location, turnaround time in days, status, and total number of launches.

Prompt 3:
Ensure that each row represents a single launch, including multiple launches for the same booster, and include Falcon Heavy side boosters and center core data.

---

## Prompt Strategy

The prompt strategy started with a general request for booster data. Then it was refined to:
- specify exact required fields
- enforce one row per launch
- require CSV-style output
- ensure proper formatting of dates and turnaround values

This step-by-step refinement helped improve the accuracy of the extracted data.

---

## Development Tools

The following tools were used:

- Python
- Requests (HTTP requests)
- Beautiful Soup (HTML parsing)
- CSV module (file handling)
- VS Code (development environment)
- PowerShell / Terminal (running scripts)
- GitHub (version control)

---

## Development Plan

The development followed these steps:

1. Build the main scraper (`f9Extract.py`)
2. Debug table parsing and handle continuation rows
3. Generate the cleaned dataset (`Blocks.csv`)
4. Create report programs to filter and analyze the data
5. Generate all required output files
6. Develop AI-based versions of the report scripts
7. Write the project summary

---

## Difficulties and Hurdles

Several challenges were encountered:

- **403 Forbidden error** when accessing Wikipedia, fixed by adding request headers
- **Different table structures** across Block 1, Block 4, and Block 5
- **Continuation rows** in Block 5 tables, requiring tracking of the current booster
- **Missing turnaround data** for Block 1/1.1, handled by setting values to 0
- **Unicode encoding errors** in Windows (GBK), fixed by forcing UTF-8 output
- **PowerShell redirection issues**, caused by accidental extra characters in commands

These issues required debugging and adjusting parsing logic.

---

## Conclusion

This project provided hands-on experience with web scraping, data cleaning, and structured data processing in Python. It also demonstrated the importance of handling inconsistent data formats and debugging real-world issues such as encoding errors and HTML structure variations.

The final result successfully extracts and processes SpaceX booster launch data and generates all required reports.
