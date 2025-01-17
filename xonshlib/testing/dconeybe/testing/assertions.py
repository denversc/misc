import re

def contains_with_non_abutting_text(s: str, substring: str) -> bool:
  pattern = r"(\W|^)" + re.escape(substring) + r"(\W|$)"
  return re.search(pattern, s) is not None
