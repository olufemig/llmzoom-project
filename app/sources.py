from dataclasses import dataclass


@dataclass(frozen=True)
class SourceExcerpt:
    text: str
    section_ref: str
