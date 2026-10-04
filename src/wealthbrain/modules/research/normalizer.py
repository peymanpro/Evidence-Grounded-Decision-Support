from html.parser import HTMLParser
from re import sub

from wealthbrain.modules.research.contracts import NormalizedSource


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._title_depth = 0
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "template"}:
            self._skip_depth += 1
        if tag.lower() == "title" and self._skip_depth == 0:
            self._title_depth += 1

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "title" and self._title_depth:
            self._title_depth -= 1
        if lowered in {"script", "style", "noscript", "template"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        value = sub(r"\s+", " ", data).strip()
        if not value:
            return
        if self._title_depth:
            self.title_parts.append(value)
        self.text_parts.append(value)


def normalize_source(
    *,
    url: str,
    content: str,
    content_type: str,
    content_sha256: str,
    content_length_bytes: int,
) -> NormalizedSource:
    if content_type == "text/html":
        parser = _TextExtractor()
        parser.feed(content)
        parser.close()
        title = " ".join(parser.title_parts).strip() or url
        text = " ".join(parser.text_parts).strip()
    else:
        title = url
        text = " ".join(content.split())

    return NormalizedSource(
        url=url,
        title=title[:500],
        content=text,
        content_sha256=content_sha256,
        content_length_bytes=content_length_bytes,
    )
