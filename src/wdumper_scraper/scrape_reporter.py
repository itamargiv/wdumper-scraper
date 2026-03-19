import time
from tqdm.auto import tqdm
from IPython.display import display, Markdown, clear_output
from wdumper_scraper.scrape_result import ScrapeResult

__all__ = ["NullReporter", "ScrapeReporter"]

class NullReporter:
    def scrape_bar(self, futures, total: int, desc: str) -> tqdm:
        return tqdm(futures, total=total, disable=True)

    def countdown(self, seconds: int, attempt: int, max_retries: int) -> None:
        time.sleep(seconds)

    def report(self, result: ScrapeResult) -> None:
        pass

class ScrapeReporter(NullReporter):
    def scrape_bar(self, futures, total: int, desc: str) -> tqdm:
        return tqdm(futures, total=total, desc=desc, leave=True)

    def countdown(self, seconds: int, attempt: int, max_retries: int) -> None:
        countdown = tqdm(range(seconds, 0, -1), bar_format="{desc}", leave=False)
        for remaining in countdown:
            countdown.set_description(f"Retrying in {remaining} seconds... (attempt {attempt}/{max_retries})")
            time.sleep(1)

    def report(self, result: ScrapeResult) -> None:
        error_msgs = [data["error"] for data in result.skipped]
        error_counts = {msg: error_msgs.count(msg) for msg in set(error_msgs)}

        if error_counts:
            table_rows = "\n".join(f"| {msg} | {count} |" for msg, count in error_counts.items())
            errors_md = f"| Error | Count |\n|---|---|\n{table_rows}"
        else:
            errors_md = "_No errors_"

        clear_output(wait=True)
        display(Markdown(f"**Scraped {len(result.dumps)} dumps, skipped {len(result.skipped)} dumps.**\n\n{errors_md}"))
