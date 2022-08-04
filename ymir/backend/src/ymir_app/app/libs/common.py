from typing import List, Optional


def pagination(items: List, offset: Optional[int] = 0, limit: Optional[int] = 10) -> List:
    return items[offset : (limit + offset if limit is not None else None)]
