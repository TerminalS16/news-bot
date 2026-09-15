from dataclasses import dataclass, field
import hashlib


@dataclass
class Article:
    title: str
    url: str
    content: str
    published_at: str
    content_hash: str = field(init=False)

    def __post_init__(self) -> None:
        raw = f"{self.title}{self.content}".encode("utf-8")
        self.content_hash = hashlib.md5(raw).hexdigest()

@dataclass
class DigestBlock:
    topic_name: str
    content_text: str