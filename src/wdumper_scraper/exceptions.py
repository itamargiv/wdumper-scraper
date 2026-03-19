__all__ = ["WDumperError", "ScraperError", "PageError", "ClientError"]


class WDumperError(Exception):
    pass


class ScraperError(WDumperError):
    pass


class PageError(WDumperError):
    pass


class ClientError(WDumperError):
    pass
