from typing import List, Optional


def pagination(items: List, offset: int = 0, limit: Optional[int] = None) -> List:
    """
    Mimic the behavior of database query's offset-limit pagination
    """
    end = limit + offset if limit is not None else None
    return items[offset:end]
