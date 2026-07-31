from dataclasses import dataclass


@dataclass(frozen=True)
class SourceExcerpt:
    text: str
    source_title: str
    source_url: str
    section_ref: str
