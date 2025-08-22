import re

MARKDOWN_PATTERN = re.compile(
    r"(\*\*.*?\*\*|__.*?__|`.*?`|#+\s|>\s|[-*+]\s|\[.*?\]\(.*?\))"
)

def detect_mime_type(text: str) -> str:
    """
    텍스트가 마크다운 문법을 포함하면 text/markdown,
    아니면 text/plain 반환
    """
    if MARKDOWN_PATTERN.search(text):
        return "text/markdown"
    return "text/plain"