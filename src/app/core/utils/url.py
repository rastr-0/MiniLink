import secrets, hashlib


def generate_short_code(original_url: str, length: int = 6) -> str:
    salt = secrets.token_hex(4)  # random salt
    hash_str = hashlib.md5((original_url + salt).encode()).hexdigest()
    return hash_str[:length]
