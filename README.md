# wdumper-scraper

A notebook that scrapes all dump subsets listed under "recent dumps" on [WDumper](https://wdumper.toolforge.org), in order to better understand what kinds of Wikidata entity dump subsets users are interested in.

The notebook generates a CSV file where each row represents a dump and includes the following columns:

- Dump name & URL
- Filter (human-readable, including labels for any items and properties used)
- Statements included in the dump
- Labels, descriptions, aliases, sitelinks (yes/no)
- Languages

## Prerequisites

- Python 3.10+

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/itamargiv/wdumper-scraper.git
   cd wdumper-scraper
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Launch the notebook**
   ```bash
   jupyter notebook notebook.ipynb
   ```

## Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/itamargiv/wdumper-scraper/blob/main/notebook.ipynb)

The notebook includes a setup cell that automatically clones the repository and installs dependencies when run in Colab — no manual setup required.

