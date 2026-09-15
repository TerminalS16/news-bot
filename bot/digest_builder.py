from bot.schemas import DigestBlock

TELEGRAM_MAX_MESSAGE_LENGTH = 4000  # запас от официального лимита Telegram в 4096 символов


def format_block(block: DigestBlock) -> str:
    return f"📌 <b>{block.topic_name}</b>\n{block.content_text}"


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