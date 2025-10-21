import hashlib


def analyze_string(value: str):
    if not isinstance(value, str):
        raise TypeError("Value must be a string!")

    # clear whitespaces and convert to lowercase
    cleaned = ''.join(value.lower().split())

    # check for palindrome
    is_palindrome = cleaned == cleaned[::-1]

    # check for the length of input
    length = len(value)

    # check for the length of each word in the input value
    words = value.strip().split()
    word_count = len(words)

    # count the occurrence of each character in  the input value
    freq_map = {}
    for ch in value:
        freq_map[ch] = freq_map.get(ch, 0)+1

    unique_characters = len(freq_map.keys())
    sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": freq_map
    }
