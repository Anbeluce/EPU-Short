import bcrypt


def generate_short_code(length: int = 6) -> str:
    import string
    import random
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def validate_custom_code(code: str) -> bool:
    import re
    if not 3 <= len(code) <= 20:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', code))
