from bot.digest_builder import split_into_messages, format_block
from bot.schemas import DigestBlock


def test_short_text_not_split():
    text = "Короткий текст."
    result = split_into_messages(text)
    assert result == [text]


def test_long_text_is_split_into_multiple_chunks():
    long_text = "а" * 5000
    result = split_into_messages(long_text)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 4000


def test_split_preserves_all_content():
    long_text = "строка\n" * 1000
    result = split_into_messages(long_text)
    joined_back = "".join(result)
    assert joined_back == long_text


def test_format_block_includes_topic_name_and_content():
    block = DigestBlock(topic_name="BTS", content_text="Новый альбом анонсирован.")
    result = format_block(block)
    assert "BTS" in result
    assert "Новый альбом анонсирован." in result