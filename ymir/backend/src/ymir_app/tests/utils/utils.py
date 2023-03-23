import random
import string
from typing import Dict


def random_lower_string(k: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))


def random_hash(hash_type: str = "asset") -> str:
    leading = hash_type[0]
    return leading + "0" * 9 + random_lower_string(40)


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_url() -> str:
    return f"https://www.{random_lower_string()}.com/{random_lower_string()}"


def get_normal_token_headers() -> Dict[str, str]:
    headers = {"X-User-Id": "233", "X-User-Role": "1"}
    return headers


def get_admin_token_headers() -> Dict[str, str]:
    headers = {"X-User-Id": "233", "X-User-Role": "2"}
    return headers


def get_super_admin_token_headers() -> Dict[str, str]:
    headers = {"X-User-Id": "233", "X-User-Role": "3"}
    return headers
