import random, string, hashlib


def generate_short_code(original_url: str, length: int = 6) -> str:
    # based on MD5 algorithm for generating unique short codes
    hash_str = hashlib.md5(original_url.encode()).hexdigest()
    code = hash_str[:length]
    if len(code) < length:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return code
