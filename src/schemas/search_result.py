from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str
    domain: str
    content: Optional[str] = None
