from requests import HTTPError


class HTTPError404(HTTPError):
    ...

class ParsedArticleError(ValueError):
    ...