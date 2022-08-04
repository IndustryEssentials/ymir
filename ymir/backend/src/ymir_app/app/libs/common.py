from typing import List, Optional


def pagination(items: List, offset: Optional[int], limit: Optional[int]) -> List:
    offset = offset or 0
    limit = limit or 10
    return items[offset : (limit + offset if limit is not None else None)]  # noqa: E203
