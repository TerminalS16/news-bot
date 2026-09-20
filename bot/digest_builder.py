import html

from bot.schemas import DigestBlock

TELEGRAM_MAX_MESSAGE_LENGTH = 4000


def format_block(block: DigestBlock) -> str:
    safe_topic_name = html.escape(block.topic_name)
    safe_content = html.escape(block.content_text)
    return f"📌 <b>{safe_topic_name}</b>\n{safe_content}"


def split_into_messages(text: str, max_len: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= max_len:
        return [text]

    chunks = []
    while len(text) > max_len:
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:]
    if text:
        chunks.append(text)

    return chunks