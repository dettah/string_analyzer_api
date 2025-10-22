# analyzer/utils.py
import hashlib
from collections import Counter

def analyze_string(value: str) -> dict:
    length = len(value)
    is_palindrome = value.lower() == value.lower()[::-1]
    unique_characters = len(set(value))  # Case-sensitive distinct characters
    word_count = len(value.split())  # Split on whitespace
    sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
    character_frequency_map = dict(Counter(value))  # Case-sensitive frequency

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map,
    }