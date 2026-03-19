
import re
import unicodedata

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


def remove_accents(text: str) -> str:
    """
    Remove Vietnamese diacritical marks from text.
    Example: "Nguyễn Hải Đăng" → "Nguyen Hai Dang"
    """
    if not text:
        return text
    
    # Normalize to NFD (decomposed form)
    nfd_text = unicodedata.normalize('NFD', text)
    
    # Remove combining characters (diacritical marks)
    output = ''.join(char for char in nfd_text if unicodedata.category(char) != 'Mn')
    
    return output
