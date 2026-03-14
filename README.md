# wdumper-scraper

A notebook that scrapes all dump subsets listed under "recent dumps" on [WDumper](https://wdumper.toolforge.org), in order to better understand what kinds of Wikidata entity dump subsets users are interested in.

The notebook generates a CSV file where each row represents a dump and includes the following columns:

- Dump name & URL
- Filter (human-readable, including labels for any items and properties used)
- Statements included in the dump
- Labels, descriptions, aliases, sitelinks (yes/no)
- Languages

## Project Structure

```
wdumper-scraper/
├── src/
│   └── wdumper_scraper/       # Source package
│       ├── __init__.py        # Re-exports all public symbols
│       ├── scraper.py         # Scraper and CacheDuration classes
│       ├── recent_dumps_page.py  # RecentDumpsPage class
│       ├── dump_info_page.py  # DumpInfoPage class
│       ├── dump_info.py       # DumpInfo class
│       └── dumps_info_loader.py  # DumpsInfoLoader and ScrapeResult
├── tests/
│   ├── conftest.py            # Shared pytest fixtures
│   ├── test_scraper.py
│   ├── test_recent_dumps_page.py
│   ├── test_dump_info_page.py
│   ├── test_dump_info.py
│   └── test_dumps_info_loader.py
├── notebook.ipynb             # Main analysis notebook
├── pyproject.toml             # Project metadata, dependencies, and build config
└── pytest.ini                 # Pytest configuration
```

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
   pip install -e ".[dev]"
   ```

4. **Install the git filter to strip notebook outputs before commits**
   ```bash
   nbstripout --install --attributes .gitattributes
   ```

5. **Launch the notebook**
   ```bash
   jupyter notebook notebook.ipynb
   ```

## Testing

```bash
pytest
```

## Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/itamargiv/wdumper-scraper/blob/main/notebook.ipynb)

The notebook includes a setup cell that automatically clones the repository and installs dependencies when run in Colab — no manual setup required.
