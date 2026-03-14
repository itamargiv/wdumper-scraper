__all__ = ['WDumperError', 'ScraperError', 'PageError']


class WDumperError(Exception):
    pass


class ScraperError(WDumperError):
    pass


class PageError(WDumperError):
    pass

