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
│   └── wdumper_scraper/               # Source package
│       ├── __init__.py                # Re-exports public symbols
│       ├── cached_limiter_session.py  # Rate-limited and cached HTTP session
│       ├── dump_info.py               # DumpInfo class
│       ├── dumps_info_loader.py       # DumpsInfoLoader class
│       ├── exceptions.py              # WDumperError and subclasses
│       ├── recent_dumps_page.py       # RecentDumpsPage class
│       ├── scrape_reporter.py         # ScrapeReporter and NullReporter classes
│       ├── scrape_result.py           # ScrapeResult named tuple
│       ├── scraper.py                 # Scraper and CacheDuration classes
│       ├── wdumper_client.py          # WDumperClient and typed dict types
│       └── wdumper_scraper.py         # WDumperScraper main entry point
├── tests/
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── test_dump_info.py
│   ├── test_dumps_info_loader.py
│   ├── test_recent_dumps_page.py
│   ├── test_scraper.py
│   └── test_wdumper_client.py
├── notebook.ipynb                     # Main analysis notebook
├── pyproject.toml                     # Project metadata, dependencies, and build config
└── pytest.ini                         # Pytest configuration
```

## Prerequisites

- Python 3.10+
- [git-lfs](https://git-lfs.com/)

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/itamargiv/wdumper-scraper.git
   cd wdumper-scraper
   git lfs pull
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

4. **Install the pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Launch the notebook**
   ```bash
   jupyter notebook notebook.ipynb
   ```

## Linting & Type Checking

Check for lint errors and enforce formatting:

```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

Run type checking:

```bash
mypy src/ tests/
```

To auto-fix lint and formatting issues:

```bash
ruff check --fix src/ tests/
ruff format src/ tests/
```

## Testing

```bash
pytest
```

## Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/itamargiv/wdumper-scraper/blob/main/notebook.ipynb)

The notebook includes a setup cell that automatically clones the repository and installs dependencies when run in Colab — no manual setup required.
