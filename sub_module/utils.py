
import re

def clean_content(html_string: str) -> str:
    """Strips HTML tags and normalizes whitespace for reliable comparison."""
    if not html_string: return ""
    # 1. Strip HTML tags
    text = re.sub(r'<[^>]*>', '', html_string)
    # 2. Normalize whitespace and entities
    text = text.replace('&nbsp;', ' ').strip()
    text = re.sub(r'\s+', ' ', text)
    # 3. Strip common ending punctuation
    text = text.strip('.').strip(',')
    return text
