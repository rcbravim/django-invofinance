import hashlib
import re
from typing import List


def hash_gen(str2hash: str) -> str:
    return hashlib.md5(str2hash.encode()).hexdigest()


def hash_check(hash: str) -> bool:
    return bool(re.findall(r'([a-fA-F\d]{32})', hash))


def paginator(pg: int, pg_total: int) -> List[int]:
    if pg_total > 5:
        if pg > 3:
            pg_init = pg - 2
            if (pg + 1) > pg_total:
                pg_init = pg_init - 2
                pg_end = pg_total
            elif (pg + 2) > pg_total:
                pg_init = pg_init - 1
                pg_end = pg_total
            else:
                pg_init = pg - 2
                pg_end = pg + 2
        else:
            pg_init = 1
            pg_end = 5
    else:
        pg_init = 1
        pg_end = pg_total
    return list(range(pg_init, (pg_end + 1)))
